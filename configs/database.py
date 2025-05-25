from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event, text
from typing import AsyncGenerator
from dotenv import load_dotenv

# Cargamos las variables del .env
load_dotenv()

# URL de conexión a la base de datos
DATABASE_URL = "postgresql+asyncpg://neondb_owner:npg_kZ9ELSH5RjBQ@ep-icy-dawn-a4jemjme-pooler.us-east-1.aws.neon.tech/ixaviadb"

# Creamos el engine de conexión
engine = create_async_engine(
    DATABASE_URL,
    connect_args={"ssl": "require"},
    pool_size=20,
    max_overflow=10,
    echo=True
)

# Creamos la sesión asincrónica
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# Evento que se lanza al conectarse
@event.listens_for(engine.sync_engine, "connect")
def onConnect(dbapiConnection, connectionRecord):
    print("PostgreSQL | Conectando...")

# Evento que se lanza al desconectarse
@event.listens_for(engine.sync_engine, "close")
def onClose(dbapiConnection, connectionRecord):
    print("PostgreSQL | Desconectado")

# Función para testear conexión al iniciar
async def connectDb():
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
            print("PostgreSQL | ¡Conexión exitosa!")
    except Exception as e:
        print(f"PostgreSQL | Error de conexión: {e}")
        raise

# Obtenemos una sesión nueva en cada request
async def getDb() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session

# Cerramos el engine al apagar el server
async def closeDb():
    await engine.dispose()
    print("PostgreSQL | Conexión cerrada")
