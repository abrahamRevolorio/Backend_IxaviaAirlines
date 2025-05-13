from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import declarative_base
from passlib.context import CryptContext

Base = declarative_base()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "usuarios"

    usuarioid = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    passwordhash = Column(String(225))
    rol_id = Column(Integer)
    estado = Column(String(20), default=True)

    def verify_password(self, plain_password: str):
        return pwd_context.verify(plain_password, self.passwordhash)