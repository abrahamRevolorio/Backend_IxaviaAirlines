# Importamos las librerias
import os
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event
from dotenv import load_dotenv
from sqlalchemy import text
from typing import AsyncGenerator

#Inicializamos el archivo .env
load_dotenv()

# Definimos la URL de la base de datos
DATABASE_URL = "postgresql+asyncpg://neondb_owner:npg_kZ9ELSH5RjBQ@ep-icy-dawn-a4jemjme-pooler.us-east-1.aws.neon.tech/ixaviadb"

# Instancia de la base de datos
engine = create_async_engine(
    DATABASE_URL,
    connect_args={
        "ssl": "require"
    },
    pool_size=20, 
    max_overflow=10, 
    echo=True
)

# Instancia del inicio de sesion en la base de datos
AsyncSessionLocal = sessionmaker(

    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
   
)

# Evento para conectar a la base de datos
@event.listens_for(engine.sync_engine, "connect")
def on_connect(dbapi_connection, connection_record):
    print("PostgreSQL | Conectando...")

# Evento para desconectar de la base de datos
@event.listens_for(engine.sync_engine, "close")
def on_close(dbapi_connection, connection_record):
    print("PostgreSQL | Desconectado")

# Funcion para conectar a la base de datos
async def connect_db():
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
            print("PostgreSQL | ¡Conexión exitosa!")
    except Exception as e:
        print(f"PostgreSQL | Error de conexión: {e}")
        raise

# Funcion para obtener la sesion de la base de datos
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

# Funcion para cerrar la sesion de la base de datos
async def close_db():
    await engine.dispose()
    print("PostgreSQL | Conexión cerrada")