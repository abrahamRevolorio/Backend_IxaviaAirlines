from sqlalchemy import Column, Integer, String, Date, ForeignKey
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Sits(Base):
    __tablename__ = "asientos"
    asientoid = Column(Integer, primary_key=True, index=True)
    fila = Column(Integer, nullable=False)
    columna = Column(Integer, nullable=False)
    avion_id = Column(Integer, ForeignKey("aviones.avionid"), nullable=False)
    estado = Column(String(20), default="activo")