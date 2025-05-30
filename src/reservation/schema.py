from sqlalchemy import Column, Integer, String, Date, ForeignKey, Time
from sqlalchemy.orm import declarative_base

Base = declarative_base()

class Reservation(Base):
    __tablename__ = "reservaciones"
    reservaid = Column(Integer, primary_key=True, index=True)
    asiento_id = Column(Integer, ForeignKey("asientos.asientoid"), nullable=False)
    vuelo_id = Column(Integer, ForeignKey("vuelos.vueloid"), nullable=False)
    cliente_id = Column(Integer, ForeignKey("clientes.clienteid"), nullable=False)
    estado = Column(String(20), default="activo")

class Sits(Base):
    __tablename__ = "asientos"
    asientoid = Column(Integer, primary_key=True, index=True)
    fila = Column(Integer, nullable=False)
    columna = Column(Integer, nullable=False)
    avion_id = Column(Integer, ForeignKey("aviones.avionid"), nullable=False)
    estado = Column(String(20), default="activo")

class Flight(Base):
    __tablename__ = "vuelos"

    vueloid = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=False)
    horasalida = Column(Time, nullable=False)
    horallegada = Column(Time, nullable=False)
    destino_id = Column(Integer, ForeignKey("destinos.destinoid"), nullable=False)
    avion_id = Column(Integer, ForeignKey("aviones.avionid"), nullable=False)
    estado = Column(String(20), default="activo")

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