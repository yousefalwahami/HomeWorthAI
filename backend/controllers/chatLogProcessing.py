from typing import Dict
from fastapi import APIRouter, Body, File, HTTPException, UploadFile
from utils.pinecone_db import (
    extract_insights_from_chatlog,
    generate_embeddings,
    store_embeddings_in_pinecone,
    generate_query_embedding,
    search_in_pinecone
)
from database.database import get_connection
from datetime import datetime
import re

router = APIRouter()

@router.post("/process_chatlog")
async def process_chatlog(file: UploadFile = File(...), user_id: int = Body(...)):
    # Validate user_id
    if not user_id:
        raise HTTPException(status_code=400, detail="User ID is required.")
    
    # Validate file type
    if not file.content_type.startswith("text/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Please upload a valid text file.")
    
    try:
        # Read and decode the uploaded file
        chatlog_content = await file.read()
        try:
            chatlog_content = chatlog_content.decode('utf-8')
        except UnicodeDecodeError:
            raise HTTPException(status_code=400, detail="Failed to decode the file. Ensure it is UTF-8 encoded.")
        
        # 1) Extract insights (items, messages, context) using your Llama model
        dict_item_context = extract_insights_from_chatlog(chatlog_content)

        # 2) Check if insights were extracted successfully
        if not dict_item_context.get("items"):
            raise HTTPException(status_code=400, detail="No insights extracted from the chat log.")

        # 3) Generate embeddings (if needed for Pinecone)
        embeddings = generate_embeddings(dict_item_context)

        # 4) Save chat log to the database
        chat_id = save_chatlog_to_db(user_id=user_id, chat_title=file.filename)
        if not chat_id:
            raise HTTPException(status_code=500, detail="Error saving chat log to the database.")

        # 5) Save messages
        if dict_item_context.get("messages", []) and chat_id:
            dict_item_context["user_id"] = user_id  # So we can reference user_id later
            dict_item_context = save_message_to_db(dict_item_context, chat_id=chat_id)

            # 6) Store embeddings in Pinecone
            store_embeddings_in_pinecone(
                dict_item_context,
                embeddings,
                chat_id=chat_id,
                file=file.filename,
                user_id=user_id,
                image_id=0,
                type="message"
            )

        # 7) Extract items from dict_item_context and store them in `itineraries` table
        store_items_in_db(dict_item_context, user_id)

        # Return a success response
        return {
            "message": "Chat log processed successfully",
            "items": dict_item_context["items"],
            "context": dict_item_context.get("context", {}),
            "messages": dict_item_context["messages"],
        }

    except Exception as e:
        # Catch and log unexpected errors
        print(f"Error processing chat log: {e}")
        raise HTTPException(status_code=500, detail="An error occurred while processing the chat log.")

def save_chatlog_to_db(user_id, chat_title):
    conn = get_connection()
    cursor = None

    try:
        query = """
            INSERT INTO chat_logs (user_id, chat_title)
            VALUES (%s, %s) RETURNING chat_id
        """
        cursor = conn.cursor()
        cursor.execute(query, (user_id, chat_title))
        chat_id = cursor.fetchone()['chat_id']
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

def save_message_to_db(dict_item_context, chat_id):
    """
    Saves each parsed message to the 'messages' table, then returns the updated dict_item_context.
    We assume `dict_item_context["user_id"]` is set so we know which user these messages belong to.
    """
    conn = None
    cursor = None
    messages = dict_item_context["messages"]

    try:
        conn = get_connection()
        cursor = conn.cursor()

        query = """
            INSERT INTO messages (chat_id, sender, receiver, message, timestamp)
            VALUES (%s, %s, %s, %s, %s) RETURNING message_id
        """

        for message in messages:
            parsed_message = parse_message(message)
            if parsed_message:
                cursor.execute(
                    query,
                    (
                        chat_id,
                        parsed_message["sender"],
                        parsed_message.get("receiver", None),
                        parsed_message["message"],
                        parsed_message["timestamp"],
                    )
                )
                msg_id = cursor.fetchone()["message_id"]
                dict_item_context["ids"].append(msg_id)

        conn.commit()
        print("All messages have been uploaded successfully!")
        return dict_item_context

    except Exception as e:
        print("Error saving messages to DB:", e)
        if conn:
            conn.rollback()
        return dict_item_context

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

def parse_message(message):
    """
    Parse a message string to extract timestamp, sender, and message content.
    Format example:
      "Message: [2023-12-01 09:15:23] John: Message text here"
    """
    try:
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

def store_items_in_db(dict_item_context, user_id):
    """
    Extracts the items from dict_item_context["items"], parses them, and
    stores them in the 'itineraries' table. The item format is assumed to be
    "Item: [Laptop]" or similar, where we extract the content inside brackets.
    """
    conn = None
    cursor = None

    # Example of how dict_item_context["items"] might look:
    # ["Item: [Laptop]", "Item: [Phone]", "Some other text..."]
    all_items = dict_item_context.get("items", [])
    if not all_items:
        return  # No items to store

    try:
        conn = get_connection()
        cursor = conn.cursor()

        insert_itinerary = """
            INSERT INTO itineraries 
            (user_id, item_name, description, quantity, source_references, created_at)
            VALUES (%s, %s, %s, %s, %s, %s)
        """

        for item_entry in all_items:
            # Attempt to parse out the actual item
            # e.g. "Item: [Laptop]" => "Laptop"
            match = re.search(r"Item:\s*\[(.+?)\]", item_entry)
            if match:
                actual_item = match.group(1).strip()
            else:
                # fallback if pattern not matched
                actual_item = item_entry

            # Insert into itineraries
            cursor.execute(
                insert_itinerary,
                (
                    user_id,
                    actual_item,               # item_name
                    "Extracted from chat log", # description
                    1,                         # quantity
                    [{"source": "chat_log"}],  # JSONB or text for references
                    datetime.now(),
                )
            )

        conn.commit()
        print("Items stored successfully in 'itineraries' table.")

    except Exception as e:
        print("Error storing items in DB:", e)
        if conn:
            conn.rollback()

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()

@router.get("/chatlog_from_chatid/{chatid}")
def chatlog_from_chatid(chatid: int):
    """
    Fetches and returns all messages for a given chat_id, 
    ordered by timestamp descending.
    """
    conn = get_connection()
    cursor = None

    try:
        query = """
            SELECT *
            FROM messages
            WHERE chat_id = %s
            ORDER BY timestamp DESC
        """
        cursor = conn.cursor()
        cursor.execute(query, (chatid,))
        result = cursor.fetchall()

        cursor.close()
        conn.close()

        if not result:
            return {"chatlog": []}  # Return empty if no messages found

        return {"chatlog": result}

    except Exception as e:
        print(f"Error fetching all chats of chatid: {chatid}: ", e)
        return None

    finally:
        if cursor:
            cursor.close()
        if conn:
            conn.close()
