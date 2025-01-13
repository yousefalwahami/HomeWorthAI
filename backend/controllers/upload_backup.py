import os
import zipfile
import sqlite3
import io
from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import List
from datetime import datetime

router = APIRouter()

UPLOAD_DIR = "uploaded_backups"
EXTRACT_DIR = "extracted_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(EXTRACT_DIR, exist_ok=True)


async def extract_chat_db_from_backup(file: UploadFile) -> str:
  """
  Extract chat.db from an iOS backup file without saving it to disk.
  """

  # Read the file into memory
  zip_file = zipfile.ZipFile(io.BytesIO(await file.read()), "r")
  
  # List all files in the zip
  zip_files = zip_file.infolist()

  # Find Manifest.db and chat.db files inside the zip
  manifest_db_path = None
  chat_db_path = None

  for zip_file_info in zip_files:
    if 'Manifest.db' in zip_file_info.filename:
      manifest_db_path = zip_file_info.filename
    elif 'Library/Messages/chat.db' in zip_file_info.filename:
      chat_db_path = zip_file_info.filename

  if not manifest_db_path or not chat_db_path:
    raise HTTPException(status_code=400, detail="Required files not found in backup.")

  # Extract only the needed files (Manifest.db and chat.db)
  manifest_db_file = zip_file.read(manifest_db_path)
  chat_db_file = zip_file.read(chat_db_path)

  # Now, we have Manifest.db and chat.db files as in-memory bytes
  # Create a temporary directory to store them for processing
  backup_extract_path = os.path.join(EXTRACT_DIR, "temp_extracted")
  os.makedirs(backup_extract_path, exist_ok=True)

  # Save files to temporary directory
  with open(os.path.join(backup_extract_path, "Manifest.db"), "wb") as f:
    f.write(manifest_db_file)

  with open(os.path.join(backup_extract_path, "chat.db"), "wb") as f:
    f.write(chat_db_file)

  # Return the path of chat.db to extract chat logs
  extracted_chat_db = os.path.join(backup_extract_path, "chat.db")
  return extracted_chat_db


def extract_imessages(db_path: str) -> List[dict]:
  """
  Extract chat logs from the given chat.db file.
  """
  try:
    with sqlite3.connect(db_path) as conn:
      cursor = conn.cursor()

      # SQL query to fetch message data
      query = """
      SELECT 
        message.date / 1000000000 + 978307200 AS timestamp,
        message.text AS message_text,
        handle.id AS sender,
        handle.display_name AS sender_name,
        /* attachment.filename AS attachment_filename,
        attachment.mime_type AS attachment_type */
        chat.chat_identifier AS chat_id,
        chat.display_name AS chat_name
      FROM
        message
      LEFT JOIN
        handle ON message.handle_id = handle.ROWID
      LEFT JOIN
        chat_message_join ON message.ROWID = chat_message_join.message_id
      LEFT JOIN
        chat ON chat.ROWID = chat_message_join.chat_id
      /* LEFT JOIN
        attachment ON attachment.message_id = message.ROWID
        */
      WHERE
        message.text IS NOT NULL
        /* attachment.filename IS NOT NULL */
      ORDER BY
        timestamp DESC
      """

      cursor.execute(query)
      rows = cursor.fetchall()

      messages = [
        {
          "timestamp": datetime.fromtimestamp(row[0]).strftime("%Y-%m-%d %H:%M:%S"),
          "message": row[1],
          "sender": row[4] if row[4] else row[2],  # If sender has a name, use it, otherwise fallback to ID
          "chat_name": row[5] if row[5] else row[3],  # If chat has a name, use it, otherwise fallback to ID
        }
        for row in rows
      ]
    return messages
    # return { "Done processing all messages" }

  except sqlite3.Error as e:
    raise HTTPException(status_code=500, detail=f"Database error: {e}")


@router.post("/upload_backup")
async def upload_backup(file: UploadFile = File(...)):
  """
  Endpoint to upload an iOS backup file and return extracted chat logs.
  """
  if not file.filename.endswith(".zip"):
    raise HTTPException(status_code=400, detail="Only .zip backup files are allowed.")

  '''
  # Save the uploaded file
  backup_path = os.path.join(UPLOAD_DIR, file.filename)
  with open(backup_path, "wb") as f:
    f.write(await file.read())
  '''

  try:
    # Extract chat.db from the backup
    # chat_db_path = extract_chat_db_from_backup(backup_path)
    chat_db_path = await extract_chat_db_from_backup(file)

    # Extract chat logs from chat.db
    messages = extract_imessages(chat_db_path)
    return {"messages": messages}

  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error processing backup: {e}")

  finally:
    # Clean up uploaded and extracted files
    #if os.path.exists(backup_path):
      #os.remove(backup_path)

    # Clean up extracted files (if necessary, in-memory cleanup can be added here)
    pass
