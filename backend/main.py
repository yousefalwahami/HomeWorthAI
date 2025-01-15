from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from controllers.detectron2 import router as detectron2_router
from controllers.chatLogProcessing import router as chatlog_upload_router
from controllers.nebius import router as nebius_router
from controllers.upload_backup import router as upload_backup_router
from controllers.authentication import router as authentication_router
from database.database import get_connection
from utils.pinecone_db import clear_index

app = FastAPI()
'''
Access the API documentation at:

Swagger UI: http://127.0.0.1:8000/docs
Redoc UI: http://127.0.0.1:8000/redoc
'''

# Add CORS middleware
origins = [
  "http://localhost:5173", # Vite
  "https://yourfrontenddomain.com",  # Production frontend
]

app.add_middleware(
  CORSMiddleware,
  allow_origins=origins,
  allow_credentials=True,
  allow_methods=["*"],
  allow_headers=["*"],
)

# tag parameter helps group the routes for better documentation in the Swagger UI
app.include_router(detectron2_router, prefix="/api", tags=["detectron2"])
app.include_router(chatlog_upload_router, prefix="/api", tags=["chatlog_upload"])
app.include_router(nebius_router, prefix="/api", tags=["nebius"])
app.include_router(upload_backup_router, prefix="/api", tags=["files"])
app.include_router(authentication_router, prefix="/api", tags=["authentication"])


conn = get_connection()
cursor = conn.cursor()


@app.get("/")
def read_root():
  return {"message": "Hello, World!"}

# clear_index()