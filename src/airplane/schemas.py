from sqlalchemy import Column, Integer, String, Enum, Date, ForeignKey, Time
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Airplane(Base):
    __tablename__ = "aviones"

    avionid = Column(Integer, primary_key=True, index=True)
    matricula = Column(String(20), nullable=False)
    modelo = Column(String(100), nullable=False)
    capacidad = Column(Integer, nullable=False)
    estado = Column(String(20), default="activo")