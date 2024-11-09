from typing import Optional
from fastapi import HTTPException, status
from jose import JWTError, jwt

# Secret key for JWT encryption
SECRET_KEY = "secretkey"  # Replace with a more secure value
ALGORITHM = "HS256"

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

# функция возвращения email или названия чата
def get_user_chat(token: str, type:str) -> Optional[str]:
    if token is None:
        raise credentials_exception
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if type == "email":
            result: str = payload.get("sub")
        else:
            result: str = payload.get("chat")
        if result is None:
            raise credentials_exception
        return result
    except JWTError:
        raise credentials_exception
