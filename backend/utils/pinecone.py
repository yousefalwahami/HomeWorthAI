import json
from openai import OpenAI
from sentence_transformers import SentenceTransformer
import torch
from transformers import CLIPModel, CLIPProcessor
import os
from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

# Initialize Nebius OpenAI client
client = OpenAI(
    base_url="https://api.studio.nebius.ai/v1/",
    api_key=os.environ.get("NEBIUS_API_KEY")
)

# model = SentenceTransformer('all-MiniLM-L6-v2')  # You can replace this with another model if needed

# Initialize CLIP for text embeddings
clip_model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
clip_processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")


# Initialize Pinecone
pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))

# Define index name
index_name = "item-context-embeddings-512"

# Create the index if it doesn't exist
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        # dimension=384,  # Embedding dimension for 'all-MiniLM-L6-v2'
        dimension=512,  # Embedding dimension for 'CLIP ViT b3'
        spec=ServerlessSpec(
            cloud="aws",  # Specify your cloud provider
            region="us-east-1"  # Specify your region
        ),
        metric="cosine"  # You can use 'cosine', 'euclidean', or 'dotproduct'
    )

# Connect to the index
index = pc.Index(index_name)

# Query the index to check the inserted vectors
result = index.describe_index_stats()

def extract_insights_from_chatlog(chatlog_content):
    # Use Llama-3.3-70B-Instruct to extract entities and context
    completion = client.chat.completions.create(
        model="meta-llama/Meta-Llama-3.1-8B-Instruct-fast",
        # change model to CLIP
        messages=[
            {
                "role": "system",
                "content": "You are an assistant that extracts key items, their locations, and the message(including timestamp) they come from in chat logs."
            },
            {
                "role": "user",
                "content": f"Extract key items, contexts, and messages from this chat log:\n{chatlog_content}\n\nFormat as:\n* Item: [item]\n* Context: [context]\n* Message: [Original Message]"
            }
        ],
        temperature=0
    )
    
    # Parse the response
    response = json.loads(completion.to_json())
    content = response['choices'][0]['message']['content'].split('*')

    items = []
    context = []
    messages = []

    for i in range(1, len(content) - 2, 3):
        items.append(content[i].strip())
        context.append(content[i+1].strip())
        messages.append(content[i+2].strip())
    
    dict_item_context = {
        "ids": [],
        "items": items,
        "context": context,
        "messages": messages
    }

    return dict_item_context

def generate_embeddings(dict_item_context):
    """
    Generates embeddings for a list of insights using SentenceTransformer.

    Args:
        insights (list of str): The extracted insights or key phrases.

    Returns:
        list of numpy.ndarray: Embeddings for each insight.
    """
    # Prepare text input for CLIP (item + context)
    texts = [item + ' ' + context for item, context in zip(dict_item_context["items"], dict_item_context["context"])]
    
    # Process the text using CLIPProcessor
    inputs = clip_processor(text=texts, return_tensors="pt", padding=True, truncation=True)
    
    # Generate text embeddings using CLIPModel
    with torch.no_grad():
        text_embeddings = clip_model.get_text_features(**inputs)

    return text_embeddings
    # embeddings = model.encode([item + ' ' + context for (item, context) in zip(dict_item_context["items"], dict_item_context["context"])], convert_to_tensor=False)  # Set convert_to_tensor=False to return NumPy arrays
    # return embeddings

def store_embeddings_in_pinecone(dict_item_context, embeddings, chat_id, file):
    """
    Stores embeddings in Pinecone with metadata.

    Args:
        dict_item_context (dict): Dictionary containing "items" and "context".
        embeddings (list): List of embeddings corresponding to each item-context pair.
        filename (str): Name of the uploaded file (used as a unique identifier).
    """
    pinecone_data = [
        {
            "id": file + '_' + str(dict_item_context["ids"][i]),
            "values": embedding.tolist(),  # Convert NumPy array to list
            "metadata": {
                "chat_id": chat_id,
                "message_id": dict_item_context["ids"][i],
                "item": dict_item_context["items"][i],
                "context": dict_item_context["context"][i],
                "message": dict_item_context["messages"][i]
            }
        }
        for i, embedding in enumerate(embeddings)
    ]

    # Upsert data into Pinecone
    try:
        index.upsert(vectors=pinecone_data)
    except Exception as e:
        print(f"Error upserting data to Pinecone: {e}")
        raise
