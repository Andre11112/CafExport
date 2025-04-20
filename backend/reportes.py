from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from datetime import datetime
import os
from backend.database import DatabaseConnection

class ReporteFacturas:
    def __init__(self):
        self.db = DatabaseConnection()
        self.styles = getSampleStyleSheet()
        
    def generar_factura_venta(self, venta_id):
        try:
            # Crear directorio si no existe
            if not os.path.exists('facturas'):
                os.makedirs('facturas')
                
            # Obtener datos de la venta
            with self.db.connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT v.*, c.nombre_empresa, c.nit, c.telefono, c.email, c.direccion,
                               p.monto, p.fecha_pago, p.metodo_pago
                        FROM ventas v
                        JOIN clientes c ON v.cliente_id = c.id
                        LEFT JOIN pagos p ON v.id = p.venta_id
                        WHERE v.id = %s
                    """, (venta_id,))
                    venta = cur.fetchone()
                    
            if not venta:
                return None
                
            # Crear el PDF
            fecha = venta['fecha_venta'].strftime('%Y%m%d')
            filename = f'facturas/factura_venta_{venta_id}_{fecha}.pdf'
            doc = SimpleDocTemplate(filename, pagesize=letter)
            elements = []
            
            # Estilos
            title_style = self.styles['Title']
            normal_style = self.styles['Normal']
            
            # Título
            elements.append(Paragraph("CafeExport S.A.", title_style))
            elements.append(Paragraph("Factura de Venta", title_style))
            elements.append(Spacer(1, 12))
            
            # Información de la factura
            factura_data = [
                ["Número de Factura:", str(venta_id)],
                ["Fecha:", venta['fecha_venta'].strftime('%d/%m/%Y')],
                ["Cliente:", venta['nombre_empresa']],
                ["NIT:", venta['nit']],
                ["Teléfono:", venta['telefono']],
                ["Email:", venta['email']],
                ["Dirección:", venta['direccion']]
            ]
            
            factura_table = Table(factura_data, colWidths=[150, 300])
            factura_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.grey),
            ]))
            elements.append(factura_table)
            elements.append(Spacer(1, 20))
            
            # Detalles de la venta
            venta_data = [
                ["Cantidad (kg)", "Precio por kg", "Total"],
                [f"{venta['cantidad_kg']:.2f}", f"${venta['precio_kg']:.2f}", f"${venta['total']:.2f}"]
            ]
            
            venta_table = Table(venta_data, colWidths=[150, 150, 150])
            venta_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, 1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, 1), colors.black),
                ('FONTNAME', (0, 1), (-1, 1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, 1), 10),
            ]))
            elements.append(venta_table)
            elements.append(Spacer(1, 20))
            
            # Estado de pago
            estado = "Pagado" if venta['estado_cobro'] == 'pagado' else "Pendiente"
            elements.append(Paragraph(f"Estado de pago: {estado}", normal_style))
            
            if venta['monto']:
                elements.append(Paragraph(f"Monto pagado: ${venta['monto']:.2f}", normal_style))
                elements.append(Paragraph(f"Fecha de pago: {venta['fecha_pago'].strftime('%d/%m/%Y')}", normal_style))
                elements.append(Paragraph(f"Método de pago: {venta['metodo_pago']}", normal_style))
            
            # Generar el PDF
            doc.build(elements)
            return filename
            
        except Exception as e:
            print(f"Error al generar factura de venta: {str(e)}")
            return None
            
    def generar_factura_compra(self, compra_id):
        try:
            # Crear directorio si no existe
            if not os.path.exists('facturas'):
                os.makedirs('facturas')
                
            # Obtener datos de la compra
            with self.db.connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT c.*, p.nombre, p.apellido, p.documento_identidad, p.telefono, p.direccion,
                               p.monto, p.fecha_pago, p.metodo_pago
                        FROM compras c
                        JOIN proveedores p ON c.proveedor_id = p.id
                        LEFT JOIN pagos p ON c.id = p.compra_id
                        WHERE c.id = %s
                    """, (compra_id,))
                    compra = cur.fetchone()
                    
            if not compra:
                return None
                
            # Crear el PDF
            fecha = compra['fecha_compra'].strftime('%Y%m%d')
            filename = f'facturas/factura_compra_{compra_id}_{fecha}.pdf'
            doc = SimpleDocTemplate(filename, pagesize=letter)
            elements = []
            
            # Estilos
            title_style = self.styles['Title']
            normal_style = self.styles['Normal']
            
            # Título
            elements.append(Paragraph("CafeExport S.A.", title_style))
            elements.append(Paragraph("Factura de Compra", title_style))
            elements.append(Spacer(1, 12))
            
            # Información de la factura
            factura_data = [
                ["Número de Factura:", str(compra_id)],
                ["Fecha:", compra['fecha_compra'].strftime('%d/%m/%Y')],
                ["Proveedor:", f"{compra['nombre']} {compra['apellido']}"],
                ["Documento:", compra['documento_identidad']],
                ["Teléfono:", compra['telefono']],
                ["Dirección:", compra['direccion']]
            ]
            
            factura_table = Table(factura_data, colWidths=[150, 300])
            factura_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 12),
                ('TEXTCOLOR', (0, 0), (0, -1), colors.grey),
            ]))
            elements.append(factura_table)
            elements.append(Spacer(1, 20))
            
            # Detalles de la compra
            compra_data = [
                ["Cantidad (kg)", "Precio por kg", "Total"],
                [f"{compra['cantidad_kg']:.2f}", f"${compra['precio_kg']:.2f}", f"${compra['total']:.2f}"]
            ]
            
            compra_table = Table(compra_data, colWidths=[150, 150, 150])
            compra_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
                ('BACKGROUND', (0, 1), (-1, 1), colors.beige),
                ('TEXTCOLOR', (0, 1), (-1, 1), colors.black),
                ('FONTNAME', (0, 1), (-1, 1), 'Helvetica'),
                ('FONTSIZE', (0, 1), (-1, 1), 10),
            ]))
            elements.append(compra_table)
            elements.append(Spacer(1, 20))
            
            # Estado de pago
            estado = "Pagado" if compra['estado_pago'] == 'pagado' else "Pendiente"
            elements.append(Paragraph(f"Estado de pago: {estado}", normal_style))
            
            if compra['monto']:
                elements.append(Paragraph(f"Monto pagado: ${compra['monto']:.2f}", normal_style))
                elements.append(Paragraph(f"Fecha de pago: {compra['fecha_pago'].strftime('%d/%m/%Y')}", normal_style))
                elements.append(Paragraph(f"Método de pago: {compra['metodo_pago']}", normal_style))
            
            # Generar el PDF
            doc.build(elements)
            return filename
            
        except Exception as e:
            print(f"Error al generar factura de compra: {str(e)}")
            return None 