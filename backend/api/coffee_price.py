#API key: HN29649XQ7HL3UNG
import requests
from datetime import datetime
from fastapi import APIRouter
from backend.database import DatabaseConnection

router = APIRouter()

class CoffeePriceAPI:
    def __init__(self):
        # URL de la Federación Nacional de Cafeteros
        self.api_url = "https://federaciondecafeteros.org/wp/estadisticas-cafeteras/"
        self.db = DatabaseConnection()

    def get_current_price(self):
        """Obtiene el precio actual del café"""
        try:
            # Por ahora, usaremos un precio base conocido
            precio_carga = 2400000.00  # Precio aproximado actual por carga
            precio_kg = precio_carga / 125.0
            
            # Guardamos el precio en la base de datos
            with self.db.connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO precios_cafe (precio_kg, precio_carga, fuente)
                        VALUES (%s, %s, %s)
                        RETURNING id, fecha_actualizacion
                    """, (precio_kg, precio_carga, 'Precio base'))
                    conn.commit()
            
            return {
                'precio': precio_kg,
                'precio_carga': precio_carga,
                'fecha': datetime.now(),
                'fuente': 'Precio base',
                'error': False
            }
                
        except Exception as e:
            print(f"Error al obtener precio del café: {str(e)}")
            return self._get_last_saved_price()

    def _get_last_saved_price(self):
        """Obtiene el último precio guardado en la base de datos"""
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cur:
                    # Primero verificamos si existe la columna precio_carga
                    cur.execute("""
                        SELECT precio_kg, fecha_actualizacion 
                        FROM precios_cafe 
                        ORDER BY fecha_actualizacion DESC 
                        LIMIT 1
                    """)
                    result = cur.fetchone()
                    
                    if result:
                        precio_kg = float(result['precio_kg'])
                        return {
                            'precio': precio_kg,
                            'precio_carga': precio_kg * 125.0,
                            'fecha': result['fecha_actualizacion'],
                            'fuente': 'base de datos local',
                            'error': False
                        }
                    else:
                        # Precio por defecto
                        precio_carga = 2400000.00
                        return {
                            'precio': precio_carga / 125.0,
                            'precio_carga': precio_carga,
                            'fecha': datetime.now(),
                            'fuente': 'precio por defecto',
                            'error': True
                        }
        except Exception as e:
            print(f"Error al obtener último precio guardado: {str(e)}")
            return {
                'precio': 19200.00,  # 2,400,000 / 125
                'precio_carga': 2400000.00,
                'fecha': datetime.now(),
                'fuente': 'error',
                'error': True
            }

    def get_historical_prices(self, days=30):
        """Obtiene el historial de precios de los últimos días"""
        try:
            with self.db.connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT precio_kg, fecha_actualizacion, fuente
                        FROM precios_cafe 
                        WHERE fecha_actualizacion >= NOW() - INTERVAL '%s days'
                        ORDER BY fecha_actualizacion DESC
                    """, (days,))
                    results = cur.fetchall()
                    
                    return [{
                        'precio': float(row['precio_kg']),
                        'fecha': row['fecha_actualizacion'],
                        'fuente': row['fuente']
                    } for row in results]
        except Exception as e:
            print(f"Error al obtener historial de precios: {str(e)}")
            return []

# Crear instancia de la API
coffee_api = CoffeePriceAPI()

@router.get("/precio-actual")
async def get_current_price():
    return coffee_api.get_current_price()

@router.get("/precios-historicos/{days}")
async def get_historical_prices(days: int = 30):
    return coffee_api.get_historical_prices(days) 