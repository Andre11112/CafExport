from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from datetime import datetime
from ..cierres import CierreContable
import os

router = APIRouter(prefix="/cierres", tags=["cierres"])
cierre_manager = CierreContable()

@router.post("/generar/{anio}/{mes}")
def generar_cierre(anio: int, mes: int, usuario_id: int = Query(None)):
    try:
        cierre = cierre_manager.registrar_cierre(anio, mes, usuario_id)
        # Devolver todas las métricas relevantes
        return {
            "message": "Cierre generado",
            "pdf_path": cierre['pdf_path'],
            "total_ventas": cierre['total_ventas'],
            "total_compras": cierre['total_compras'],
            "utilidad": cierre['utilidad'],
            "kg_vendidos": cierre['kg_vendidos'],
            "kg_comprados": cierre['kg_comprados'],
            "prom_venta": cierre['prom_venta'],
            "prom_compra": cierre['prom_compra'],
            "facturas_ventas": cierre['facturas_ventas'],
            "facturas_compras": cierre['facturas_compras'],
            "cobros": cierre['cobros'],
            "pagos": cierre['pagos'],
            "anio": cierre['anio'],
            "mes": cierre['mes']
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/pdf/{anio}/{mes}")
def descargar_pdf_cierre(anio: int, mes: int):
    pdf_path = cierre_manager.obtener_pdf_cierre(anio, mes)
    if pdf_path and os.path.exists(pdf_path):
        return FileResponse(pdf_path, media_type='application/pdf', filename=pdf_path.split('/')[-1])
    else:
        raise HTTPException(status_code=404, detail="PDF no encontrado") 