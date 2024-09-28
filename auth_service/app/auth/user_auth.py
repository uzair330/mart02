from fastapi import HTTPException, Header
from jose import jwt
# from passlib.context import CryptContext
from datetime import datetime, timedelta, timezone
from app.settings import SECRET_KEY
from uuid import UUID
from jose.exceptions import JWTError, ExpiredSignatureError
from app.models.user_model import User
from passlib.context import CryptContext
from typing import Optional


ALGORITHM = "HS256"

# bycrpt encrption
pwd_context = CryptContext(schemes=["bcrypt"], deprecated= "auto")


# Creating access token
def create_token(user: User, expires_delta: timedelta) -> str:
    try:
        expire = datetime.now(timezone.utc) + expires_delta
        payload = {
            "user_id": str(user.id),
            "username": user.username,
            "email": user.email,
            "exp": expire,
        }
        headers = {"iss": user.iss_key}
        token = jwt.encode(payload, str(SECRET_KEY), algorithm=ALGORITHM, headers=headers)
        return token
    except JWTError as e:
        raise HTTPException(status_code=500, detail=f"Error generating token: {e}")





# # def userId_from_token(auth: str = Header(...)) -> UUID:
# def userId_from_token(token:str) -> UUID:

#     # # Check if the Authorization header exists and starts with 'Bearer '
#     # if not auth or not auth.startswith("Bearer "):
#     #     raise HTTPException(status_code=401, detail="Invalid or missing Authorization header")
    
#     # # Extract the token safely
#     # try:
#     #     token = auth.split("Bearer ")[1]
#     # except IndexError:
#     #     raise HTTPException(status_code=401, detail="Invalid token format")
    
#     # Decode the JWT token
    
#     try:
#         payload = jwt.decode(token, str(SECRET_KEY), algorithms=[ALGORITHM])
#         user_id = payload.get("user_id")
        
#         if not user_id:
#             raise HTTPException(status_code=401, detail="User ID not found in token")
        
#         return UUID(user_id)
    
#     except JWTError as e:
#         raise HTTPException(status_code=401, detail=f"Token decoding error: {str(e)}")
    
#     except ValueError:
#         raise HTTPException(status_code=400, detail="Invalid User ID format")





# def userId_from_token(token:str) -> UUID:
def userId_from_token(Authorization: str = Header(...)) -> UUID:

    # Check if the Authorization header exists and starts with 'Bearer '
    if not Authorization or not Authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing Authorization header")
    
    # Extract the token safely
    try:
        token = Authorization.split("Bearer ")[1]
    except IndexError:
        raise HTTPException(status_code=401, detail="Invalid token format")
    
    # Decode the JWT token
    
    try:
        payload = jwt.decode(token, str(SECRET_KEY), algorithms=[ALGORITHM])
        user_id = payload.get("user_id")
        
        if not user_id:
            raise HTTPException(status_code=401, detail="User ID not found in token")
        
        return UUID(user_id)
    
    except JWTError as e:
        raise HTTPException(status_code=401, detail=f"Token decoding error: {str(e)}")
    
    except ValueError:
        raise HTTPException(status_code=400, detail="Invalid User ID format")






def password_verification(raw_password:str,hashed_password)-> bool:
    verify_pass = pwd_context.verify(raw_password,hashed_password)
    return verify_pass


def hashed_password(password:str)->str:
    return pwd_context.hash(password)
