from typing import Optional
from fastapi import HTTPException, status
from jose import JWTError, jwt

SECRET_KEY = "secretkey"
ALGORITHM = "HS256"

credentials_exception = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail="Could not validate credentials",
    headers={"WWW-Authenticate": "Bearer"},
)

# функция возвращения email или названия чата
def get_user_chat(token: str, get_type: str) -> Optional[str]:
    if token is None:
        raise credentials_exception
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        if get_type == "email":
            result: str = payload.get("sub")
        else:
            result: str = payload.get("name_chat")
        if result is None:
            raise credentials_exception
        return result
    except JWTError:
        raise credentials_exception
