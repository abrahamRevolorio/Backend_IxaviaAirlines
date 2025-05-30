from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text, update

from .modelReservation import ReservationCreate, ReservationResponse, ReservationResponseList, ReservationInfo
from .schema import Reservation, Sits, Flight, Cliente

from src.auth.modelAuth import TokenData

class ReservationController:

    @staticmethod
    async def createReservationClient(db: AsyncSession, userData: ReservationCreate, current_user: TokenData) -> ReservationResponse:
        try:
            
            existingFlight = await db.execute(select(Flight).where(Flight.vueloid == userData.vuelo_id).where(Flight.estado == 'activo'))

            flight = existingFlight.scalars().first()

            if not flight:
                return ReservationResponse(
                    success=False,
                    message=f'El vuelo con el id {userData.vuelo_id} no existe',
                    status_code=400
                )

            existingSits = await db.execute(select(Sits).where(Sits.asientoid == userData.asiento_id).where(Sits.estado == 'activo'))

            sit = existingSits.scalars().first()

            if not sit:
                return ReservationResponse(
                    success=False,
                    message=f'El asiento con el id {userData.asiento_id} no existe',
                    status_code=400
                )

            ocupadedSits = await db.execute(select(Reservation).where(Reservation.asiento_id == userData.asiento_id).where(Reservation.vuelo_id == userData.vuelo_id))

            sits = ocupadedSits.scalars().first()

            if sits:
                return ReservationResponse(
                    success=False,
                    message=f'El asiento con el id {userData.asiento_id} ya esta ocupado',
                    status_code=400
                )
            
            findClient = await db.execute(select(Cliente).where(Cliente.usuario_id == current_user.userId))

            client = findClient.scalars().first()
            
            newReservation = {
                "vuelo_id": userData.vuelo_id,
                "asiento_id": userData.asiento_id,
                "cliente_id": client.clienteid
            }

            await db.execute(text("INSERT INTO reservaciones (asiento_id, vuelo_id, cliente_id) VALUES (:asiento_id, :vuelo_id, :cliente_id)"), newReservation)

            await db.commit()

            return ReservationResponse(
                success=True,
                message="La reserva se ha registrado correctamente",
                reservation_info=newReservation,
                status_code=201
            )

        except Exception as e:
            await db.rollback()
            print(f'Error: {repr(e)}')
            return ReservationResponse(
                success=False,
                message=f'Error al crear el vuelo',
                status_code=400
            )
        
    @staticmethod
    async def getReservationClient(db: AsyncSession, current_user: TokenData) -> ReservationResponseList:
        try:

            findClient = await db.execute(select(Cliente).where(Cliente.usuario_id == current_user.userId))

            client = findClient.scalars().first()

            findReservationClientToken = await db.execute(select(Reservation).where(Reservation.cliente_id == client.clienteid))

            reservationClientToken = findReservationClientToken.scalars().all()

            if not reservationClientToken:
                return ReservationResponseList(
                    success=False,
                    message=f'No tienes reservaciones activas',
                    status_code=400
                )
            
            reservationClientTokenDict = [{
                "vuelo_id": str(reservation.vuelo_id),
                "asiento_id": str(reservation.asiento_id),
                "cliente_id": str(reservation.cliente_id)
            } for reservation in reservationClientToken]

            return ReservationResponseList(
                success=True,
                message="Consulta exitosa",
                reservation_info=reservationClientTokenDict,
                status_code=200
            )

        except Exception as e:
            await db.rollback()
            print(f'Error: {repr(e)}')
            return ReservationResponseList(
                success=False,
                message=f'Error al obtener la reserva',
                status_code=400
            )