# controllers/nebius.py
import os
from openai import OpenAI
from fastapi import APIRouter, HTTPException
from dotenv import load_dotenv
import json

load_dotenv()

# Initialize the FastAPI router
router = APIRouter()

# Initialize the Nebius API client
client = OpenAI(
  base_url="https://api.studio.nebius.ai/v1/",
  api_key=os.environ.get("NEBIUS_API_KEY")  # Ensure your API key is set in the environment
)
print(client.api_key)

# Route for sending a prompt to the model
@router.post("/nebius-chat")
async def nebius_chat(prompt: str):
  try:
    # Call the Nebius API with the model and prompt
    completion = client.chat.completions.create(
      model="meta-llama/Meta-Llama-3.1-70B-Instruct-fast",
      messages=[{"role": "user", "content": prompt}],
      temperature=0.6,
      max_tokens=512,
      top_p=0.9
    )

    # Return the completion response
    response = json.loads(completion.to_json())
    message_content = response['choices'][0]['message']['content']
    try:
      print(message_content)
    except Exception as e:
      print(e)

    return {"response": response}

  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error calling Nebius API: {str(e)}")
