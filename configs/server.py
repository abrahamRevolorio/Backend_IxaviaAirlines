# Importamos las librerias
from fastapi import FastAPI, Request, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager

from middlewares.security import security_headers, setup_cors
from middlewares.limiter import limiter
from configs.database import connect_db, close_db, get_db

from src.auth.modelAuth import UserLogin, Token, TokenData
from src.auth.controllerAuth import AuthController
from src.auth.dependencies import get_current_user, oauth2_scheme

# Funcion para manejar los estados de la base de datos
@asynccontextmanager
async def lifespan(app: FastAPI):
    await connect_db()
    yield
    await close_db()

# Inicializamos FastAPI con la base de datos
app = FastAPI(lifespan=lifespan)

# Agregamos los middlewares
setup_cors(app)
app.middleware("http")(security_headers)
app.middleware("https")(security_headers)
app.state.limiter = limiter

# Peticion ruta raiz
@app.get("/")
@limiter.limit("5/minute")
async def home(request: Request):
    return {"message": "Funciona El Server Wey!"}

# Peticion para probar la base de datos
@app.get("/test-db")
async def test_db(db: AsyncSession = Depends(get_db)):
    result = await db.execute(text("SELECT version()"))
    version = result.scalar()
    return {"postgres_version": version}

@app.post("/auth/login", response_model=Token)
async def login(
    user_data: UserLogin,
    db: AsyncSession = Depends(get_db)
):
    return await AuthController.login(db, user_data)

@app.post("/auth/logout")
async def logout(
    current_user: TokenData = Depends(get_current_user)
):
    return await AuthController.logout()

@app.get("/auth/me")
async def read_users_me(
    current_user: TokenData = Depends(get_current_user)
):
    return current_user
