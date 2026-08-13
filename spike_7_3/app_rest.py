from fastapi import FastAPI, HTTPException, status, Query
from typing import List, Optional
from datetime import datetime
from schemas import VehiculoCreate, VehiculoUpdate, VehiculoResponse, EstadoVehiculo

app = FastAPI(
    title="LogiTrack Fleet API — Spike 7.3",
    description="API RESTful para gestión de vehículos con validación estricta de esquemas Pydantic",
    version="1.0.0"
)

# Base de datos simulada en memoria
db_vehiculos = {}
id_counter = 1

@app.post(
    "/api/v1/vehiculos",
    response_model=VehiculoResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo vehículo"
)
def crear_vehiculo(vehiculo: VehiculoCreate):
    global id_counter
    # Validar duplicados por placa
    for v in db_vehiculos.values():
        if v["placa"] == vehiculo.placa:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Ya existe un vehículo registrado con la placa '{vehiculo.placa}'"
            )

    nuevo_vehiculo = {
        "id": id_counter,
        "placa": vehiculo.placa,
        "modelo": vehiculo.modelo,
        "capacidad_kg": vehiculo.capacidad_kg,
        "estado": vehiculo.estado.value,
        "fecha_registro": datetime.now().isoformat()
    }
    db_vehiculos[id_counter] = nuevo_vehiculo
    id_counter += 1
    return nuevo_vehiculo

@app.get(
    "/api/v1/vehiculos",
    response_model=List[VehiculoResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar vehículos registrados"
)
def listar_vehiculos(
    estado: Optional[EstadoVehiculo] = Query(None, description="Filtrar por estado operativo"),
    limit: int = Query(10, ge=1, le=100)
):
    resultado = list(db_vehiculos.values())
    if estado:
        resultado = [v for v in resultado if v["estado"] == estado.value]
    return resultado[:limit]

@app.get(
    "/api/v1/vehiculos/{vehiculo_id}",
    response_model=VehiculoResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener un vehículo por ID"
)
def obtener_vehiculo(vehiculo_id: int):
    if vehiculo_id not in db_vehiculos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehículo con ID {vehiculo_id} no encontrado"
        )
    return db_vehiculos[vehiculo_id]

@app.put(
    "/api/v1/vehiculos/{vehiculo_id}",
    response_model=VehiculoResponse,
    status_code=status.HTTP_200_OK,
    summary="Actualizar un vehículo parcialmente o completamente"
)
def actualizar_vehiculo(vehiculo_id: int, datos: VehiculoUpdate):
    if vehiculo_id not in db_vehiculos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehículo con ID {vehiculo_id} no encontrado"
        )
    
    vehiculo_actual = db_vehiculos[vehiculo_id]
    update_data = datos.model_dump(exclude_unset=True)
    
    for key, value in update_data.items():
        if value is not None:
            vehiculo_actual[key] = value.value if isinstance(value, Enum) else value

    db_vehiculos[vehiculo_id] = vehiculo_actual
    return vehiculo_actual

@app.delete(
    "/api/v1/vehiculos/{vehiculo_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar un vehículo de la flota"
)
def eliminar_vehiculo(vehiculo_id: int):
    if vehiculo_id not in db_vehiculos:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Vehículo con ID {vehiculo_id} no encontrado"
        )
    del db_vehiculos[vehiculo_id]
    return None

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="error")
