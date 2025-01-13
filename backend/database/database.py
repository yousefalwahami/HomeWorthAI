import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

def get_connection():
    #tells the connection we want column based dbs returned
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn