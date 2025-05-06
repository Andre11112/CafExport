from fastapi import APIRouter, HTTPException
from datetime import datetime
from backend.database import DatabaseConnection
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dashboard", tags=["dashboard"])

@router.get("/kpis")
def obtener_kpis(anio: int = None, mes: int = None):
    """
    Devuelve los KPIs principales para el panel de control.
    Si no se especifica año/mes, usa el último cierre disponible.
    """
    db = DatabaseConnection()
    try:
        conn = db.connect()
        cur = conn.cursor()

        logger.info("[DEBUG] Iniciando consulta de KPIs")
        # Si no se especifica año/mes, buscar el último cierre
        if anio is None or mes is None:
            logger.info("[DEBUG] No se especificó año/mes, buscando el último cierre contable...")
            cur.execute("""
                SELECT anio, mes
                FROM cierres_contables
                ORDER BY anio DESC, mes DESC
                LIMIT 1
            """)
            row = cur.fetchone()
            logger.info(f"[DEBUG] Resultado de último cierre: {row}")
            if not row:
                logger.error("[ERROR] No hay cierres contables registrados en la base de datos.")
                raise HTTPException(status_code=404, detail="No hay cierres contables registrados")
            anio, mes = row['anio'], row['mes']

        logger.info(f"[DEBUG] Consultando cierre para año={anio}, mes={mes}")
        # Obtener los datos del cierre
        cur.execute("""
            SELECT total_ventas, total_compras, utilidad
            FROM cierres_contables
            WHERE anio = %s AND mes = %s
        """, (anio, mes))
        cierre = cur.fetchone()
        logger.info(f"[DEBUG] Resultado de cierre: {cierre}")
        if not cierre:
            logger.error(f"[ERROR] No hay cierre para el año {anio} y mes {mes}")
            raise HTTPException(status_code=404, detail="No hay cierre para ese mes/año")

        total_ventas = float(cierre['total_ventas'])
        total_compras = float(cierre['total_compras'])
        utilidad = float(cierre['utilidad'])
        margen_lote = round((utilidad / total_ventas) * 100, 2) if total_ventas else 0

        logger.info(f"[DEBUG] KPIs calculados: utilidad_neta={utilidad}, volumen_ventas={total_ventas}, margen_lote={margen_lote}")
        return {
            "anio": anio,
            "mes": mes,
            "utilidad_neta": utilidad,
            "volumen_ventas": total_ventas,
            "margen_lote": margen_lote
        }
    except Exception as e:
        logger.error(f"[ERROR] Excepción en obtener_kpis: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        if 'cur' in locals():
            cur.close()
        if 'conn' in locals():
            conn.close()
