# auth.py
from datetime import datetime, timedelta
from typing import Optional
from jose import jwt, JWTError
import os
from dotenv import load_dotenv

load_dotenv()

# Secreto para firmar y verificar tokens (¡debes cambiarlo en producción!)
SECRET_KEY = os.getenv("SECRET")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt