# Importamos FastAPI y todas las librerías que vamos a usar
from fastapi import FastAPI, Request, Depends, status
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from contextlib import asynccontextmanager
from pydantic import ValidationError

# Middlewares personalizados para seguridad, CORS y límite de peticiones
from middlewares.security import securityHeaders, setupCors
from middlewares.limiter import limiter

# Conexión a la base de datos
from configs.database import connectDb, closeDb, getDb

# Modelos y controladores de autenticación
from src.auth.modelAuth import UserLogin, Token, TokenData, UserRegister, RegisterResponse
from src.auth.controllerAuth import AuthController
from src.auth.dependencies import getCurrentUser, oauth2Scheme

# Modelos y controladores de usuarios
from src.users.controllerUser import UserController
from src.users.modelUser import ClientRegister, EmployerRegister, FindUser, DeleteUser, UpdateUser

from src.roles.controllerRole import RoleController
from src.roles.modelRole import RoleModel, RoleResponse, UpdateRole, DeleteRole

# Esto se ejecuta cuando el servidor se prende o se apaga
@asynccontextmanager
async def lifespan(app: FastAPI):
    await connectDb()  # Conectamos a la base de datos
    yield
    await closeDb()  # Cerramos la conexión cuando el servidor se apague

# Inicializamos la app de FastAPI
app = FastAPI(lifespan=lifespan)

# Configuramos los middlewares de CORS y seguridad
setupCors(app)
app.middleware("http")(securityHeaders)
app.middleware("https")(securityHeaders)
app.state.limiter = limiter  # Limite de peticiones por IP

# Ruta base para comprobar que el servidor está vivo
@app.get("/")
@limiter.limit("50/minute")
async def home(request: Request):
    return {"message": "Funciona el server wey!"}

@app.get("/ping")
async def ping():
    return {"message": "pong"}

# Ruta para probar si la conexión con la base de datos está bien
@app.get("/test-db")
@limiter.limit("50/minute")
async def testDb(request: Request, db: AsyncSession = Depends(getDb)):
    result = await db.execute(text("SELECT version()"))
    version = result.scalar()
    return {"postgresVersion": version}

# Login de usuario, si todo va bien devuelve el token
@app.post("/auth/login", response_model=Token)
@limiter.limit("50/minute")
async def login(request: Request, userData: UserLogin, db: AsyncSession = Depends(getDb)):
    return await AuthController.login(db, userData)

# Logout, no hace mucho más que responder con un mensaje
@app.post("/auth/logout")
@limiter.limit("50/minute")
async def logout(request: Request, currentUser: TokenData = Depends(getCurrentUser)):
    return await AuthController.logout()

# Devuelve los datos del usuario que hizo login (según el token)
@app.get("/auth/me")
@limiter.limit("50/minute")
async def readUser(request: Request, currentUser: TokenData = Depends(getCurrentUser)):
    return currentUser

# Ruta pública para registrar un nuevo usuario tipo cliente
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
@limiter.limit("50/minute")
async def registerUser(
    request: Request,
    userData: UserRegister,
    db: AsyncSession = Depends(getDb)
) -> RegisterResponse:
    return await AuthController.registerClient(db, userData)

# Ruta para que agentes o administradores agreguen nuevos usuarios
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
@limiter.limit("50/minute")
async def registerUser(
    request: Request,
    db: AsyncSession = Depends(getDb),
    current_user: TokenData = Depends(getCurrentUser)
) -> RegisterResponse:
    try:
        data = await request.json()
        rol = data.get("rol")

        # Validamos si el rol existe
        if rol not in ["Cliente", "Agente", "Administrador"]:
            return RegisterResponse(success=False, message="Rol no válido")

        # Solo agentes y administradores pueden registrar
        if current_user.role not in ["Administrador", "Agente"]:
            return RegisterResponse(success=False, message="No tienes permiso para realizar esta acción")

        # Un agente no puede registrar a otro agente o admin
        if current_user.role != "Administrador" and rol != "Cliente":
            return RegisterResponse(success=False, message="No puedes agregar un administrador o agente")

        # Según el rol, usamos un modelo u otro
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
    
# Ruta para que admin o agentes puedan ver todos los usuarios
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
@limiter.limit("50/minute")
async def viewUsers(request: Request, db: AsyncSession = Depends(getDb), current_user: TokenData = Depends(getCurrentUser)):
    if current_user.role == "Administrador" or current_user.role == "Agente":
        return await UserController.viewUsers(db)
    else:
        return {"success": False, "message": "No tienes permiso para esta acción"}

# Ruta para buscar un usuario específico
@app.get(
    "/user/find",
    status_code=status.HTTP_200_OK,
    responses = {
        status.HTTP_200_OK: {"description": "Consulta exitosa"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Error interno del servidor"}
    },
    summary="Busca un usuario",
    tags=["Users"]
)
@limiter.limit("50/minute")
async def viewUsers(request: Request, userData: FindUser, db: AsyncSession = Depends(getDb), current_user: TokenData = Depends(getCurrentUser)) -> RegisterResponse:
    if current_user.role == "Administrador" or current_user.role == "Agente":
        return await UserController.findUser(db, userData)
    else:
        return RegisterResponse(success=False, message="No tienes permiso para esta acción")

# Ruta para eliminar un usuario (solo admins)
@app.delete(
    "/user/delete",
    status_code=status.HTTP_200_OK,
    responses = {
        status.HTTP_200_OK: {"description": "Consulta exitosa"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Error interno del servidor"}
    },
    summary="Elimina un usuario",
    tags=["Users"]
)
@limiter.limit("50/minute")
async def deleteUser(request: Request, userData: DeleteUser, db: AsyncSession = Depends(getDb), current_user: TokenData = Depends(getCurrentUser)) -> RegisterResponse:
    if current_user.role == "Administrador":
        return await UserController.deleteUser(db, userData)
    else:
        return RegisterResponse(success=False, message="No tienes permiso para esta acción")

@app.put(
    "/user/update",
    status_code=status.HTTP_200_OK,
    responses = {
        status.HTTP_200_OK: {"description": "Consulta exitosa"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Error interno del servidor"}
    },
    summary="Actualizar usuario",
    tags=["Users"]
)
@limiter.limit("50/minute")
async def updateUser(request: Request, userData: UpdateUser, db: AsyncSession = Depends(getDb), current_user: TokenData = Depends(getCurrentUser)) -> RegisterResponse:
    if current_user.role == "Administrador" or current_user.role == "Agente":
        return await UserController.editUser(db, userData, current_user=current_user)
    else:
        return RegisterResponse(success=False, message="No tienes permiso para esta acción")
    
@app.post(
    "/role/add",
    status_code=status.HTTP_200_OK,
    responses = {
        status.HTTP_200_OK: {"description": "Consulta exitosa"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Error interno del servidor"}
    },
    summary="Agregar rol",
    tags=["Users"]
)
@limiter.limit("50/minute")
async def addRole(request: Request, userData: RoleModel, db: AsyncSession = Depends(getDb), current_user: TokenData = Depends(getCurrentUser)) -> RoleResponse:
    if current_user.role == "Administrador":
        return await RoleController.addRole(db, userData)
    else:
        return RoleResponse(success=False, message="No tienes permiso para estaacción")
    
@app.get(
    "/role/view",
    status_code=status.HTTP_200_OK,
    responses = {
        status.HTTP_200_OK: {"description": "Consulta exitosa"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Error interno del servidor"}
    },
    summary="Obtiene todos los roles",
    tags=["Users"]
)
@limiter.limit("50/minute")
async def viewRoles(request: Request, db: AsyncSession = Depends(getDb), current_user: TokenData = Depends(getCurrentUser)) -> RoleResponse:
    if current_user.role == "Administrador":
        return await RoleController.showRoles(db)
    else:
        return RoleResponse(success=False, message="No tienes permiso para estaacción")
    
@app.put(
    "/role/update",
    status_code=status.HTTP_200_OK,
    responses = {
        status.HTTP_200_OK: {"description": "Consulta exitosa"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Error interno del servidor"}
    },
    summary="Actualizar rol",
    tags=["Users"]
)
@limiter.limit("50/minute")
async def updateRole(request: Request, userData: UpdateRole, db: AsyncSession = Depends(getDb), current_user: TokenData = Depends(getCurrentUser)) -> RoleResponse:
    if current_user.role == "Administrador":
        return await RoleController.editRoles(db, userData)
    else:
        return RoleResponse(success=False, message="No tienes permiso para estaacción")
    
@app.delete(
    "/role/delete",
    status_code=status.HTTP_200_OK,
    responses = {
        status.HTTP_200_OK: {"description": "Consulta exitosa"},
        status.HTTP_500_INTERNAL_SERVER_ERROR: {"description": "Error interno del servidor"}
    },
    summary="Eliminar rol",
    tags=["Users"]
)
@limiter.limit("50/minute")
async def deleteRole(request: Request, userData: DeleteRole, db: AsyncSession = Depends(getDb), current_user: TokenData = Depends(getCurrentUser)) -> RoleResponse:
    if current_user.role == "Administrador":
        return await RoleController.deleteRoles(db, userData)
    else:
        return RoleResponse(success=False, message="No tienes permiso para estaacción")