from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Union
from passlib.hash import bcrypt
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from fastapi.responses import JSONResponse
import os
from dotenv import load_dotenv
from database.database import get_connection

load_dotenv()

# Constants for JWT
SECRET_KEY = os.getenv("SECRET_KEY", "default_secret_key")
'''
import secrets
print(secrets.token_hex(32)) #set SECRET_KEY in .env = to this
'''
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Database connection
conn = get_connection()

# Mock database
users_db = {
  "m@example.com": {
    "password": bcrypt.hash("securepassword")  # Store hashed passwords
  }
}

# Models
class LoginInput(BaseModel):
  email: str
  password: str

class Token(BaseModel):
  user_id: int
  email: str
  token: str
  expires_at: str

router = APIRouter()

def verify_password(plain_password: str, hashed_password: str) -> bool:
  return bcrypt.verify(plain_password, hashed_password)

def create_access_token(email: str):
  expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
  to_encode = {"sub": email, "exp": expire}
  return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

@router.post("/user/login", response_model=Token)
async def login(login_input: LoginInput):
  """
  Authenticate the user and return a JWT token.

  Args:
    login_input (LoginInput): The email and password for login.

  Returns:
    Token: A response containing the email, JWT token, and expiry.
  """
  with conn.cursor() as cursor:
    # Query the database for the user
    cursor.execute("SELECT password_hash FROM users WHERE email = %s;", (login_input.email,))
    user = cursor.fetchone()
    
    cursor.execute("SELECT user_id FROM users WHERE email = %s;", (login_input.email,))
    user_id_result = cursor.fetchone()

  if not user or not verify_password(login_input.password, user["password_hash"]):
    raise HTTPException(status_code=401, detail="Invalid email or password")

  token = create_access_token(email=login_input.email)
  expires_at = (datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).isoformat()

  return {"user_id": user_id_result['user_id'], "email": login_input.email, "token": token, "expires_at": expires_at}



# Function to add a user
def add_user(username: str, email: str, password: str):
  """
  Add a user to the database with a hashed password.

  Args:
    username (str): The user's username.
    email (str): The user's email.
    password (str): The user's plaintext password.
  """
  # Hash the password
  password_hash = bcrypt.hash(password)

  with conn.cursor() as cursor:
    try:
      cursor.execute("""
      INSERT INTO users (username, email, password_hash)
      VALUES (%s, %s, %s);
      """, (username, email, password_hash))
      conn.commit()
      print("User added successfully!")
    except Exception as e:
      print(f"Error: {e}")
      conn.rollback()


# add_user("example_user", "m@example.com", "securepassword")

@router.post("/user/register", response_model=Token)
async def signup(login_input: LoginInput):
  """
  Sign up a new user and log them in by returning a JWT token.

  Args:
    login_input (LoginInput): The email and password for signup.

  Returns:
    Token: A response containing the email, JWT token, and expiry.
  """
  # Hash the password
  password_hash = bcrypt.hash(login_input.password)

  with conn.cursor() as cursor:
    try:
      # Insert the new user into the database
      cursor.execute("""
      INSERT INTO users (username, email, password_hash)
      VALUES (%s, %s, %s);
      """, (login_input.email.split('@')[0], login_input.email, password_hash))
      conn.commit()

      cursor.execute("SELECT user_id FROM users WHERE email = %s;", (login_input.email,))
      user_id = cursor.fetchone()

    except Exception as e:
      # Check for duplicate email or username
      if "unique constraint" in str(e).lower():
        raise HTTPException(status_code=400, detail="Email already in use.")
      raise HTTPException(status_code=500, detail="An error occurred while signing up.")

  # Create a token for the new user
  token = create_access_token(email=login_input.email)
  expires_at = (datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)).isoformat()
  return {"user_id": user_id, "email": login_input.email, "token": token, "expires_at": expires_at}


@router.get("/user/session")
async def check_session(request: Request):
  """
  Check if the user has an active session based on the token provided in the headers.
  Returns user details if the session is valid.
  """
  # Extract the token from the Authorization header
  
  conn = get_connection()
  cursor = conn.cursor()
  auth_header = request.headers.get("Authorization")
  if not auth_header or not auth_header.startswith("Bearer "):
    raise HTTPException(status_code=401, detail="Token missing or invalid")

  token = auth_header.split(" ")[1]  # Get the token part

  try:
    # Decode the token
    payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    email = payload.get("sub")

    if not email:
      raise HTTPException(status_code=401, detail="Invalid token")

    # Query the database to check if the user exists
    cursor.execute("SELECT email FROM users WHERE email = %s", (email,))
    user = cursor.fetchone()

    if not user:
      raise HTTPException(status_code=401, detail="User does not exist")

    cursor.close()
    conn.close()
    # Return user details
    return {"email": user["email"]}
    
  except JWTError:
    raise HTTPException(status_code=401, detail="Invalid or expired token")
    