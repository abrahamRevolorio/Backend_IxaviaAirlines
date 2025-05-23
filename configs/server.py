# Importamos FastAPI y librerías necesarias
from fastapi import FastAPI, Request, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from pydantic import ValidationError

from middlewares.security import securityHeaders, setupCors
from middlewares.limiter import limiter
from configs.database import connectDb, closeDb, getDb

from src.auth.modelAuth import UserLogin, Token, TokenData, UserRegister, RegisterResponse
from src.auth.controllerAuth import AuthController
from src.auth.dependencies import getCurrentUser, oauth2Scheme
from src.users.controllerUser import UserController
from src.users.modelUser import ClientRegister, EmployerRegister, FindUser, DeleteUser

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

@app.post(
    "/user/add",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    responses = {
        status.HTTP_201_CREATED: {"description": "Registro exitoso"},
        status.HTTP_400_BAD_REQUEST: {"description": "Error de validación o email existente"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Error interno del servidor"}
    },
    summary="Registra un nuevo usuario",
    tags=["Users"]
)
async def registerUser(
    request: Request,
    db: AsyncSession = Depends(getDb),
    current_user: TokenData = Depends(getCurrentUser)
) -> RegisterResponse:
    try:
        data = await request.json()
        rol = data.get("rol")

        if rol not in ["Cliente", "Agente", "Administrador"]:
            return RegisterResponse(success=False, message="Rol no válido")

        if current_user.role not in ["Administrador", "Agente"]:
            return RegisterResponse(success=False, message="No tienes permiso para realizar esta acción")

        if current_user.role != "Administrador" and rol != "Cliente":
            return RegisterResponse(success=False, message="No puedes agregar un administrador o agente")

        if rol == "Cliente":
            userData = ClientRegister(**data)
            return await UserController.registerClient(db, userData)
        else:
            userData = EmployerRegister(**data)
            return await UserController.registerEmployer(db, userData)

    except ValidationError as e:
        return RegisterResponse(success=False, message=f"Datos inválidos: {e.errors()}")
    except Exception as e:
        return RegisterResponse(success=False, message=f"Error interno: {str(e)}")
    
@app.get(
    "/user/view",
    status_code=status.HTTP_200_OK,
    responses = {
        status.HTTP_200_OK: {"description": "Consulta exitosa"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Error interno del servidor"}
    },
    summary="Obtiene todos los usuarios",
    tags=["Users"]
)
async def viewUsers(db: AsyncSession = Depends(getDb), current_user: TokenData = Depends(getCurrentUser)):
    if current_user.role == "Administrador" or current_user.role == "Agente":
        return await UserController.viewUsers(db)
    else:
        return {"success": False,
                "message": "No tienes permiso para esta acción"
                }
    
@app.get(
    "/user/find",
    status_code=status.HTTP_200_OK,
    responses = {
        status.HTTP_200_OK: {"description": "Consulta exitosa"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Error interno del servidor"}
    },
    summary="Obtiene todos los usuarios",
    tags=["Users"]
)
async def viewUsers(userData: FindUser, db: AsyncSession = Depends(getDb), current_user: TokenData = Depends(getCurrentUser)) -> RegisterResponse:
    if current_user.role == "Administrador" or current_user.role == "Agente":
        return await UserController.findUser(db, userData)
    else:
        return RegisterResponse(success=False, message="No tienes permiso para esta acción")

@app.delete(
    "/user/delete",
    status_code=status.HTTP_200_OK,
    responses = {
        status.HTTP_200_OK: {"description": "Consulta exitosa"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Error interno del servidor"}
    },
    summary="Obtiene todos los usuarios",
    tags=["Users"]
)
async def deleteUser(userData: DeleteUser, db: AsyncSession = Depends(getDb), current_user: TokenData = Depends(getCurrentUser)) -> RegisterResponse:
    if current_user.role == "Administrador":
        return await UserController.deleteUser(db, userData)
    else:
        return RegisterResponse(success=False, message="No tienes permiso para esta acción")