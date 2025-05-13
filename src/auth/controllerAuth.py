from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .modelAuth import Token, TokenData
from .schemas import User

SECRET_KEY = "3sUnaC1aveSup3erS3cret2"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class AuthController:

    @staticmethod
    def createAccessToken(data: dict, expiresDelta: timedelta | None = None):
        toEncode = data.copy()
        expire = datetime.utcnow() + (expiresDelta or timedelta(minutes=15))
        toEncode.update({"exp": expire})
        return jwt.encode(toEncode, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    async def authenticateUser(db: AsyncSession, email: str, password: str):
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        if not user or not user.verifyPassword(password):
            return None
        return user

    @staticmethod
    async def login(db: AsyncSession, userData):
        user = await AuthController.authenticateUser(db, userData.email, userData.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"},
            )

        accessTokenExpires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        tokenPayload = {
            "sub": user.email,
            "userId": user.usuarioid,
            "rol": "admin" if user.rol_id == 1 else "user"
        }

        return {
            "accessToken": AuthController.createAccessToken(tokenPayload, expiresDelta=accessTokenExpires),
            "tokenType": "bearer"
        }

    @staticmethod
    async def logout():
        return {"message": "Logout exitoso"}
