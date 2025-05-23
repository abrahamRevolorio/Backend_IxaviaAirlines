from jose import jwt
from datetime import datetime, timedelta, date
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text
from passlib.hash import bcrypt

from .modelUser import ClientRegister, EmployerRegister, RegisterResponse
from .shemas import User, Cliente, Empleado

class UserController:

    @staticmethod
    async def registerClient(db: AsyncSession, userData: ClientRegister) -> RegisterResponse:

        try:
            
            existingUser = await db.execute(select(User).where(User.email == userData.email))

            existingDPI = await db.execute(select(Cliente).where(Cliente.dpi == userData.dpi))

            if existingUser.scalars().first():
                return RegisterResponse(
                    success=False,
                    message="El email ya esta registrado"
                )
            
            if existingDPI.scalars().first():
                return RegisterResponse(
                    success=False,
                    message="El DPI ya esta registrado"
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
                    "email": userData.email,
                    "nombres": userData.nombres,
                    "apellidos": userData.apellidos
                },
                status_code=201

            )

        except Exception as e:
            await db.rollback()
            print(f"Error: {repr(e)}")
            return RegisterResponse(
                success=False,
                message="Error al registrar el usuario",
                status_code=5000
            )
    
    @staticmethod
    async def registerEmployer(db: AsyncSession, userData: EmployerRegister) -> RegisterResponse:

        try:

            existingUser = await db.execute(select(User).where(User.email == userData.email))

            existingDPI = await db.execute(select(Empleado).where(Empleado.dpi == userData.dpi))

            if existingUser.scalars().first():
                return RegisterResponse(
                    success=False,
                    message="El email ya esta registrado"
                )
            
            if existingDPI.scalars().first():
                return RegisterResponse(
                    success=False,
                    message="El DPI ya esta registrado"
                )
            
            hashedPassword = bcrypt.hash(userData.password)

            if userData.rol == "Administrador":
                roleId = 1
            elif userData.rol == "Agente":
                roleId = 3

            newUser = User(

                email = userData.email,
                passwordhash  = hashedPassword,
                rol_id = roleId,
                estado = "activo"

            )

            db.add(newUser)

            await db.flush()

            newEmployer = {

                "nombre": userData.nombres,
                "apellido": userData.apellidos,
                "dpi": userData.dpi,
                "nit": userData.nit,
                "telefono": userData.telefono,
                "edad": userData.edad,
                "usuario_id": newUser.usuarioid

            }

            await db.execute(

                text("""

                    INSERT INTO empleados (nombre, apellido, dpi, nit, telefono, edad, usuario_id)
                    VALUES (:nombre, :apellido, :dpi, :nit, :telefono, :edad, :usuario_id);

                """),

                newEmployer

            )

            await db.commit()

            return RegisterResponse(
                success=True,
                message="El usuario se ha registrado correctamente",
                user_info={
                    "email": userData.email,
                    "nombres": userData.nombres,
                    "apellidos": userData.apellidos
                },
                status_code=201
            )

        except Exception as e:
            await db.rollback()
            print(f"Error: {repr(e)}")
            return RegisterResponse(
                success=False,
                message="Error al registrar el usuario",
                status_code=5000
            )