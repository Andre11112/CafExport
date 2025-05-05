from fastapi import APIRouter, HTTPException
from typing import List, Optional
from datetime import datetime
from ..contratos import (
    Contrato,
    DetalleContrato,
    crear_contrato,
    obtener_contrato,
    listar_contratos,
    actualizar_estado_contrato
)

router = APIRouter(prefix="/contratos", tags=["contratos"])

@router.post("/", response_model=int)
async def crear_nuevo_contrato(contrato: Contrato, detalles: List[DetalleContrato]):
    try:
        contrato_id = crear_contrato(contrato, detalles)
        return contrato_id
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/{contrato_id}", response_model=tuple[Contrato, List[DetalleContrato]])
async def obtener_contrato_por_id(contrato_id: int):
    try:
        return obtener_contrato(contrato_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/", response_model=List[Contrato])
async def listar_todos_contratos(estado: Optional[str] = None):
    try:
        return listar_contratos(estado)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/{contrato_id}/estado")
async def actualizar_estado(contrato_id: int, nuevo_estado: str):
    try:
        actualizar_estado_contrato(contrato_id, nuevo_estado)
        return {"message": "Estado actualizado correctamente"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) 