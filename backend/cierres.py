from datetime import datetime, date, timedelta
from typing import Optional
from .database import DatabaseConnection
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import os
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from decimal import Decimal

class CierreContable:
    def __init__(self):
        self.db = DatabaseConnection()
        self.styles = getSampleStyleSheet()

    def _convert_to_float(self, value) -> float:
        """Convierte un valor a float de manera segura"""
        if isinstance(value, Decimal):
            return float(value)
        if value is None:
            return 0.0
        return float(value)

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
        try:
            print(f"[DEBUG] Calculando cierre para año={anio}, mes={mes}")
            fecha_inicio = date(anio, mes, 1)
            if mes == 12:
                fecha_fin = date(anio + 1, 1, 1)
            else:
                fecha_fin = date(anio, mes + 1, 1)
            
            print(f"[DEBUG] Rango de fechas: {fecha_inicio} a {fecha_fin}")
            
            with self.db.connect() as conn:
                with conn.cursor() as cur:
                    # Total ventas
                    cur.execute('''
                        SELECT 
                            COALESCE(SUM(total), 0) as total_ventas,
                            COALESCE(SUM(cantidad_kg), 0) as kg_vendidos,
                            COALESCE(AVG(precio_kg), 0) as prom_venta
                        FROM ventas
                        WHERE fecha_venta >= %s AND fecha_venta < %s
                    ''', (fecha_inicio, fecha_fin))
                    row_ventas = cur.fetchone()
                    print(f"[DEBUG] Resultados ventas: {row_ventas}")
                    total_ventas = self._convert_to_float(row_ventas['total_ventas'])
                    kg_vendidos = self._convert_to_float(row_ventas['kg_vendidos'])
                    prom_venta = self._convert_to_float(row_ventas['prom_venta'])

                    # Total compras
                    cur.execute('''
                        SELECT 
                            COALESCE(SUM(total), 0) as total_compras,
                            COALESCE(SUM(cantidad_kg), 0) as kg_comprados,
                            COALESCE(AVG(precio_kg), 0) as prom_compra
                        FROM compras
                        WHERE fecha_compra >= %s AND fecha_compra < %s
                    ''', (fecha_inicio, fecha_fin))
                    row_compras = cur.fetchone()
                    print(f"[DEBUG] Resultados compras: {row_compras}")
                    total_compras = self._convert_to_float(row_compras['total_compras'])
                    kg_comprados = self._convert_to_float(row_compras['kg_comprados'])
                    prom_compra = self._convert_to_float(row_compras['prom_compra'])

                    utilidad = total_ventas - total_compras

                    # Facturas emitidas (ventas)
                    cur.execute('''
                        SELECT COUNT(*) as total
                        FROM facturas 
                        WHERE fecha >= %s AND fecha < %s AND total > 0
                    ''', (fecha_inicio, fecha_fin))
                    facturas_ventas = int(cur.fetchone()['total'] or 0)

                    # Facturas recibidas (compras)
                    cur.execute('''
                        SELECT COUNT(*) as total
                        FROM facturas 
                        WHERE fecha >= %s AND fecha < %s AND total < 0
                    ''', (fecha_inicio, fecha_fin))
                    facturas_compras = int(cur.fetchone()['total'] or 0)

                    # Cobros de ventas
                    cur.execute('''
                        SELECT COALESCE(SUM(monto), 0) as total
                        FROM cobros_ventas 
                        WHERE fecha_cobro >= %s AND fecha_cobro < %s
                    ''', (fecha_inicio, fecha_fin))
                    cobros = self._convert_to_float(cur.fetchone()['total'])

                    # Pagos de compras
                    cur.execute('''
                        SELECT COALESCE(SUM(monto), 0) as total
                        FROM pagos_compras 
                        WHERE fecha_pago >= %s AND fecha_pago < %s
                    ''', (fecha_inicio, fecha_fin))
                    pagos = self._convert_to_float(cur.fetchone()['total'])

            print(f"[DEBUG] Valores calculados:")
            print(f"Total ventas: {total_ventas}")
            print(f"Total compras: {total_compras}")
            print(f"Utilidad: {utilidad}")

            # Validar que los valores sean válidos
            if total_ventas < 0 or total_compras < 0:
                raise ValueError("Los totales no pueden ser negativos")

            resultado = {
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
            print(f"[DEBUG] Diccionario resultado: {resultado}")
            return resultado
        except Exception as e:
            print(f"[ERROR] Error en calcular_cierre_mes: {str(e)}")
            raise

    def generar_pdf_cierre(self, cierre: dict, output_dir: str = 'cierres') -> str:
        try:
            print(f"[DEBUG] Iniciando generación de PDF con datos: {cierre}")
            
            # Validar que los datos del cierre sean válidos
            if not isinstance(cierre, dict):
                raise ValueError("Los datos del cierre deben ser un diccionario")
            
            required_fields = ['anio', 'mes', 'total_ventas', 'total_compras', 'utilidad']
            for field in required_fields:
                if field not in cierre:
                    raise ValueError(f"Falta el campo requerido: {field}")
                if not isinstance(cierre[field], (int, float)):
                    raise ValueError(f"El campo {field} debe ser un número")

            # Crear directorio si no existe
            current_dir = os.path.dirname(os.path.abspath(__file__))
            output_dir = os.path.join(os.path.dirname(current_dir), output_dir)
            print(f"[DEBUG] Directorio de salida: {output_dir}")
            
            if not os.path.exists(output_dir):
                print(f"[DEBUG] Creando directorio: {output_dir}")
                os.makedirs(output_dir)

            # Generar nombre del archivo con el formato: cierre_YYYY_MM.pdf
            nombre_pdf = f"cierre_{cierre['anio']}_{cierre['mes']:02d}.pdf"
            pdf_path = os.path.join(output_dir, nombre_pdf)
            print(f"[DEBUG] Ruta del PDF: {pdf_path}")

            doc = SimpleDocTemplate(pdf_path, pagesize=letter)
            elements = []
            
            # Título
            elements.append(Paragraph("CafeExport S.A.", self.styles['Title']))
            elements.append(Paragraph("Cierre Contable Mensual", self.styles['Title']))
            elements.append(Spacer(1, 12))

            # Información del cierre
            cierre_data = [
                ["Año:", str(cierre['anio'])],
                ["Mes:", f"{cierre['mes']:02d}"],
                ["Fecha de generación:", datetime.now().strftime('%d/%m/%Y %H:%M')]
            ]
            cierre_table = Table(cierre_data, colWidths=[150, 300])
            cierre_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.grey),
            ]))
            elements.append(cierre_table)
            elements.append(Spacer(1, 20))

            # Resumen financiero
            resumen_data = [
                ["Concepto", "Valor"],
                ["Total Ventas", f"${cierre['total_ventas']:,.2f}"],
                ["Total Compras", f"${cierre['total_compras']:,.2f}"],
                ["Utilidad", f"${cierre['utilidad']:,.2f}"]
            ]
            resumen_table = Table(resumen_data, colWidths=[300, 150])
            resumen_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
            ]))
            elements.append(resumen_table)
            elements.append(Spacer(1, 20))

            # Detalles de operaciones
            detalles_data = [
                ["Concepto", "Valor"],
                ["Kg Vendidos", f"{cierre['kg_vendidos']:,.2f} kg"],
                ["Precio Promedio Venta", f"${cierre['prom_venta']:.2f}/kg"],
                ["Kg Comprados", f"{cierre['kg_comprados']:,.2f} kg"],
                ["Precio Promedio Compra", f"${cierre['prom_compra']:.2f}/kg"],
                ["Facturas Emitidas", str(cierre['facturas_ventas'])],
                ["Facturas Recibidas", str(cierre['facturas_compras'])],
                ["Total Cobros", f"${cierre['cobros']:,.2f}"],
                ["Total Pagos", f"${cierre['pagos']:,.2f}"]
            ]
            detalles_table = Table(detalles_data, colWidths=[300, 150])
            detalles_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, -1), colors.black),
                ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, -1), 10),
            ]))
            elements.append(detalles_table)

            print("[DEBUG] Construyendo PDF...")
            doc.build(elements)
            print(f"[DEBUG] PDF generado exitosamente en: {pdf_path}")
            return pdf_path
        except Exception as e:
            print(f"[ERROR] Error en generar_pdf_cierre: {str(e)}")
            raise

    def registrar_cierre(self, anio: int, mes: int, usuario_id: Optional[int] = None) -> dict:
        cierre = self.calcular_cierre_mes(anio, mes)
        self.generar_pdf_cierre(cierre)
        with self.db.connect() as conn:
            with conn.cursor() as cur:
                cur.execute('''
                    INSERT INTO cierres_contables (mes, anio, total_ventas, total_compras, utilidad, usuario_id)
                    VALUES (%s, %s, %s, %s, %s, %s)
                    RETURNING id, fecha_cierre
                ''', (mes, anio, cierre['total_ventas'], cierre['total_compras'], cierre['utilidad'], usuario_id))
                result = cur.fetchone()
                conn.commit()
        cierre['id'] = result[0]
        cierre['fecha_cierre'] = result[1]
        return cierre

    def obtener_pdf_cierre(self, anio: int, mes: int) -> Optional[str]:
        # Ya no se usa, pero si se requiere, solo calcula la ruta
        current_dir = os.path.dirname(os.path.abspath(__file__))
        output_dir = os.path.join(os.path.dirname(current_dir), 'cierres de mes')
        nombre_pdf = f"cierre_{anio}_{mes:02d}.pdf"
        pdf_path = os.path.join(output_dir, nombre_pdf)
        if os.path.exists(pdf_path):
            return pdf_path
        return None

    def generar_pdf_cierre_por_id(self, cierre_id: int) -> str:
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cur:
                    cur.execute('''
                        SELECT anio, mes FROM cierres_contables WHERE id = %s
                    ''', (cierre_id,))
                    cierre = cur.fetchone()
                    if not cierre:
                        print(f"No se encontró el cierre con ID {cierre_id}")
                        return None
                    cierre_dict = self.calcular_cierre_mes(cierre['anio'], cierre['mes'])
                    # Siempre generar el PDF, aunque ya exista
                    pdf_path = self.generar_pdf_cierre(cierre_dict)
                    print(f"PDF generado para cierre {cierre_id} en: {pdf_path}")
                    return pdf_path
        except Exception as e:
            print(f"Error al generar PDF del cierre {cierre_id}: {str(e)}")
            return None

# Para uso automático mensual, puedes usar APScheduler o un cron externo para llamar a registrar_cierre() 