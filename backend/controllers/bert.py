from fastapi import APIRouter, HTTPException
from sentence_transformers import SentenceTransformer
from transformers import pipeline

# Initialize the BERT model and pipelines
embedding_model = SentenceTransformer('sentence-transformers/all-MiniLM-L6-v2')  # For sentence embeddings
ner_pipeline = pipeline("ner", model="dbmdz/bert-large-cased-finetuned-conll03-english")  # NER model

# Create the FastAPI router for BERT-related endpoints
router = APIRouter()

@router.post("/generate_embeddings")
async def generate_embeddings(sentences: list[str]):
  """
  Generate embeddings for a list of sentences.
  """
  try:
    embeddings = embedding_model.encode(sentences)
    return {"embeddings": embeddings.tolist()}  # Convert numpy array to list for JSON serialization
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error generating embeddings: {str(e)}")

@router.post("/extract_entities")
async def extract_entities(text: str):
  """
  Extract named entities from a given text.
  """
  try:
    entities = ner_pipeline(text)
    return {"entities": entities}
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error extracting entities: {str(e)}")

@router.post("/process_chatlog_embeddings")
async def process_chatlog_embeddings(chat_log: list[str]):
  """
  Process a chat log to generate embeddings for each message.
  """
  try:
    embeddings = embedding_model.encode(chat_log)
    return {"chat_log": chat_log, "embeddings": embeddings.tolist()}
  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error processing chat log: {str(e)}")

