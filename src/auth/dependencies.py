from fastapi import Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession

from .modelAuth import TokenData
from configs.database import getDb

SECRET_KEY = "3sUnaC1aveSup3erS3cret2"
ALGORITHM = "HS256"

oauth2Scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def getCurrentUser(request: Request, db: AsyncSession = Depends(getDb)):
    authHeader = request.headers.get("authorization")

    if not authHeader:
        print("🔴 Falta autenticación (no se envió ninguna cabecera Authorization)")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta autenticación",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not authHeader.lower().startswith("bearer "):
        print("🔴 Falta 'Bearer' en el encabezado Authorization")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta 'Bearer' en la cabecera Authorization",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token = authHeader[7:].strip()
    if not token:
        print("🔴 Falta token después de 'Bearer'")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Falta token en la cabecera Authorization",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("sub")
        userId = payload.get("userId")
        role = payload.get("rol")

        if email is None or userId is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido: faltan campos obligatorios",
                headers={"WWW-Authenticate": "Bearer"},
            )

        return TokenData(email=email, userId=userId, role=role)

    except JWTError:
        print("🔴 Token inválido o expirado")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token inválido o expirado",
            headers={"WWW-Authenticate": "Bearer"},
        )
