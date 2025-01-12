from fastapi import APIRouter, File, UploadFile
import os
from utils.pinecone import extract_insights_from_chatlog, generate_embeddings, store_embeddings_in_pinecone

router = APIRouter()

#file: UploadFile means that the file type will be of type upload file
#File(...) lets Fast API know it will be coming from the requests multipart/form-data body.
@router.post("/process_chatlog")
async def process_chatlog(file: UploadFile = File(...)):
    # Step 1: Save chat log locally
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
    
    return {
        "message": "Chat log processed successfully",
        "items": dict_item_context["items"],
        "context": dict_item_context["context"],
        "messages": dict_item_context["messages"],
    }

