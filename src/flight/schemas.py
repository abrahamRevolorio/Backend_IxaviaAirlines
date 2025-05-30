from sqlalchemy import Column, Integer, String, Enum, Date, ForeignKey, Time
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Flight(Base):
    __tablename__ = "vuelos"

    vueloid = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=False)
    horasalida = Column(Time, nullable=False)
    horallegada = Column(Time, nullable=False)
    destino_id = Column(Integer, ForeignKey("destinos.destinoid"), nullable=False)
    avion_id = Column(Integer, ForeignKey("aviones.avionid"), nullable=False)
    estado = Column(String(20), default="activo")