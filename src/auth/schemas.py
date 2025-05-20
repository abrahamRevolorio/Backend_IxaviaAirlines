from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import declarative_base
from passlib.context import CryptContext
from passlib.hash import bcrypt

Base = declarative_base()

class User(Base):
    __tablename__ = "usuarios"

    usuarioid = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    passwordhash = Column(String(225))
    rol_id = Column(Integer)
    estado = Column(String(20), default="activo")

    def verifyPassword(self, plainPassword: str):
        return bcrypt.verify(plainPassword, self.passwordhash)
    
class Cliente(Base):
    __tablename__ = "clientes"

    clienteid = Column(Integer, primary_key=True, index=True)
    dpi = Column(String(20), nullable=False)
    nombre = Column(String(100), nullable=False)
    apellido = Column(String(100), nullable=False)
    telefono = Column(String(15), nullable=False)
    direccion = Column(String(500), nullable=False)
    fechadenacimiento = Column(Date, nullable=False)
    nacionalidad = Column(String(100), nullable=False)
    edad = Column(Integer)
    telefonoemergencia = Column(String(15))
    usuario_id = Column(Integer, ForeignKey("usuarios.usuarioid"), nullable=False)
