'''
Arquivo com componentes gerais de segurança
'''
import jwt
import time
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="Bearer")


JWT_SECRET = "SECRET.20221007"
JWT_ALGORITHM = "HS256"


def token_response(token: str):
    return {
        "access_token": token
    }

def signJWT(user):
    payload = {
        "user_id": user.id,
        "user_email": user.user_email,
        "expires": time.time() + 3600
    }
    token = jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)
    return token_response(token)

def decodeJWT(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        decoded_token = jwt.decode(token.split()[1], JWT_SECRET, algorithms=[JWT_ALGORITHM])
        return decoded_token if check_token_valid(decoded_token) else None
    except:
        return None

def check_token_valid(decoded_token:str) -> bool:
    if decoded_token["expires"] <= time.time():
        return False
    return True 
