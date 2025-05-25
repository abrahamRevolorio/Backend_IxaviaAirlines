from sqlalchemy import Column, Integer, String, Enum
from sqlalchemy.orm import declarative_base

Base = declarative_base()


class Role(Base):
    __tablename__ = "roles"
    rolid = Column(Integer, primary_key=True, index=True)
    nombrerol = Column(String(100), nullable=False)
    estado = Column(Enum('activo', 'inactivo', 'pendiente', name='estado_rol'))

    def toDict(self):
        return {
            "rolid": self.rolid,
            "nombrerol": self.nombrerol,
            "estado": self.estado
        }