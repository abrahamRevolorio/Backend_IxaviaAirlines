from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text, update

from .modelRole import RoleModel, RoleResponse, UpdateRole, DeleteRole
from .schemas import Role

class RoleController:
    @staticmethod
    async def addRole(db: AsyncSession, userData: RoleModel) -> RoleResponse:
        try:

            existingRole = await db.execute(select(Role).where(Role.nombrerol == userData.nombrerol))

            if existingRole.scalars().first():
                return RoleResponse(
                    success=False,
                    message=f'El rol {userData.nombrerol} ya existe',
                    status_code=400
                )
            
            newRole = Role(

                nombrerol=userData.nombrerol,
                estado='activo'

            )

            db.add(newRole)

            await db.flush()

            await db.commit()

            return RoleResponse(
                success=True,
                message=f'El rol {userData.nombrerol} se ha registrado correctamente',
                status_code=201
            )

        except Exception as e:
            await db.rollback()
            print(f'Error: {repr(e)}')
            return RoleResponse(
                success=False,
                message=f'Error interno del servidor',
                status_code=500
            )
        
    @staticmethod
    async def showRoles(db: AsyncSession):
        try:

            result = await db.execute(select(Role).where(Role.estado == 'activo'))

            roles = result.scalars().all()

            roleDict = {str(role.rolid): role.nombrerol for role in roles}

            return RoleResponse(
                success=True,
                message='Consulta exitosa',
                status_code=200,
                roles=roleDict
            )

        except Exception as e:
            await db.rollback()
            print(f'Error: {repr(e)}')
            return RoleResponse(
                success=False,
                message=f'Error interno del servidor',
                status_code=500
            )

    @staticmethod
    async def editRoles(db: AsyncSession, userData: UpdateRole):
        try:
            
            findRole = await db.execute(select(Role).where(Role.rolid == userData.rolid))

            role = findRole.scalars().first()

            if not role:

                return RoleResponse(
                    success=False,
                    message=f'El rol con el id {userData.rolid} no existe',
                    status_code=400
                )
            
            await db.execute(update(Role).where(Role.rolid == userData.rolid).values(nombrerol=userData.nuevonombrerol))

            await db.commit()

            return RoleResponse(
                success=True,
                message=f'El rol con id {userData.rolid} se ha actualizado correctamente',
                status_code=200
            )

        except Exception as e:
            await db.rollback()
            print(f'Error: {repr(e)}')
            return RoleResponse(
                success=False,
                message=f'Error interno del servidor',
                status_code=500
            )

    @staticmethod    
    async def deleteRoles(db: AsyncSession, userData: DeleteRole):
        try:
            findRole = await db.execute(select(Role).where(Role.rolid == userData.rolid))

            role = findRole.scalars().first()

            if not role:

                return RoleResponse(
                    success=False,
                    message=f'El rol con el id {userData.rolid} no existe',
                    status_code=400
                )
            
            await db.execute(update(Role).where(Role.rolid == userData.rolid).values(estado='inactivo'))

            await db.commit()

            return RoleResponse(
                success=True,
                message=f'El rol se ha eliminado correctamente',
                status_code=200
            )
        
        except Exception as e:
            await db.rollback()
            print(f'Error: {repr(e)}')
            return RoleResponse(
                success=False,
                message=f'Error interno del servidor',
                status_code=500
            )