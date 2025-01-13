from fastapi import APIRouter, File, UploadFile
import os
from utils.pinecone import extract_insights_from_chatlog, generate_embeddings, store_embeddings_in_pinecone
from database.database import get_connection
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
    
    store_embeddings_in_pinecone(dict_item_context, embeddings, file.filename)

    #Step 6: save data to db
    chat_id = save_chatlog_to_db(
        user_id=1, 
        chat_title=file.filename
    )

    messages = dict_item_context.get("messages", [])

    if messages and chat_id:
        save_message_to_db(messages, chat_id=chat_id)
    
    return {
        "message": "Chat log processed successfully",
        "items": dict_item_context["items"],
        "context": dict_item_context["context"],
        "messages": messages,
    }


def save_chatlog_to_db(user_id, chat_title):
    conn = get_connection()
    cursor = None

    try:
        # Prepare SQL query to insert the chat log and return the chat_id
        query = f"""
            INSERT INTO chat_logs (user_id, chat_title)
            VALUES (%s, %s) RETURNING chat_id
        """
        cursor = conn.cursor()

        # Execute the query
        cursor.execute(query, (user_id, chat_title))
        
        # Retrieve the chat_id
        chat_id = cursor.fetchone()['chat_id']

        # Commit the transaction
        conn.commit()

        return chat_id

    except Exception as e:
        print("Error saving chat log to DB:", e)
        return None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def save_message_to_db(messages, chat_id):
    conn = None
    cursor = None

    try:
        # Get database connection
        conn = get_connection()
        cursor = conn.cursor()

        # Prepare SQL query to insert the message data
        query = """
            INSERT INTO messages (chat_id, sender, receiver, message, timestamp)
            VALUES (%s, %s, %s, %s, %s)
        """

        for message in messages:
            # Attempt to parse the message
            parsed_message = parse_message(message)
            if parsed_message:
                cursor.execute(query, (
                    chat_id,
                    parsed_message["sender"],
                    parsed_message.get("receiver", None),
                    parsed_message["message"],
                    parsed_message["timestamp"]
                ))

        # Commit the transaction
        conn.commit()
        print("All messages have been uploaded successfully!")

    except Exception as e:
        print("Error saving messages to DB:", e)

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def parse_message(message):
    """
    Parse a message string to extract timestamp, sender, and message content.
    Supports the following format:
    "Message: [2023-12-01 09:15:23] John: Message text here"
    """
    try:
        # Pattern for messages with the "Message:" prefix
        pattern = r"^Message: \[([^\]]+)\]\s+(\w+):\s*(.+)$"
        match = re.match(pattern, message)
        if match:
            timestamp, sender, message_text = match.groups()
            return {
                "timestamp": timestamp,
                "sender": sender,
                "message": message_text.strip()
            }

    except Exception as e:
        print(f"Error parsing message: {message}, Error: {e}")

    return None

