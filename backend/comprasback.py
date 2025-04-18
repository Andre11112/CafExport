from datetime import datetime
from decimal import Decimal
from .database import DatabaseConnection

class ComprasManager:
    def __init__(self):
        self.db = DatabaseConnection()
        
    def registrar_compra(self, proveedor_id: int, cantidad_kg: float, 
                        precio_kg: float) -> dict:
        """
        Registra una nueva compra de café
        """
        try:
            conn = self.db.connect()
            cur = conn.cursor()
            
            total = Decimal(str(cantidad_kg)) * Decimal(str(precio_kg))
            
            query = """
                INSERT INTO compras (proveedor_id, cantidad_kg, precio_kg, 
                                   total, estado_pago)
                VALUES (%s, %s, %s, %s, 'pendiente')
                RETURNING id, fecha_compra;
            """
            
            cur.execute(query, (proveedor_id, cantidad_kg, precio_kg, total))
            result = cur.fetchone()
            conn.commit()
            
            return {
                'id': result[0],
                'proveedor_id': proveedor_id,
                'cantidad_kg': cantidad_kg,
                'precio_kg': precio_kg,
                'total': float(total),
                'fecha_compra': result[1],
                'estado': 'pendiente'
            }
            
        except Exception as e:
            if conn:
                conn.rollback()
            raise e
        finally:
            if cur:
                cur.close()
            self.db.close() 