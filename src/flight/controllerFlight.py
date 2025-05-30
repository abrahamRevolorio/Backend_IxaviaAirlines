from datetime import date, time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text, update
from datetime import datetime
import json

from .modelFlight import FlightCreate, FlightResponse, FlightUpdate, FlightResponseList, FlightDelete
from .schemas import Flight

from src.auth.modelAuth import TokenData

class FlightController:

    @staticmethod
    async def createFlight(db: AsyncSession, userData: FlightCreate) -> FlightResponse:
        try:

            existingFecha = await db.execute(
                select(Flight).where(Flight.fecha == userData.fecha)
            )
            vuelosMismaFecha = existingFecha.scalars().all()

            for vuelo in vuelosMismaFecha:
                if vuelo.destino_id == userData.destino_id:
                    if vuelo.avion_id == userData.avion_id:
                        return FlightResponse(
                            success=False,
                            message=f'Ya existe un vuelo con el mismo avión y destino en la misma fecha',
                            status_code=400
                        )
                    
            

            newFlight = {
                "fecha": userData.fecha,
                "hora_salida": datetime.strptime(userData.hora_salida, "%H:%M:%S").time(),
                "hora_llegada": datetime.strptime(userData.hora_llegada, "%H:%M:%S").time(),
                "destino_id": userData.destino_id,
                "avion_id": userData.avion_id
            }

            await db.execute(
                text("""
                     
                    INSERT INTO vuelos (fecha, horasalida, horallegada, destino_id, avion_id)
                    VALUES (:fecha, :hora_salida, :hora_llegada, :destino_id, :avion_id)

                """), newFlight
            )

            await db.commit()

            return FlightResponse(
                success=True,
                message=f'El vuelo se ha registrado correctamente',
                flight_info=newFlight,
                status_code=201
            )
            
        except Exception as e:
            await db.rollback()
            print(f'Error: {repr(e)}')
            return FlightResponse(
                success=False,
                message=f'Error al crear el vuelo',
                status_code=400
            )
        
    @staticmethod
    async def viewFlights(db: AsyncSession) -> FlightResponseList:
        try:

            result = await db.execute(select(Flight).where(Flight.estado == 'activo'))

            flights = result.scalars().all()

            flightDict = [{
                "id": str(flight.vueloid),
                "fecha": str(flight.fecha),
                "hora_salida": str(flight.horasalida),
                "hora_llegada": str(flight.horallegada),
                "destino_id": str(flight.destino_id),
                "avion_id": str(flight.avion_id)
            } for flight in flights]

            return FlightResponseList(
                success=True,
                message='Consulta exitosa',
                status_code=200,
                flights_info=flightDict
            )

        except Exception as e:
            await db.rollback()
            print(f'Error: {repr(e)}')
            return FlightResponseList(
                success=False,
                message=f'Error interno del servidor',
                status_code=500
            )
        
        
    @staticmethod
    async def viewFlightsToPeten(db: AsyncSession) -> FlightResponseList:
        try:

            result = await db.execute(select(Flight).where(Flight.estado == 'activo').where(Flight.destino_id == 2))

            flights = result.scalars().all()

            flightDict = [{
                "id": str(flight.vueloid),
                "fecha": str(flight.fecha),
                "hora_salida": str(flight.horasalida),
                "hora_llegada": str(flight.horallegada),
                "destino_id": str(flight.destino_id),
                "avion_id": str(flight.avion_id)
            } for flight in flights]

            return FlightResponseList(
                success=True,
                message='Consulta exitosa',
                status_code=200,
                flights_info=flightDict
            )

        except Exception as e:
            await db.rollback()
            print(f'Error: {repr(e)}')
            return FlightResponseList(
                success=False,
                message=f'Error interno del servidor',
                status_code=500
            )
        
    @staticmethod
    async def viewFlightsToGuatemalaCity(db: AsyncSession) -> FlightResponseList:
        try:

            result = await db.execute(select(Flight).where(Flight.estado == 'activo').where(Flight.destino_id == 1))

            flights = result.scalars().all()

            flightDict = [{
                "id": str(flight.vueloid),
                "fecha": str(flight.fecha),
                "hora_salida": str(flight.horasalida),
                "hora_llegada": str(flight.horallegada),
                "destino_id": str(flight.destino_id),
                "avion_id": str(flight.avion_id)
            } for flight in flights]

            return FlightResponseList(
                success=True,
                message='Consulta exitosa',
                status_code=200,
                flights_info=flightDict
            )

        except Exception as e:
            await db.rollback()
            print(f'Error: {repr(e)}')
            return FlightResponseList(
                success=False,
                message=f'Error interno del servidor',
                status_code=500
            )
        
    @staticmethod
    async def updateFlight(db: AsyncSession, userData: FlightUpdate) -> FlightResponse:
        try:

            existingFlight = await db.execute(select(Flight).where(Flight.vueloid == userData.vueloid))

            flight = existingFlight.scalars().first()

            if not flight:

                return FlightResponse(
                    success=False,
                    message=f'El vuelo con el id {userData.vueloid} no existe',
                    status_code=400
                )
            
            else:

                updates = {}

                fieldsMapping = {

                    'fecha': 'fecha',
                    'hora_salida': 'horasalida',
                    'hora_llegada': 'horallegada',
                    'destino_id': 'destino_id',
                    'avion_id': 'avion_id'

                }

                for field, db_field in fieldsMapping.items():
                    value = getattr(userData, field, None)
                    if value is not None:

                        if field == 'hora_salida' or field == 'hora_llegada':
                            value = datetime.strptime(value, "%H:%M:%S").time()

                        updates[db_field] = value

                if updates:

                    await db.execute(update(Flight).where(Flight.vueloid == userData.vueloid).values(**updates))
                    await db.commit()
            

                    return FlightResponse(
                        success=True,
                        message=f'El vuelo  se ha actualizado correctamente',
                        status_code=200
                    )
                
                else:

                    return FlightResponse(
                        success=False,
                        message=f'No se proporcionaron campos para actualizar',
                        status_code=400
                    )

        except Exception as e:
            await db.rollback()
            print(f"Error completo: {repr(e)}")
            return FlightResponse(
                success=False,
                message="Error interno del servidor",
                status_code=500
            )
        
    @staticmethod
    async def deleteFlight(db: AsyncSession, userData: FlightDelete) -> FlightResponse:
        try:

            existingFlight = await db.execute(select(Flight).where(Flight.vueloid == userData.vueloid))

            flight = existingFlight.scalars().first()

            if not flight:

                return FlightResponse(
                    success=False,
                    message=f'El vuelo con el id {userData.vueloid} no existe',
                    status_code=400
                )
            
            else:

                await db.execute(update (Flight).where(Flight.vueloid == userData.vueloid).values(estado='inactivo'))
                await db.commit()

                return FlightResponse(
                    success=True,
                    message=f'El vuelo se ha eliminado correctamente',
                    status_code=200
                )
    
        except Exception as e:
            await db.rollback()
            print(f"Error completo: {repr(e)}")
            return FlightResponse(
                success=False,
                message="Error interno del servidor",
                status_code=500
            )