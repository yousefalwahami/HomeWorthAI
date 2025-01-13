from fastapi import APIRouter, File, UploadFile
import os
from utils.pinecone import extract_insights_from_chatlog, generate_embeddings, store_embeddings_in_pinecone
from database.database import get_connection
from psycopg2 import sql
from datetime import datetime
import re

router = APIRouter()

#file: UploadFile means that the file type will be of type upload file
#File(...) lets Fast API know it will be coming from the requests multipart/form-data body.
@router.post("/process_chatlog")
async def process_chatlog(file: UploadFile = File(...)):
    # Step 1: Save chat log locally
    # TODO: not save chat logs locally.. 
    file_path = f"chatlogs/{file.filename}"
    os.makedirs("chatlogs", exist_ok=True)
    with open(file_path, "wb") as f:
        f.write(await file.read())
    
    # Step 2: Read chat log content
    with open(file_path, "r") as fi:
        chatlog_content = fi.read()
    
    # Step 3: Extract insights using Llama
    dict_item_context = extract_insights_from_chatlog(chatlog_content)
    
    # Step 4: Generate embeddings
    embeddings = generate_embeddings(dict_item_context)
    
    # Step 5: Store embeddings in Pinecone
    store_embeddings_in_pinecone(dict_item_context, embeddings, file.filename)

    #Step 6: save data to db
    '''
    save_chatlog_to_db(
        chat_id=1 # Replace with dynamic chat ID
        user_id=1,  # Replace with dynamic user ID if needed
        chat_title=file.filename,
        created_at=datetime.now()
    )
    '''
    messages = dict_item_context.get("messages", [])
    '''
    # TODO: test
    if messages:  # Ensure there are messages to save
        save_message_to_db(messages)
    '''
    
    return {
        "message": "Chat log processed successfully",
        "items": dict_item_context["items"],
        "context": dict_item_context["context"],
        "messages": messages,
    }


def save_chatlog_to_db(chat_id, user_id, chat_title, created_at):
  try:
    # Get database connection
    conn = get_connection()
    cursor = conn.cursor()

    # Prepare SQL query to insert the image data
    query = sql.SQL("""
        INSERT INTO messages (message_id, chat_id, sender, receiver, message, timestamp)
        /* INSERT INTO messages (user_id, filename, items, chatlog_content, uploaded_at) */
        VALUES (%s, %s, %s, %s, %s, %s)
    """)    

    # Execute the query with the parameters
    cursor.execute(query, (chat_id, user_id, chat_title, datetime.now()))

    # Commit the transaction
    conn.commit()

    # Close the cursor and connection
    cursor.close()
    conn.close()

    # print(f"Message '{message_id}' uploaded successfully!")

  except Exception as e:
    print("Error saving image to DB:", e)

def save_message_to_db(messages):
    try:
        # Get database connection
        conn = get_connection()
        cursor = conn.cursor()

        # Prepare SQL query to insert the message data
        query = sql.SQL("""
            INSERT INTO messages (message_id, chat_id, sender, receiver, message, timestamp)
            VALUES (%s, %s, %s, %s, %s, %s)
        """)

        for index, message in enumerate(messages):
            # Parse message details
            parsed_message = parse_message(message)
            if parsed_message:
                message_id = index + 1  # Use the index as a unique ID
                chat_id = parsed_message.get("chat_id", "unknown_chat")
                sender = parsed_message["sender"]
                receiver = parsed_message.get("receiver", "unknown_receiver")
                message_text = parsed_message["message"]
                timestamp = parsed_message["timestamp"]

                # Execute the query with the parameters
                cursor.execute(query, (message_id, chat_id, sender, receiver, message_text, timestamp))

        # Commit the transaction
        conn.commit()

        # Close the cursor and connection
        cursor.close()
        conn.close()

        print(f"All messages have been uploaded successfully!")

    except Exception as e:
        print("Error saving messages to DB:", e)

def parse_message(message):
    """
    Parse a message string to extract timestamp, sender, and message content.
    Example input:
    "Message: [2023-12-01 09:15:23] John: Hey, did you grab my laptop from the living room?"
    """
    try:
        pattern = r"^\[([^\]]+)\] (\w+): (.+)$"
        match = re.search(pattern, message.split("Message: ")[-1])
        if match:
            timestamp, sender, message_text = match.groups()
            return {
                "timestamp": timestamp,
                "sender": sender,
                "message": message_text.strip(),
                "chat_id": "default_chat",  # Placeholder, update if chat_id is available
                "receiver": None  # Placeholder, update if receiver info is available
            }
    except Exception as e:
        print(f"Error parsing message: {message}, Error: {e}")
    return None
