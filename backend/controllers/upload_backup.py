import os
import zipfile
import sqlite3
import tempfile
from fastapi import APIRouter, File, UploadFile, HTTPException
from typing import List
from datetime import datetime

router = APIRouter()

UPLOAD_DIR = "uploaded_backups"
EXTRACT_DIR = "extracted_files"
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(EXTRACT_DIR, exist_ok=True)


def extract_chat_db_from_backup(backup_path: str) -> str:
  """
  Extract chat.db from an iOS backup file.
  """

  backup_extract_path = os.path.join(EXTRACT_DIR, os.path.basename(backup_path))
  os.makedirs(backup_extract_path, exist_ok=True)  # Ensure the directory exists

  # Create a temporary directory for extraction
  #with tempfile.TemporaryDirectory() as backup_extract_path:
  with zipfile.ZipFile(backup_path, "r") as zip_ref:
    zip_ref.extractall(backup_extract_path)

  # Locate the Manifest.db file
  manifest_db_path = os.path.join(backup_extract_path, "Manifest.db")
  if not os.path.exists(manifest_db_path):
    raise HTTPException(status_code=400, detail="Manifest.db not found in backup.")

  # Connect to Manifest.db to find chat.db
  conn = sqlite3.connect(manifest_db_path)
  cursor = conn.cursor()
  query = """
  SELECT fileID
  FROM Files
  WHERE relativePath LIKE '%Library/Messages/chat.db'
  """
  cursor.execute(query)
  result = cursor.fetchone()
  conn.close()

  if not result:
    raise HTTPException(status_code=400, detail="chat.db not found in backup.")

  # Get the fileID of chat.db and locate it
  file_id = result[0]
  chat_db_path = os.path.join(backup_extract_path, file_id[:2], file_id)

  print(f"Extracted chat.db path: {chat_db_path}")

  if not os.path.exists(chat_db_path):
    raise HTTPException(status_code=400, detail="chat.db file is missing in backup.")

  return chat_db_path


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
        chat.chat_identifier AS chat_id
      FROM
        message
      LEFT JOIN
        handle ON message.handle_id = handle.ROWID
      LEFT JOIN
        chat_message_join ON message.ROWID = chat_message_join.message_id
      LEFT JOIN
        chat ON chat.ROWID = chat_message_join.chat_id
      WHERE
        message.text IS NOT NULL
      ORDER BY
        timestamp DESC
      """

      cursor.execute(query)
      rows = cursor.fetchall()

      messages = [
        {
          "timestamp": datetime.fromtimestamp(row[0]).strftime("%Y-%m-%d %H:%M:%S"),
          "message": row[1],
          "sender": row[2],
          "chat_id": row[3],
        }
        for row in rows
      ]
    return messages

  except sqlite3.Error as e:
    raise HTTPException(status_code=500, detail=f"Database error: {e}")


@router.post("/upload_backup")
async def upload_backup(file: UploadFile = File(...)):
  """
  Endpoint to upload an iOS backup file and return extracted chat logs.
  """
  if not file.filename.endswith(".zip"):
    raise HTTPException(status_code=400, detail="Only .zip backup files are allowed.")

  # Save the uploaded file
  backup_path = os.path.join(UPLOAD_DIR, file.filename)
  with open(backup_path, "wb") as f:
    f.write(await file.read())

  try:
    # Extract chat.db from the backup
    chat_db_path = extract_chat_db_from_backup(backup_path)

    # Extract chat logs from chat.db
    messages = extract_imessages(chat_db_path)
    return {"messages": messages}

  except Exception as e:
    raise HTTPException(status_code=500, detail=f"Error processing backup: {e}")

  finally:
    # Clean up uploaded and extracted files
    if os.path.exists(backup_path):
      os.remove(backup_path)
