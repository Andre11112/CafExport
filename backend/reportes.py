from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from datetime import datetime
import os
from .database import DatabaseConnection

class ReporteFacturas:
    def __init__(self):
        self.db = DatabaseConnection()
        self.styles = getSampleStyleSheet()
        # Crear directorio de facturas si no existe
        self.facturas_dir = "facturas"
        if not os.path.exists(self.facturas_dir):
            os.makedirs(self.facturas_dir)
        
    def generar_reporte_ventas(self, fecha_inicio=None, fecha_fin=None):
        """Genera un reporte PDF de ventas"""
        try:
            # Crear el documento PDF
            filename = f"reporte_ventas_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            doc = SimpleDocTemplate(filename, pagesize=letter)
            
            # Contenido del documento
            elements = []
            
            # Título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=16,
                spaceAfter=30
            )
            elements.append(Paragraph("Reporte de Ventas", title_style))
            
            # Fechas del reporte
            if fecha_inicio and fecha_fin:
                date_text = f"Período: {fecha_inicio} al {fecha_fin}"
            else:
                date_text = "Período: Todo el tiempo"
            elements.append(Paragraph(date_text, self.styles['Normal']))
            elements.append(Spacer(1, 20))
            
            # Obtener datos de ventas
            with self.db.connect() as conn:
                with conn.cursor() as cur:
                    query = """
                        SELECT v.*, c.nombre_empresa,
                               COALESCE(SUM(cv.monto), 0) as total_pagado
                        FROM ventas v
                        JOIN clientes c ON v.cliente_id = c.id
                        LEFT JOIN cobros_ventas cv ON v.id = cv.venta_id
                    """
                    params = []
                    if fecha_inicio and fecha_fin:
                        query += " WHERE v.fecha_venta BETWEEN %s AND %s"
                        params.extend([fecha_inicio, fecha_fin])
                    
                    query += " GROUP BY v.id, c.nombre_empresa ORDER BY v.fecha_venta DESC"
                    cur.execute(query, params)
                    ventas = cur.fetchall()
            
            # Crear tabla de ventas
            data = [['ID', 'Cliente', 'Fecha', 'Cantidad (kg)', 'Precio/kg', 'Total', 'Pagado', 'Estado']]
            
            for venta in ventas:
                data.append([
                    str(venta['id']),
                    venta['nombre_empresa'],
                    str(venta['fecha_venta']),
                    f"{venta['cantidad_kg']:.2f}",
                    f"${venta['precio_kg']:.2f}",
                    f"${venta['total']:.2f}",
                    f"${venta['total_pagado']:.2f}",
                    venta['estado_cobro']
                ])
            
            # Estilo de la tabla
            table = Table(data)
            table.setStyle(TableStyle([
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
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            
            # Generar el PDF
            doc.build(elements)
            return filename
            
        except Exception as e:
            print(f"Error al generar reporte de ventas: {str(e)}")
            return None
            
    def generar_reporte_compras(self, fecha_inicio=None, fecha_fin=None):
        """Genera un reporte PDF de compras"""
        try:
            # Crear el documento PDF
            filename = f"reporte_compras_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            doc = SimpleDocTemplate(filename, pagesize=letter)
            
            # Contenido del documento
            elements = []
            
            # Título
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=16,
                spaceAfter=30
            )
            elements.append(Paragraph("Reporte de Compras", title_style))
            
            # Fechas del reporte
            if fecha_inicio and fecha_fin:
                date_text = f"Período: {fecha_inicio} al {fecha_fin}"
            else:
                date_text = "Período: Todo el tiempo"
            elements.append(Paragraph(date_text, self.styles['Normal']))
            elements.append(Spacer(1, 20))
            
            # Obtener datos de compras
            with self.db.connect() as conn:
                with conn.cursor() as cur:
                    query = """
                        SELECT c.*, p.nombre || ' ' || p.apellido as proveedor_nombre,
                               COALESCE(SUM(pc.monto), 0) as total_pagado
                        FROM compras c
                        JOIN proveedores p ON c.proveedor_id = p.id
                        LEFT JOIN pagos_compras pc ON c.id = pc.compra_id
                    """
                    params = []
                    if fecha_inicio and fecha_fin:
                        query += " WHERE c.fecha_compra BETWEEN %s AND %s"
                        params.extend([fecha_inicio, fecha_fin])
                    
                    query += " GROUP BY c.id, p.nombre, p.apellido ORDER BY c.fecha_compra DESC"
                    cur.execute(query, params)
                    compras = cur.fetchall()
            
            # Crear tabla de compras
            data = [['ID', 'Proveedor', 'Fecha', 'Cantidad (kg)', 'Precio/kg', 'Total', 'Pagado', 'Estado']]
            
            for compra in compras:
                data.append([
                    str(compra['id']),
                    compra['proveedor_nombre'],
                    str(compra['fecha_compra']),
                    f"{compra['cantidad_kg']:.2f}",
                    f"${compra['precio_kg']:.2f}",
                    f"${compra['total']:.2f}",
                    f"${compra['total_pagado']:.2f}",
                    compra['estado_pago']
                ])
            
            # Estilo de la tabla
            table = Table(data)
            table.setStyle(TableStyle([
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
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            
            # Generar el PDF
            doc.build(elements)
            return filename
            
        except Exception as e:
            print(f"Error al generar reporte de compras: {str(e)}")
            return None
            
    def generar_factura_venta(self, venta_id):
        """Genera una factura PDF para una venta específica"""
        try:
            # Obtener datos de la venta
            with self.db.connect() as conn:
                with conn.cursor() as cur:
                    # Obtener datos de la venta
                    cur.execute("""
                        SELECT v.*, c.nombre_empresa, c.nit, c.direccion,
                               u.nombre || ' ' || u.apellido as vendedor
                        FROM ventas v
                        JOIN clientes c ON v.cliente_id = c.id
                        JOIN usuarios u ON v.usuario_id = u.id
                        WHERE v.id = %s
                    """, (venta_id,))
                    venta = cur.fetchone()
                    
                    # Obtener pagos realizados
                    cur.execute("""
                        SELECT * FROM cobros_ventas
                        WHERE venta_id = %s
                        ORDER BY fecha_cobro
                    """, (venta_id,))
                    pagos = cur.fetchall()
            
            # Crear el documento PDF
            filename = os.path.join(self.facturas_dir, f"factura_venta_{venta_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
            doc = SimpleDocTemplate(filename, pagesize=letter)
            
            # Contenido del documento
            elements = []
            
            # Estilos
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=16,
                spaceAfter=30
            )
            subtitle_style = ParagraphStyle(
                'CustomSubtitle',
                parent=self.styles['Heading2'],
                fontSize=12,
                spaceAfter=10
            )
            
            # Título
            elements.append(Paragraph("FACTURA DE VENTA", title_style))
            
            # Información de la empresa
            elements.append(Paragraph("CafeExport S.A.", subtitle_style))
            elements.append(Paragraph("NIT: 123456789-0", self.styles['Normal']))
            elements.append(Paragraph("Dirección: Calle Principal #123", self.styles['Normal']))
            elements.append(Paragraph(f"Fecha: {venta['fecha_venta']}", self.styles['Normal']))
            elements.append(Paragraph(f"Factura No: {venta_id}", self.styles['Normal']))
            elements.append(Spacer(1, 20))
            
            # Información del cliente
            elements.append(Paragraph("Datos del Cliente:", subtitle_style))
            elements.append(Paragraph(f"Nombre: {venta['nombre_empresa']}", self.styles['Normal']))
            elements.append(Paragraph(f"NIT: {venta['nit']}", self.styles['Normal']))
            elements.append(Paragraph(f"Dirección: {venta['direccion']}", self.styles['Normal']))
            elements.append(Spacer(1, 20))
            
            # Detalles de la venta
            elements.append(Paragraph("Detalles de la Venta:", subtitle_style))
            data = [['Cantidad (kg)', 'Precio/kg', 'Subtotal']]
            data.append([
                f"{venta['cantidad_kg']:.2f}",
                f"${venta['precio_kg']:.2f}",
                f"${venta['total']:.2f}"
            ])
            
            table = Table(data)
            table.setStyle(TableStyle([
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
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 20))
            
            # Total
            elements.append(Paragraph(f"Total: ${venta['total']:.2f}", self.styles['Heading2']))
            elements.append(Spacer(1, 20))
            
            # Pagos realizados
            if pagos:
                elements.append(Paragraph("Pagos Realizados:", subtitle_style))
                data_pagos = [['Fecha', 'Monto', 'Método', 'Referencia']]
                for pago in pagos:
                    data_pagos.append([
                        str(pago['fecha_cobro']),
                        f"${pago['monto']:.2f}",
                        pago['metodo_cobro'],
                        pago['referencia_cobro'] or ''
                    ])
                
                table_pagos = Table(data_pagos)
                table_pagos.setStyle(TableStyle([
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
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                elements.append(table_pagos)
            
            # Generar el PDF
            doc.build(elements)
            return filename
            
        except Exception as e:
            print(f"Error al generar factura de venta: {str(e)}")
            return None
            
    def generar_factura_compra(self, compra_id):
        """Genera una factura PDF para una compra específica"""
        try:
            # Obtener datos de la compra
            with self.db.connect() as conn:
                with conn.cursor() as cur:
                    # Obtener datos de la compra
                    cur.execute("""
                        SELECT c.*, p.nombre || ' ' || p.apellido as proveedor_nombre,
                               p.documento_identidad, p.direccion,
                               u.nombre || ' ' || u.apellido as comprador
                        FROM compras c
                        JOIN proveedores p ON c.proveedor_id = p.id
                        JOIN usuarios u ON c.usuario_id = u.id
                        WHERE c.id = %s
                    """, (compra_id,))
                    compra = cur.fetchone()
                    
                    # Obtener pagos realizados
                    cur.execute("""
                        SELECT * FROM pagos_compras
                        WHERE compra_id = %s
                        ORDER BY fecha_pago
                    """, (compra_id,))
                    pagos = cur.fetchall()
            
            # Crear el documento PDF
            filename = os.path.join(self.facturas_dir, f"factura_compra_{compra_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf")
            doc = SimpleDocTemplate(filename, pagesize=letter)
            
            # Contenido del documento
            elements = []
            
            # Estilos
            title_style = ParagraphStyle(
                'CustomTitle',
                parent=self.styles['Heading1'],
                fontSize=16,
                spaceAfter=30
            )
            subtitle_style = ParagraphStyle(
                'CustomSubtitle',
                parent=self.styles['Heading2'],
                fontSize=12,
                spaceAfter=10
            )
            
            # Título
            elements.append(Paragraph("FACTURA DE COMPRA", title_style))
            
            # Información de la empresa
            elements.append(Paragraph("CafeExport S.A.", subtitle_style))
            elements.append(Paragraph("NIT: 123456789-0", self.styles['Normal']))
            elements.append(Paragraph("Dirección: Calle Principal #123", self.styles['Normal']))
            elements.append(Paragraph(f"Fecha: {compra['fecha_compra']}", self.styles['Normal']))
            elements.append(Paragraph(f"Factura No: {compra_id}", self.styles['Normal']))
            elements.append(Spacer(1, 20))
            
            # Información del proveedor
            elements.append(Paragraph("Datos del Proveedor:", subtitle_style))
            elements.append(Paragraph(f"Nombre: {compra['proveedor_nombre']}", self.styles['Normal']))
            elements.append(Paragraph(f"Documento: {compra['documento_identidad']}", self.styles['Normal']))
            elements.append(Paragraph(f"Dirección: {compra['direccion']}", self.styles['Normal']))
            elements.append(Spacer(1, 20))
            
            # Detalles de la compra
            elements.append(Paragraph("Detalles de la Compra:", subtitle_style))
            data = [['Cantidad (kg)', 'Precio/kg', 'Subtotal']]
            data.append([
                f"{compra['cantidad_kg']:.2f}",
                f"${compra['precio_kg']:.2f}",
                f"${compra['total']:.2f}"
            ])
            
            table = Table(data)
            table.setStyle(TableStyle([
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
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('GRID', (0, 0), (-1, -1), 1, colors.black)
            ]))
            
            elements.append(table)
            elements.append(Spacer(1, 20))
            
            # Total
            elements.append(Paragraph(f"Total: ${compra['total']:.2f}", self.styles['Heading2']))
            elements.append(Spacer(1, 20))
            
            # Pagos realizados
            if pagos:
                elements.append(Paragraph("Pagos Realizados:", subtitle_style))
                data_pagos = [['Fecha', 'Monto', 'Método', 'Referencia']]
                for pago in pagos:
                    data_pagos.append([
                        str(pago['fecha_pago']),
                        f"${pago['monto']:.2f}",
                        pago['metodo_pago'],
                        pago['referencia_pago'] or ''
                    ])
                
                table_pagos = Table(data_pagos)
                table_pagos.setStyle(TableStyle([
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
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.black)
                ]))
                
                elements.append(table_pagos)
            
            # Generar el PDF
            doc.build(elements)
            return filename
            
        except Exception as e:
            print(f"Error al generar factura de compra: {str(e)}")
            return None 