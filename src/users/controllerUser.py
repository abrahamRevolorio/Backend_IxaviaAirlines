from jose import jwt
from datetime import datetime, timedelta, date
from fastapi import HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text, update
from passlib.hash import bcrypt

from .modelUser import ClientRegister, EmployerRegister, RegisterResponse, FindUser, DeleteUser
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
        
    @staticmethod
    async def viewUsers(db: AsyncSession):
        try:
            usersResult = await db.execute(select(User).order_by(User.email))
            users = usersResult.scalars().all()

            clientes = []
            empleados = []

            for user in users:
                clientResult = await db.execute(select(Cliente).where(Cliente.usuario_id == user.usuarioid))
                client = clientResult.scalar_one_or_none()

                if client:
                    clientes.append({
                        "user": {
                            "email": user.email,
                            "estado": user.estado,
                            "rol_id": user.rol_id,
                            "usuario_id": user.usuarioid
                        },
                        "cliente": {
                            "nombre": client.nombre,
                            "apellido": client.apellido,
                            "dpi": client.dpi,
                            "telefono": client.telefono,
                            "direccion": client.direccion,
                            "nacionalidad": client.nacionalidad,
                            "edad": client.edad,
                            "telefono_emergencia": client.telefonoemergencia
                        }
                    })
                    continue

                empResult = await db.execute(select(Empleado).where(Empleado.usuario_id == user.usuarioid))
                emp = empResult.scalar_one_or_none()

                if emp:
                    empleados.append({
                        "user": {
                            "email": user.email,
                            "estado": user.estado,
                            "rol_id": user.rol_id,
                            "usuario_id": user.usuarioid
                        },
                        "empleado": {
                            "nombre": emp.nombre,
                            "apellido": emp.apellido,
                            "dpi": emp.dpi,
                            "telefono": emp.telefono,
                            "edad": emp.edad,
                            "nit": emp.nit
                        }
                    })

            return {
                "clientes": clientes,
                "empleados": empleados
            }

        except Exception as e:
            await db.rollback()
            print(f"Error completo: {repr(e)}")
            return RegisterResponse(
                success=False,
                message="Error interno del servidor",
                status_code=500
            )
        
    @staticmethod
    async def findUser(db: AsyncSession, userData: FindUser) -> RegisterResponse:
        try:
            findClientResult = await db.execute(select(Cliente).where(Cliente.dpi == userData.dpi))
            client = findClientResult.scalars().first()

            if client:
                userResult = await db.execute(select(User).where(User.usuarioid == client.usuario_id))
                user = userResult.scalars().first()

                return RegisterResponse(
                    success=True,
                    message="Usuario encontrado",
                    user_info={
                        "email": user.email,
                        "password": user.passwordhash,
                        "dpi": client.dpi,
                        "nombres": client.nombre,
                        "apellidos": client.apellido,
                        "telefono": client.telefono,
                        "direccion": client.direccion,
                        "fechadenacimiento": client.fechadenacimiento.isoformat(),
                        "nacionalidad": client.nacionalidad,
                        "edad": str(client.edad),
                        "telefonoemergencia": client.telefonoemergencia,
                        "rol": "Cliente"
                    },
                    status_code=200
                )

            findEmployerResult = await db.execute(select(Empleado).where(Empleado.dpi == userData.dpi))
            employer = findEmployerResult.scalars().first()

            if employer:
                userResult = await db.execute(select(User).where(User.usuarioid == employer.usuario_id))
                user = userResult.scalars().first()

                if user.rol_id == 1:
                    role = "Administrador"
                elif user.rol_id == 3:
                    role = "Agente"

                return RegisterResponse(
                    success=True,
                    message="Usuario encontrado",
                    user_info={
                        "email": user.email,
                        "password": user.passwordhash,
                        "dpi": employer.dpi,
                        "nombres": employer.nombre,
                        "apellidos": employer.apellido,
                        "telefono": employer.telefono,
                        "edad": str(employer.edad),
                        "nit": employer.nit,
                        "rol": role
                    },
                    status_code=200
                )
            
            return RegisterResponse(
                success=False,
                message="No se encontró el usuario",
                status_code=404
            )

        except Exception as e:
            await db.rollback()
            print(f"Error completo: {repr(e)}")
            return RegisterResponse(
                success=False,
                message="Error interno del servidor",
                status_code=500
            )
        
    @staticmethod
    async def deleteUser(db: AsyncSession, userData: DeleteUser) -> RegisterResponse:

        try:
            
            findClientResult = await db.execute(select(Cliente).where(Cliente.dpi == userData.dpi))
            client = findClientResult.scalars().first()

            if client:

                userResult = await db.execute(update(User).where(User.usuarioid == client.usuario_id).values(estado="inactivo"))

                await db.commit()
                
                return RegisterResponse(
                    success=True,
                    message="Usuario desactivado",
                    status_code=200
                )

            findEmployerResult = await db.execute(select(Empleado).where(Empleado.dpi == userData.dpi))
            employer = findEmployerResult.scalars().first()

            if employer:

                userResult = await db.execute(update(User).where(User.usuarioid == employer.usuario_id).values(estado="inactivo"))

                await db.commit()
                
                return RegisterResponse(
                    success=True,
                    message="Usuario desactivado",
                    status_code=200
                )    
            
            return RegisterResponse(
                success=False,
                message="No se encontró el usuario",
                status_code=404
            )

        except Exception as e:
            await db.rollback()
            print(f"Error completo: {repr(e)}")
            return RegisterResponse(
                success=False,
                message="Error interno del servidor",
                status_code=500
            )
