from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import FileResponse
from datetime import datetime
from ..cierres import CierreContable
import os
from backend.database import DatabaseConnection
import logging
import psycopg2

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/cierres", tags=["cierres"])
cierre_manager = CierreContable()

@router.post("/generar/{anio}/{mes}")
def generar_cierre(anio: int, mes: int, usuario_id: int = Query(None)):
    try:
        cierre = cierre_manager.registrar_cierre(anio, mes, usuario_id)
        # Devolver todas las métricas relevantes
        return {
            "message": "Cierre generado",
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

@router.get("/pdf/por-id/{cierre_id}")
def generar_pdf_cierre_por_id(cierre_id: int):
    logger.info(f"[BACKEND] Iniciando generación de PDF para cierre_id: {cierre_id}")
    try:
        # Validar que el ID sea un número positivo
        if not isinstance(cierre_id, int) or cierre_id <= 0:
            logger.error(f"[BACKEND] ID inválido: {cierre_id}")
            raise HTTPException(status_code=400, detail="ID de cierre inválido")

        # Obtener año y mes directamente de la base de datos
        with cierre_manager.db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute('SELECT anio, mes FROM cierres_contables WHERE id = %s', (cierre_id,))
                cierre = cur.fetchone()
                if not cierre:
                    logger.error(f"[BACKEND] No se encontró cierre con ID: {cierre_id}")
                    raise HTTPException(status_code=404, detail="No se encontró el cierre con ese ID")
                
                logger.info(f"[BACKEND] Cierre encontrado: año={cierre['anio']}, mes={cierre['mes']}")
                # Calcular los datos y generar el PDF SIEMPRE
                cierre_dict = cierre_manager.calcular_cierre_mes(cierre['anio'], cierre['mes'])
                pdf_path = cierre_manager.generar_pdf_cierre(cierre_dict)
                
                if not os.path.exists(pdf_path):
                    logger.error(f"[BACKEND] PDF no generado en ruta: {pdf_path}")
                    raise HTTPException(status_code=500, detail="Error al generar el PDF")
                
                logger.info(f"[BACKEND] PDF generado exitosamente en: {pdf_path}")
                return FileResponse(
                    pdf_path,
                    media_type='application/pdf',
                    filename=f"cierre_{cierre_id}.pdf"
                )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"[BACKEND] Error al generar PDF del cierre {cierre_id}: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al generar el PDF: {str(e)}"
        )

@router.get("/pdf/{anio}/{mes}")
def descargar_pdf_cierre(anio: int, mes: int):
    try:
        pdf_path = cierre_manager.obtener_pdf_cierre(anio, mes)
        if pdf_path and os.path.exists(pdf_path):
            return FileResponse(
                pdf_path,
                media_type='application/pdf',
                filename=f"cierre_{anio}_{mes:02d}.pdf"
            )
        else:
            raise HTTPException(
                status_code=404,
                detail="PDF no encontrado"
            )
    except Exception as e:
        logger.error(f"Error al descargar PDF: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al descargar el PDF: {str(e)}"
        )

@router.get("/historico/{anio}/{mes}")
def obtener_cierre_historico(anio: int, mes: int):
    try:
        db = DatabaseConnection()
        conn = db.connect()
        cur = conn.cursor()
        try:
            cur.execute("""
                SELECT 
                    total_ventas, 
                    total_compras, 
                    utilidad, 
                    usuario_id,
                    fecha_cierre
                FROM cierres_contables
                WHERE anio = %s AND mes = %s
            """, (anio, mes))
            row = cur.fetchone()
            if not row:
                logger.warning(f"No existe cierre para {anio}-{mes}")
                raise HTTPException(
                    status_code=404, 
                    detail="No existe cierre para ese mes/año"
                )
            return {
                "total_ventas": float(row[0]),
                "total_compras": float(row[1]),
                "utilidad": float(row[2]),
                "usuario_id": row[3],
                "fecha_cierre": row[4]
            }
        except psycopg2.Error as e:
            logger.error(f"Error de base de datos: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error de base de datos: {str(e)}"
            )
        finally:
            cur.close()
            conn.close()
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error al obtener cierre histórico: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener el cierre: {str(e)}"
        )

@router.get("/historico/lista")
def listar_cierres():
    try:
        db = DatabaseConnection()
        conn = db.connect()
        cur = conn.cursor()
        
        try:
            # Consulta directa a la tabla cierres_contables
            cur.execute("""
                SELECT anio, mes 
                FROM cierres_contables 
                ORDER BY anio DESC, mes DESC
            """)
            
            rows = cur.fetchall()
            logger.info(f"Cierres encontrados: {len(rows)}")
            
            # Convertir los resultados a una lista de diccionarios
            cierres = []
            for row in rows:
                cierres.append({
                    "anio": int(row[0]),
                    "mes": int(row[1])
                })
            
            return cierres
            
        except psycopg2.Error as e:
            logger.error(f"Error de base de datos: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Error de base de datos: {str(e)}"
            )
        finally:
            cur.close()
            conn.close()
            
    except Exception as e:
        logger.error(f"Error al listar cierres: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al obtener la lista de cierres: {str(e)}"
        ) 