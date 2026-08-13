from enum import Enum
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, ConfigDict

class EstadoVehiculo(str, Enum):
    ACTIVO = "ACTIVO"
    EN_TRANSITO = "EN_TRANSITO"
    MANTENIMIENTO = "MANTENIMIENTO"
    INACTIVO = "INACTIVO"

class VehiculoBase(BaseModel):
    placa: str = Field(
        ..., 
        min_length=7, 
        max_length=8, 
        pattern=r"^[A-Z]{3}-\d{3,4}$",
        description="Placa con formato oficial (ej. MXN-1234)"
    )
    modelo: str = Field(..., min_length=2, max_length=50, description="Marca y modelo")
    capacidad_kg: float = Field(..., gt=0, le=50000, description="Capacidad máxima en kilogramos")
    estado: EstadoVehiculo = Field(default=EstadoVehiculo.ACTIVO)

class VehiculoCreate(VehiculoBase):
    pass

class VehiculoUpdate(BaseModel):
    modelo: Optional[str] = Field(None, min_length=2, max_length=50)
    capacidad_kg: Optional[float] = Field(None, gt=0, le=50000)
    estado: Optional[EstadoVehiculo] = None

class VehiculoResponse(VehiculoBase):
    id: int
    fecha_registro: str

    model_config = ConfigDict(from_attributes=True)
