from fastapi import HTTPException, Header
from jose import jwt
from app.settings import SECRET_KEY
from uuid import UUID
from jose.exceptions import JWTError, ExpiredSignatureError



ALGORITHM = "HS256"


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


