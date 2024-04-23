from datetime import timedelta, datetime
from typing import Optional

from jose import jwt

from app.config import settings

JWT_EXPIRE_DAYS = 365
SECRET_KEY = settings.JWT_SECRET_KEY
ALGORITHM = settings.JWT_ALGORITHM


def obtain_jwt(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(days=JWT_EXPIRE_DAYS)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_jwt(jwt_token: str):
    user_data_dict = jwt.decode(jwt_token, key=SECRET_KEY, algorithms=ALGORITHM)
    return user_data_dict
