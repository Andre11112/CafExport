from database import Database
from datetime import datetime

class FacturacionBackend:
    def __init__(self):
        self.db = Database()
        
    def crear_factura(self, cliente_id, usuario_id, detalles, notas=None):
        """Crea una nueva factura en la base de datos"""
        try:
            # Calcular el total
            total = sum(detalle['cantidad_kg'] * detalle['precio_kg'] for detalle in detalles)
            
            # Insertar la factura
            query = """
                INSERT INTO facturas (cliente_id, usuario_id, total, notas)
                VALUES (?, ?, ?, ?)
                RETURNING id
            """
            factura_id = self.db.execute_query(query, (cliente_id, usuario_id, total, notas))
            
            # Insertar detalles de la factura
            for detalle in detalles:
                subtotal = detalle['cantidad_kg'] * detalle['precio_kg']
                query_detalle = """
                    INSERT INTO detalles_factura 
                    (factura_id, cantidad_kg, precio_kg, subtotal)
                    VALUES (?, ?, ?, ?)
                """
                self.db.execute_query(query_detalle, (
                    factura_id,
                    detalle['cantidad_kg'],
                    detalle['precio_kg'],
                    subtotal
                ))
            
            return factura_id
        except Exception as e:
            print(f"Error al crear factura: {str(e)}")
            return None
            
    def registrar_pago(self, factura_id, monto, usuario_id, metodo_pago, referencia_pago=None):
        """Registra un pago para una factura"""
        try:
            query = """
                INSERT INTO pagos_facturas 
                (factura_id, monto, usuario_id, metodo_pago, referencia_pago)
                VALUES (?, ?, ?, ?, ?)
            """
            self.db.execute_query(query, (
                factura_id, monto, usuario_id, metodo_pago, referencia_pago
            ))
            
            # Actualizar estado de la factura
            self.actualizar_estado_factura(factura_id)
            return True
        except Exception as e:
            print(f"Error al registrar pago: {str(e)}")
            return False
            
    def obtener_facturas(self, filtro=None):
        """Obtiene todas las facturas o filtra por parámetros"""
        try:
            query = """
                SELECT f.*, c.nombre_empresa as cliente_nombre,
                       u.nombre || ' ' || u.apellido as usuario_nombre
                FROM facturas f
                JOIN clientes c ON f.cliente_id = c.id
                JOIN usuarios u ON f.usuario_id = u.id
            """
            if filtro:
                query += " WHERE " + filtro
            return self.db.fetch_all(query)
        except Exception as e:
            print(f"Error al obtener facturas: {str(e)}")
            return []
            
    def obtener_detalles_factura(self, factura_id):
        """Obtiene los detalles de una factura específica"""
        try:
            query = """
                SELECT *
                FROM detalles_factura
                WHERE factura_id = ?
            """
            return self.db.fetch_all(query, (factura_id,))
        except Exception as e:
            print(f"Error al obtener detalles de factura: {str(e)}")
            return []
            
    def obtener_pagos_factura(self, factura_id):
        """Obtiene los pagos registrados para una factura"""
        try:
            query = """
                SELECT pf.*, u.nombre || ' ' || u.apellido as usuario_nombre
                FROM pagos_facturas pf
                JOIN usuarios u ON pf.usuario_id = u.id
                WHERE pf.factura_id = ?
            """
            return self.db.fetch_all(query, (factura_id,))
        except Exception as e:
            print(f"Error al obtener pagos de factura: {str(e)}")
            return []
            
    def actualizar_estado_factura(self, factura_id):
        """Actualiza el estado de la factura basado en los pagos realizados"""
        try:
            # Obtener total de la factura
            query_total = "SELECT total FROM facturas WHERE id = ?"
            total_factura = self.db.fetch_one(query_total, (factura_id,))['total']
            
            # Obtener total de pagos
            query_pagos = """
                SELECT COALESCE(SUM(monto), 0) as total_pagado
                FROM pagos_facturas
                WHERE factura_id = ?
            """
            total_pagado = self.db.fetch_one(query_pagos, (factura_id,))['total_pagado']
            
            # Determinar el nuevo estado
            if total_pagado >= total_factura:
                nuevo_estado = 'pagado'
            elif total_pagado > 0:
                nuevo_estado = 'parcial'
            else:
                nuevo_estado = 'pendiente'
                
            # Actualizar estado
            query_update = "UPDATE facturas SET estado_pago = ? WHERE id = ?"
            self.db.execute_query(query_update, (nuevo_estado, factura_id))
            return True
        except Exception as e:
            print(f"Error al actualizar estado de factura: {str(e)}")
            return False 