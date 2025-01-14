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
  user_id = data.get('user_id')
  message_from_frontend = data.get('messages')
  print(*message_from_frontend[-3:])

  if not prompt:
    raise HTTPException(status_code=400, detail="Prompt cannot be empty.")
  try:
    # Key item from user
    key_item = extract_key_item_from_prompt(prompt)

    # Using key item, get info from vector db
    key_item_embedding = generate_query_embedding(key_item)

    pc_response = search_in_pinecone(key_item_embedding, user_id, "message")

    print(pc_response)

    # Call the Nebius API with the model and prompt
    completion = client.chat.completions.create(
      model="meta-llama/Llama-3.3-70B-Instruct",
      # messages=[{"role": "user", "content": prompt}],
      messages = [{
          "role": "system",
          "content": '''Your goal is to act as an AI chat bot to help people who have lost there home file insurance claims. 
          We may or may not provide you with information. If the user is vague try to help them jog there memory. 
          If you receive items such as chat logs or images let the user know. ENSURE TO ACT AS IF YOU ARE TALKING TO SOMEONE SO HAVE SOME BREVITY AT TIMES.'''

          # make sure to make it talk like an ai aswell -> if i say hello it should talk to me normally like an assistant
        },
        *message_from_frontend[-3:]
      ],
      temperature=0.6,
      max_tokens=512,
      top_p=0.9
    )

    # Return the completion response
    response = json.loads(completion.to_json())

    return {"response": response}

  except Exception as e:
    print(e)
    raise HTTPException(status_code=500, detail=f"Error calling Nebius API: {str(e)}")


# @router.post("/prompt-chat")
def extract_key_item_from_prompt(prompt: str):
  completion = client.chat.completions.create(
    model="meta-llama/Meta-Llama-3.1-8B-Instruct-fast",
    messages=[
      {
        "role": "system",
        "content": "You are an assistant that extracts a specific key item and context of what the user is looking for filling insurance claims."
      },
      {
        "role": "user",
        "content": f"Extract a key item of what I'm looking for from my prompt :\n{prompt}\n\nFormat as:\n* Item: [item] Context: [context]."
        # if you believe there is no query, return no query
        # if its a generic query, make up query "like I need to find some items"
      }
    ],
    temperature=0
  )
  
  # Parse the response
  response = json.loads(completion.to_json())
  key_item = response['choices'][0]['message']['content'].split('*')

  return key_item[1]
