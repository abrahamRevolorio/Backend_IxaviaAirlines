from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import declarative_base
from passlib.context import CryptContext

Base = declarative_base()
pwdContext = CryptContext(schemes=["bcrypt"], deprecated="auto")

class User(Base):
    __tablename__ = "usuarios"

    usuarioid = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    passwordhash = Column(String(225))
    rol_id = Column(Integer)
    estado = Column(String(20), default=True)

    def verifyPassword(self, plainPassword: str):
        return pwdContext.verify(plainPassword, self.passwordhash)
