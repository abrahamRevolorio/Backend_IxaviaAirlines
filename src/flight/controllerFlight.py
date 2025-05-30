from datetime import date, time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import text, update
from datetime import datetime
import json

from .modelFlight import FlightCreate, FlightResponse, FlightUpdate, FlightResponseList
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