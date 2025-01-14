import os
from openai import OpenAI
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from dotenv import load_dotenv
import json
from utils.pinecone import generate_query_embedding, search_in_pinecone

load_dotenv()

# Initialize the FastAPI router
router = APIRouter()

# Initialize the Nebius API client
client = OpenAI(
  base_url="https://api.studio.nebius.ai/v1/",
  api_key=os.environ.get("NEBIUS_API_KEY")  # Ensure your API key is set in the environment
)

# Route for sending a prompt to the model
@router.post("/nebius-chat")
#async def nebius_chat(prompt: str = Form(...), file: UploadFile = File(None), user_id: str = Form(...)):
async def nebius_chat(data: dict):
  prompt = data.get('prompt')
  if not prompt:
    raise HTTPException(status_code=400, detail="Prompt cannot be empty.")
  try:
    # Key item from user
    key_item = extract_key_item_from_prompt(prompt)

    # Using key item, get info from vector db
    key_item_embedding = generate_query_embedding(key_item)
    pc_response = search_in_pinecone(key_item_embedding)

    # Call the Nebius API with the model and prompt
    completion = client.chat.completions.create(
      model="meta-llama/Meta-Llama-3.1-70B-Instruct-fast",
      # messages=[{"role": "user", "content": prompt}],
      messages = [{
          "role": "system",
          "content": "You are to recieve metadata about something that the user is looking for."
        },
        {
          "role": "user",
          "content": f"Using this metadata, give me a proper response explaining where I can find {key_item} using this:\n{pc_response}"
        }
      ],
      temperature=0.6,
      max_tokens=512,
      top_p=0.9
    )

    # Return the completion response
    response = json.loads(completion.to_json())
    message_content = response['choices'][0]['message']['content']
    '''
    try:
      print(message_content)
    except Exception as e:
      print(e)
    '''

    return {"response": response}

  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error calling Nebius API: {str(e)}")

@router.post("/prompt-chat")
def extract_key_item_from_prompt(prompt: str):
  completion = client.chat.completions.create(
    model="meta-llama/Meta-Llama-3.1-8B-Instruct-fast",
    messages=[
      {
        "role": "system",
        "content": "You are an assistant that extracts a specific key item of what the user is looking for."
      },
      {
        "role": "user",
        "content": f"Extract a key item of what I'm looking for from my prompt :\n{prompt}\n\nFormat as:\n* Item: [item]"
      }
    ],
    temperature=0
  )
  
  # Parse the response
  response = json.loads(completion.to_json())
  key_item = response['choices'][0]['message']['content'].split('*')
  print(response)
  print('Key Item Found: ', key_item)

  '''
  key_item_embedding = generate_query_embedding(key_item)
  pc_response = search_in_pinecone(key_item_embedding)
  print('pinecone response: ', pc_response)
  '''

  return key_item
