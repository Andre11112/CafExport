from datetime import datetime, date, timedelta
from typing import Optional
from .database import DatabaseConnection
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os

class CierreContable:
    def __init__(self):
        self.db = DatabaseConnection()

    def crear_tabla_cierres(self):
        with self.db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    CREATE TABLE IF NOT EXISTS cierres_contables (
                        id SERIAL PRIMARY KEY,
                        mes INTEGER NOT NULL,
                        anio INTEGER NOT NULL,
                        total_ventas NUMERIC(14,2) NOT NULL,
                        total_compras NUMERIC(14,2) NOT NULL,
                        utilidad NUMERIC(14,2) NOT NULL,
                        fecha_cierre TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        pdf_path TEXT,
                        usuario_id INTEGER REFERENCES usuarios(id)
                    )
                ''')
                conn.commit()

    def calcular_cierre_mes(self, anio: int, mes: int) -> dict:
        fecha_inicio = date(anio, mes, 1)
        if mes == 12:
            fecha_fin = date(anio + 1, 1, 1)
        else:
            fecha_fin = date(anio, mes + 1, 1)
        with self.db.connect() as conn:
            with conn.cursor() as cur:
                # Total ventas
                cur.execute('''
                    SELECT COALESCE(SUM(total), 0), COALESCE(SUM(cantidad_kg), 0), COALESCE(AVG(precio_kg), 0) FROM ventas
                    WHERE fecha_venta >= %s AND fecha_venta < %s
                ''', (fecha_inicio, fecha_fin))
                row_ventas = cur.fetchone()
                total_ventas = float(row_ventas[0])
                kg_vendidos = float(row_ventas[1])
                prom_venta = float(row_ventas[2])
                # Total compras
                cur.execute('''
                    SELECT COALESCE(SUM(total), 0), COALESCE(SUM(cantidad_kg), 0), COALESCE(AVG(precio_kg), 0) FROM compras
                    WHERE fecha_compra >= %s AND fecha_compra < %s
                ''', (fecha_inicio, fecha_fin))
                row_compras = cur.fetchone()
                total_compras = float(row_compras[0])
                kg_comprados = float(row_compras[1])
                prom_compra = float(row_compras[2])
                utilidad = total_ventas - total_compras
                # Facturas emitidas (ventas)
                cur.execute('''SELECT COUNT(*) FROM facturas WHERE fecha >= %s AND fecha < %s AND total > 0''', (fecha_inicio, fecha_fin))
                facturas_ventas = int(cur.fetchone()[0])
                # Facturas recibidas (compras)
                cur.execute('''SELECT COUNT(*) FROM facturas WHERE fecha >= %s AND fecha < %s AND total < 0''', (fecha_inicio, fecha_fin))
                facturas_compras = int(cur.fetchone()[0])
                # Cobros de ventas
                cur.execute('''SELECT COALESCE(SUM(monto),0) FROM cobros_ventas WHERE fecha_cobro >= %s AND fecha_cobro < %s''', (fecha_inicio, fecha_fin))
                cobros = float(cur.fetchone()[0])
                # Pagos de compras
                cur.execute('''SELECT COALESCE(SUM(monto),0) FROM pagos_compras WHERE fecha_pago >= %s AND fecha_pago < %s''', (fecha_inicio, fecha_fin))
                pagos = float(cur.fetchone()[0])
        return {
            'anio': anio,
            'mes': mes,
            'total_ventas': total_ventas,
            'total_compras': total_compras,
            'utilidad': utilidad,
            'kg_vendidos': kg_vendidos,
            'kg_comprados': kg_comprados,
            'prom_venta': prom_venta,
            'prom_compra': prom_compra,
            'facturas_ventas': facturas_ventas,
            'facturas_compras': facturas_compras,
            'cobros': cobros,
            'pagos': pagos
        }

    def generar_pdf_cierre(self, cierre: dict, output_dir: str = 'cierres_pdfs') -> str:
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        nombre_pdf = f"cierre_{cierre['anio']}_{cierre['mes']:02d}.pdf"
        pdf_path = os.path.join(output_dir, nombre_pdf)
        c = canvas.Canvas(pdf_path, pagesize=letter)
        c.setFont("Helvetica-Bold", 18)
        c.drawString(180, 750, "Cierre Contable Mensual")
        c.setFont("Helvetica", 12)
        c.drawString(80, 710, f"Año: {cierre['anio']}  Mes: {cierre['mes']:02d}")
        c.drawString(80, 680, f"Total Ventas: ${cierre['total_ventas']:,.2f}")
        c.drawString(80, 660, f"Total Compras: ${cierre['total_compras']:,.2f}")
        c.drawString(80, 640, f"Utilidad: ${cierre['utilidad']:,.2f}")
        c.drawString(80, 620, f"Vendido: {cierre['kg_vendidos']} kg (Prom: ${cierre['prom_venta']:.2f}/kg)")
        c.drawString(80, 600, f"Comprado: {cierre['kg_comprados']} kg (Prom: ${cierre['prom_compra']:.2f}/kg)")
        c.drawString(80, 580, f"Facturas emitidas: {cierre['facturas_ventas']}")
        c.drawString(80, 560, f"Facturas recibidas: {cierre['facturas_compras']}")
        c.drawString(80, 540, f"Cobros: ${cierre['cobros']:,.2f}")
        c.drawString(80, 520, f"Pagos: ${cierre['pagos']:,.2f}")
        c.setFont("Helvetica-Oblique", 10)
        c.drawString(80, 490, f"Generado el {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        c.save()
        return pdf_path

    def registrar_cierre(self, anio: int, mes: int, usuario_id: Optional[int] = None) -> dict:
        cierre = self.calcular_cierre_mes(anio, mes)
        pdf_path = self.generar_pdf_cierre(cierre)
        with self.db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    INSERT INTO cierres_contables (mes, anio, total_ventas, total_compras, utilidad, pdf_path, usuario_id)
                    VALUES (%s, %s, %s, %s, %s, %s, %s)
                    RETURNING id, fecha_cierre
                ''', (mes, anio, cierre['total_ventas'], cierre['total_compras'], cierre['utilidad'], pdf_path, usuario_id))
                result = cur.fetchone()
                conn.commit()
        cierre['pdf_path'] = pdf_path
        cierre['id'] = result[0]
        cierre['fecha_cierre'] = result[1]
        return cierre

    def obtener_pdf_cierre(self, anio: int, mes: int) -> Optional[str]:
        with self.db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    SELECT pdf_path FROM cierres_contables WHERE anio = %s AND mes = %s
                ''', (anio, mes))
                result = cur.fetchone()
                if result:
                    return result[0]
        return None

# Para uso automático mensual, puedes usar APScheduler o un cron externo para llamar a registrar_cierre() 