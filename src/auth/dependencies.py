from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from .modelAuth import TokenData
from configs.database import getDb

SECRET_KEY = "3sUnaC1aveSup3erS3cret2"
ALGORITHM = "HS256"

oauth2Scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def getCurrentUser(token: str = Depends(oauth2Scheme), db: AsyncSession = Depends(getDb)):
    credentialsException = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        userId: int = payload.get("userId")
        role: str = payload.get("rol")

        if email is None or userId is None:
            raise credentialsException

        return TokenData(email=email, userId=userId, role=role)
    except JWTError:
        raise credentialsException
