from jose import jwt
from datetime import datetime, timedelta
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import insert, text
from datetime import date
from passlib.hash import bcrypt

from .modelAuth import Token, TokenData, UserRegister, RegisterResponse
from .schemas import User, Cliente

SECRET_KEY = "3sUnaC1aveSup3erS3cret2"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

class AuthController:

    @staticmethod
    def createAccessToken(data: dict, expiresDelta: timedelta | None = None):
        toEncode = data.copy()
        expire = datetime.utcnow() + (expiresDelta or timedelta(minutes=15))
        toEncode.update({"exp": expire})
        return jwt.encode(toEncode, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    async def authenticateUser(db: AsyncSession, email: str, password: str):
        result = await db.execute(select(User).where(User.email == email))
        user = result.scalars().first()
        if not user or not user.verifyPassword(password):
            return None
        return user

    @staticmethod
    async def login(db: AsyncSession, userData):
        user = await AuthController.authenticateUser(db, userData.email, userData.password)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Credenciales incorrectas",
                headers={"WWW-Authenticate": "Bearer"},
            )

        accessTokenExpires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

        if user.rol_id == 1:
            rolActual = "Administrador"
            query_str = text("""
                SELECT 
                    e.*, 
                    u.email, 
                    u.fecharegistro, 
                    u.estado AS estado_usuario,
                    r.nombrerol
                FROM 
                    empleados e
                JOIN 
                    usuarios u ON e.usuario_id = u.usuarioid
                JOIN
                    roles r ON u.rol_id = r.rolid
                WHERE 
                    u.email = :email
            """)
            result = await db.execute(query_str, {"email": userData.email})
            dataUser = result.mappings().first()

            tokenPayload = {
                "sub": user.email,
                "userId": user.usuarioid,
                "rol": rolActual,
                "nombre": dataUser.nombre,
                "apellido": dataUser.apellido,
                "dpi": dataUser.dpi,
                "nit": dataUser.nit,
                "telefono": dataUser.telefono,
                "edad": dataUser.edad
            }
        elif user.rol_id == 2:
            rolActual = "Cliente"
            query_str = text("""
                SELECT 
                    c.*, 
                    u.email, 
                    u.fecharegistro, 
                    u.estado AS estado_usuario,
                    r.nombrerol
                FROM 
                    clientes c
                JOIN 
                    usuarios u ON c.usuario_id = u.usuarioid
                JOIN
                    roles r ON u.rol_id = r.rolid
                WHERE 
                    u.email = :email
            """)
            result = await db.execute(query_str, {"email": userData.email})
            dataUser = result.mappings().first()

            tokenPayload = {
                "sub": user.email,
                "userId": user.usuarioid,
                "rol": rolActual,
                "nombre": dataUser.nombre,
                "apellido": dataUser.apellido,
                "dpi": dataUser.dpi,
                "telefono": dataUser.telefono,
                "direccion": dataUser.direccion,
                "fechadenacimiento": dataUser.fechadenacimiento,
                "nacionalidad": dataUser.nacionalidad,
                "edad": dataUser.edad,
                "telefonoemergencia": dataUser.telefonoemergencia
            }

        elif user.rol_id == 3:
            rolActual = "Agente"
            query_str = text("""
                SELECT 
                    e.*, 
                    u.email, 
                    u.fecharegistro, 
                    u.estado AS estado_usuario,
                    r.nombrerol
                FROM 
                    empleados e
                JOIN 
                    usuarios u ON e.usuario_id = u.usuarioid
                JOIN
                    roles r ON u.rol_id = r.rolid
                WHERE 
                    u.email = :email
            """)
            result = await db.execute(query_str, {"email": userData.email})
            dataUser = result.mappings().first()

            tokenPayload = {
                "sub": user.email,
                "userId": user.usuarioid,
                "rol": rolActual,
                "nombre": dataUser.nombre,
                "apellido": dataUser.apellido,
                "dpi": dataUser.dpi,
                "nit": dataUser.nit,
                "telefono": dataUser.telefono,
                "edad": dataUser.edad
            }

        return {
            "accessToken": AuthController.createAccessToken(tokenPayload, expiresDelta=accessTokenExpires),
            "tokenType": "bearer"
        }

    @staticmethod
    async def logout():
        return {"message": "Logout exitoso"}
    
    @staticmethod
    async def registerClient(db: AsyncSession, userData: UserRegister) -> RegisterResponse:

        try:

            existingUser = await db.execute(select(User).where(User.email == userData.email))

            if existingUser.scalars().first():
                return RegisterResponse(
                    success=False,
                    message="El email ya esta registrado"
                )
            
            hashedPassword = bcrypt.hash(userData.password)
                
            newUser = User(

                email = userData.email,
                passwordhash  = hashedPassword,
                rol_id = 2,
                estado = "activo"

            )

            db.add(newUser)

            await db.flush()

            today = date.today()
            age = today.year - userData.nacimiento.year - (
                (today.month, today.day) < (userData.nacimiento.month, userData.nacimiento.day)
            )

            newClient = {
                "dpi": userData.dpi,
                "nombre": userData.nombres,
                "apellido": userData.apellidos,
                "telefono": userData.telefono,
                "direccion": userData.direccion,
                "fechadenacimiento": userData.nacimiento,
                "nacionalidad": userData.nacionalidad,
                "edad": age,
                "telefonoemergencia": userData.telefonoEmergencia,
                "usuario_id": newUser.usuarioid
            }

            await db.execute(
            text("""
            INSERT INTO clientes 
            (dpi, nombre, apellido, telefono, direccion, fechadenacimiento, 
             nacionalidad, edad, telefonoemergencia, usuario_id)
            VALUES 
            (:dpi, :nombre, :apellido, :telefono, :direccion, :fechadenacimiento, 
             :nacionalidad, :edad, :telefonoemergencia, :usuario_id)
            """),
            newClient
        )

            await db.commit()

            return RegisterResponse(

                success=True,
                message="El usuario se ha registrado correctamente",
                user_info={
                    "email": newUser.email,
                    "nombres": userData.nombres,
                    "apellidos": userData.apellidos
                },
                status_code=201

            )

        except Exception as e:
            await db.rollback()
            print(f"Error completo: {repr(e)}")
            return RegisterResponse(
                success=False,
                message="Error interno del servidor",
                status_code=500
            )