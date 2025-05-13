from jose import JWTError, jwt
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from .modelAuth import Token, TokenData
from .schemas import User
from configs.database import get_db

SECRET_KEY = "3sUnaC1aveSup3erS3cret2"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class AuthController:

    @staticmethod
    def createAccessToken(data: dict, expiresDelta: timedelta | None = None):
        toEncode = data.copy()

        if expiresDelta:
            expire = datetime.utcnow() + expiresDelta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)

        toEncode.update({"exp": expire})
        encodedJWT = jwt.encode(toEncode, SECRET_KEY, algorithm=ALGORITHM)
        return encodedJWT

    @staticmethod
    async def authenticateUser(
        db: AsyncSession,
        email: str,
        password: str,
    ):
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()

        if not user or not user.verify_password(password):
            return None
        
        return user

    @staticmethod
    async def login(
        db: AsyncSession,
        userData
    ):
        user = await AuthController.authenticateUser(
            db,
            userData.email,
            userData.password,
        )

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        token_payload = {
            "sub": user.email,
            "user_id": user.usuarioid,
            "rol": "admin" if user.rol_id == 1 else "user"
        }

        return {
            "access_token": AuthController.createAccessToken(
                token_payload, expiresDelta=access_token_expires
            ),
            "token_type": "bearer"
        }

    @staticmethod
    async def logout():
        return {"message": "Logout exitoso"}
