import os
import traceback
from fastapi.responses import FileResponse
from openai import OpenAI
from fastapi import APIRouter, File, Form, HTTPException, UploadFile
from dotenv import load_dotenv
from fpdf import FPDF
import json
from database.database import get_connection
from utils.pinecone_db import generate_query_embedding, search_in_pinecone
from .chatLogProcessing import chatlog_from_chatid

load_dotenv()

# Initialize the FastAPI router
router = APIRouter()

# Initialize the Nebius API client
client = OpenAI(
  base_url="https://api.studio.nebius.ai/v1/",
  api_key=os.environ.get("NEBIUS_API_KEY")  # Ensure your API key is set in the environment
)

@router.post("/nebius-chat")
async def nebius_chat(data: dict):
  prompt = data.get('prompt')
  user_id = data.get('user_id')
  message_from_frontend = data.get('messages')
  searchChat = data.get('searchChat')
  searchImage = data.get('searchImage')

  if not prompt:
    raise HTTPException(status_code=400, detail="Prompt cannot be empty.")
  try:
    key_item = extract_key_item_from_prompt(prompt)
    key_item_embedding = generate_query_embedding(key_item)
    

    # only being used in final_response
    pc_chat_response = None
    pc_image_response = None
    if(searchChat):
      pc_chat_response = search_in_pinecone(key_item_embedding, user_id, "message", 3)

    if(searchImage):
      pc_image_response = search_in_pinecone(key_item_embedding, user_id, "image", 2)
    
    print(pc_image_response)
    print(pc_chat_response)
  
    formatted_messages = [
      {"role": "user" if msg["sender"] == "user" else "assistant", "content": msg["text"]}
      for msg in message_from_frontend 
    ]
    
    formatted_messages = formatted_messages[-5:] if len(formatted_messages) > 5 else formatted_messages

    completion = None

    if(pc_chat_response and pc_image_response):
      completion = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct",
        messages = [{
            "role": "system",
            "content": '''Your goal is to act as an AI chat bot to help people who have lost there home remember items lost in there home. 
            We may or may not provide you with information. If the user is vague try to help them jog there memory. 
            If you receive items such as chat logs or images let the user know. ENSURE TO ACT AS IF YOU ARE TALKING TO SOMEONE SO HAVE SOME BREVITY AT TIMES.'''

            # make sure to make it talk like an ai aswell -> if i say hello it should talk to me normally like an assistant
          },
          *formatted_messages,
          {
            "role": "user",
            "content": f'''Here are some related messages and detected items in the images related to the user message. Ensure to let the user know about this:
            {', '.join(["image" + str(i) + " items: " + str(pc_image_response[i]['items']) for i in range(len(pc_image_response))])}
            Messages: {', '.join(["Found " + str(pc_chat_response[i]['item']) + " in " + str(pc_chat_response[i]['message']) for i in range(len(pc_chat_response))])},
            User message: {prompt}'''
          }
        ],
        temperature=0.6,
        max_tokens=512,
        top_p=0.9
      )
    elif pc_chat_response:
      completion = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct",
        messages = [{
            "role": "system",
            "content": '''Your goal is to act as an AI chat bot to help people who have lost there home remember items lost in there home. 
            We may or may not provide you with information. If the user is vague try to help them jog there memory. 
            If you receive items such as chat logs or images let the user know. ENSURE TO ACT AS IF YOU ARE TALKING TO SOMEONE SO HAVE SOME BREVITY AT TIMES.'''

            # make sure to make it talk like an ai aswell -> if i say hello it should talk to me normally like an assistant
          },
          *formatted_messages,
          {
            "role": "user",
            "content": f'''Here are some related messages to the user query, ENSURE TO LET THE USER KNOW ABOUT THE FOUND MESSAGE it will be visible to them in the UI just need to bring it up in conversation. ENSURE YOU RESPOND AS IF YOU ARE STILL TALKING: 
            messages: {["Found " + pc_chat_response[i]['item'] + "in " + pc_chat_response[i]['message'] for i in range(len(pc_chat_response))]}, 
            user message: {prompt}'''
          }
        ],
        temperature=0.6,
        max_tokens=512,
        top_p=0.9
      )
    elif pc_image_response:
      completion = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct",
        messages = [{
            "role": "system",
            "content": '''Your goal is to act as an AI chat bot to help people who have lost there home remember items lost in there home. 
            We may or may not provide you with information. If the user is vague try to help them jog there memory. 
            If you receive items such as chat logs or images let the user know. ENSURE TO ACT AS IF YOU ARE TALKING TO SOMEONE SO HAVE SOME BREVITY AT TIMES.'''

            # make sure to make it talk like an ai aswell -> if i say hello it should talk to me normally like an assistant
          },
          *formatted_messages,
          {
            "role": "user",
            "content": f'''Here are some items found in images that are related to the user query, ENSURE TO LET THE USER KNOW ABOUT THE FOUND IMAGES it will be visible to them in the UI you just need to bring it up in conversation. ENSURE YOU RESPOND AS IF YOU ARE STILL TALKING TO THEM: 
            {['image' + str(i) + "items found: " + pc_image_response[i]['items'] for i in range(len(pc_image_response))]},
            user message: {prompt}'''
          }
        ],
        temperature=0.6,
        max_tokens=512,
        top_p=0.9
      )
    else:
      completion = client.chat.completions.create(
        model="meta-llama/Llama-3.3-70B-Instruct",
        messages = [{
            "role": "system",
            "content": '''Your goal is to act as an AI chat bot to help people who have lost there home remember items lost in there home. 
            We may or may not provide you with information. If the user is vague try to help them jog there memory. 
            If you receive items such as chat logs or images let the user know. ENSURE TO ACT AS IF YOU ARE TALKING TO SOMEONE SO HAVE SOME BREVITY AT TIMES.'''

            # make sure to make it talk like an ai aswell -> if i say hello it should talk to me normally like an assistant
          },
          *formatted_messages,
          {
            "role": "user",
            "content": f'''
            No messages or images searched JUST RESPOND TO USER PROMPT,
            user message: {prompt}'''
          }
        ],
        temperature=0.6,
        max_tokens=512,
        top_p=0.9
      )

    # Return the completion response
    response = json.loads(completion.to_json())

    final_response = {
      "response": response,
      "pc_chat_response": pc_chat_response,
      "pc_image_response": pc_image_response
    }

    # return {"response": response}
    return final_response
    

  except Exception as e:
    print(e)
    raise HTTPException(status_code=500, detail=f"Error calling Nebius API: {str(e)}")


def extract_key_item_from_prompt(prompt: str):
  completion = client.chat.completions.create(
    model="meta-llama/Meta-Llama-3.1-8B-Instruct-fast",
    messages=[
      {
        "role": "system",
        "content": '''You are an assistant that extracts a specific key item and context of what 
        the user is looking for filling insurance claims.
        '''
      },
      {
        "role": "user",
        "content": f"Extract a key item of what I'm looking for from my prompt:\n{prompt}\n\nFormat as:\n* Item: [item] Context: [context]. "
        # if you believe there is no query, return no query
        # if its a generic query, make up query "like I need to find some items"
      }
    ],
    temperature=0
  )
  
  response = json.loads(completion.to_json())
  key_item = response['choices'][0]['message']['content'].split('*')

  return key_item[1] if len(key_item) > 1 else key_item[0]


class PDF(FPDF):
    def write_with_formatting(self, text):
        """Custom method to handle basic Markdown-like formatting."""
        lines = text.split("\n")
        for line in lines:
            # Handle headings (###)
            if line.startswith("###"):
                self.set_font("Arial", "B", 14)  # Bold, larger font for headings
                self.cell(0, 10, line.strip("#").strip(), ln=True)
                self.ln(2)  # Add space after heading

            # Handle bold text (e.g., **bold**)
            elif line.startswith("**") and line.endswith("**"):
                self.set_font("Arial", "B", 12)
                self.multi_cell(0, 10, line.strip("**"))
                self.set_font("Arial", "", 12)

            # Handle bullet points (e.g., * Item)
            elif line.startswith("* "):
                self.cell(10)  # Indent bullet points
                self.multi_cell(0, 10, line.strip("* ").strip())

            # Handle normal text
            else:
                self.multi_cell(0, 10, line)
                self.ln(2)  # Add space between paragraphs


@router.get("/generate_report")
def generate_report(user_id: int):
    # Validate user_id
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID is required.")

    conn = get_connection()
    cursor = None

    try:
        # Fetch all items from images for the given user_id
        query = """
            SELECT items
            FROM images
            WHERE user_id = %s
        """
        cursor = conn.cursor()
        cursor.execute(query, (user_id,))
        rows = cursor.fetchall()

        if not rows:
            raise HTTPException(status_code=404, detail="No items found for this user.")

        # Flatten and parse items
        item_list = []
        for row in rows:
            if row['items']:  # Ensure items is not NULL
                item_list.extend(row['items'].split(","))

        # Remove duplicates and sort the list
        unique_items = sorted(set(item.strip() for item in item_list if item.strip()))

        # Generate text for the report using Llama3.3
        report_text = generate_report_text(unique_items)

        # Generate the PDF report
        pdf_path = create_pdf_report(user_id, report_text)

        return FileResponse(pdf_path, media_type='application/pdf', filename=f"user_{user_id}_report.pdf")

    except Exception as e:
        print(f"Error generating report for user_id {user_id}: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while generating the report.")

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()


def generate_report_text(items: list) -> str:
    """Generate well-formatted report text using Llama3.3."""
    prompt = f"""
    Generate a detailed, well-structured, and user-friendly PDF report text listing the following items. 
    Ensure the report is formatted with sections, bullet points, and a summary:
    
    Items: {', '.join(items)}
    
    Format it professionally and include a brief introduction and conclusion.
    """
    
    try:
        completion = client.chat.completions.create(
            model="meta-llama/Llama-3.3-70B-Instruct",
            messages=[
                {
                    "role": "system",
                    "content": "You are a report generator tasked with creating well-structured and professional PDF report text."
                },
                {
                    "role": "user",
                    "content": f'''you need to make a report that will be placed in a pdf file. Have all formatting needed
                    it will contain items found from images the user uploaded. This is to help file insurance claims and jog user memory
                    PLEASE DO IT CORRECTLY HERE ARE THE ITEMS: {prompt}
                    '''
                }
            ],
            temperature=0.5,
            max_tokens=1024,
            top_p=0.9
        )

        response = json.loads(completion.to_json())
        return response['choices'][0]['message']['content']

    except Exception as e:
        print(f"Error generating report text: {e}")
        raise HTTPException(status_code=500, detail="Error generating report text.")


def create_pdf_report(user_id: int, report_text: str) -> str:
    """Generate a PDF report from the LLM-generated text."""
    # Ensure the reports directory exists
    os.makedirs("reports", exist_ok=True)

    pdf = PDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    # Use the custom formatting method to handle the report text
    pdf.write_with_formatting(report_text)

    pdf_path = f"reports/user_{user_id}_report.pdf"
    pdf.output(pdf_path)
    return pdf_path

