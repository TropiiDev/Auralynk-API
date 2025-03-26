import os

from datetime import datetime, timedelta
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from tables import *
from sql import *
from functions import *

from dotenv import load_dotenv

load_dotenv()

secret_key = os.getenv("SECRET_KEY")
algo = os.getenv("ALGORITHM")

pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def create_access_token(data: dict, expires_delta: timedelta or None = None):
    to_encode = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)

    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, secret_key, algorithm=algo)
    return encoded_jwt

async def get_current_user(session: SessionDep, token: str = Depends(oauth2_scheme)):
    credential_exception = HTTPException(status_code=401, detail="Could not validate credentials", headers={"WWW-Authenticate": "Bearer"})
    try:
        payload = jwt.decode(token, secret_key, algorithms=[algo])
        username: str = payload.get("sub")
        if username is None:
            raise credential_exception

        token_data = TokenData(username=username)
    except JWTError:
        raise credential_exception

    user = get_user_by_username(token_data.username, session)
    if user is None:
        raise credential_exception

    return user
