# Importamos FastAPI y librerías necesarias
from fastapi import FastAPI, Request, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager

from middlewares.security import securityHeaders, setupCors
from middlewares.limiter import limiter
from configs.database import connectDb, closeDb, getDb

from src.auth.modelAuth import UserLogin, Token, TokenData, UserRegister, RegisterResponse
from src.auth.controllerAuth import AuthController
from src.auth.dependencies import getCurrentUser, oauth2Scheme

# Función que se ejecuta cuando inicia o se apaga el server
@asynccontextmanager
async def lifespan(app: FastAPI):
    await connectDb()
    yield
    await closeDb()

# Creamos la app de FastAPI
app = FastAPI(lifespan=lifespan)

# Aplicamos middlewares para CORS y seguridad
setupCors(app)
app.middleware("http")(securityHeaders)
app.middleware("https")(securityHeaders)
app.state.limiter = limiter

# Ruta raíz para verificar que el server funciona
@app.get("/")
@limiter.limit("5/minute")
async def home(request: Request):
    return {"message": "Funciona el server wey!"}

# Ruta para probar conexión a la base de datos
@app.get("/test-db")
async def testDb(db: AsyncSession = Depends(getDb)):
    result = await db.execute(text("SELECT version()"))
    version = result.scalar()
    return {"postgresVersion": version}

# Ruta de login que devuelve un token si todo va bien
@app.post("/auth/login", response_model=Token)
async def login(userData: UserLogin, db: AsyncSession = Depends(getDb)):
    return await AuthController.login(db, userData)

# Ruta de logout, simplemente devuelve un mensaje
@app.post("/auth/logout")
async def logout(currentUser: TokenData = Depends(getCurrentUser)):
    return await AuthController.logout()

# Ruta para obtener datos del usuario logueado
@app.get("/auth/me")
async def readUser(currentUser: TokenData = Depends(getCurrentUser)):
    return currentUser

# Ruta para registrar un nuevo usuario
@app.post(
    "/auth/register", 
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    responses = {
        status.HTTP_201_CREATED: {"description": "Registro exitoso"},
        status.HTTP_400_BAD_REQUEST: {"description": "Error de validacion o email existente"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Error interno del servidor"}
    },
    summary="Registra un nuevo usuario",
    tags=["Auth"]
)
async def registerUser(
    userData: UserRegister,
    db: AsyncSession = Depends(getDb)
) -> RegisterResponse:
    return await AuthController.registerClient(db, userData)