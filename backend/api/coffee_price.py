#API key: HN29649XQ7HL3UNG
import requests
from datetime import datetime
from fastapi import APIRouter
from backend.database import DatabaseConnection
import json
import logging
from bs4 import BeautifulSoup
import re

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter()

class CoffeePriceAPI:
    def __init__(self):
        self.db = DatabaseConnection()
        # URL de la página de precios de la FNC
        self.fnc_url = "https://federaciondecafeteros.org/wp/estadisticas-cafeteras/"
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

    def get_current_price(self):
        """Obtiene el precio actual del café de la FNC"""
        try:
            logger.info("Intentando obtener precio de la FNC...")
            # Obtener la página web de la FNC
            response = requests.get(self.fnc_url, headers=self.headers)
            logger.info(f"Respuesta de la FNC: Status {response.status_code}")
            
            if response.status_code == 200:
                # Parsear el HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Ejemplo: buscar cualquier número grande en la página
                match = re.search(r'(\d{1,3}(?:\.\d{3})*(?:,\d{2})?)', soup.text)
                if match:
                    precio_str = match.group(1).replace('.', '').replace(',', '.')
                    precio_carga = float(precio_str)
                    logger.info(f"Precio extraído: Carga={precio_carga}")
                    
                    # Guardar en la base de datos
                    with self.db.connect() as conn:
                        with conn.cursor() as cur:
                            cur.execute("""
                                INSERT INTO precios_cafe (precio_kg, precio_carga, fuente)
                                VALUES (%s, %s, %s)
                                RETURNING id, fecha_actualizacion
                            """, (precio_carga / 125.0, precio_carga, 'Federación Nacional de Cafeteros'))
                            conn.commit()
                            logger.info("Precio guardado en la base de datos")
                    
                    return {
                        'precio': precio_carga / 125.0,
                        'precio_carga': precio_carga,
                        'fecha': datetime.now(),
                        'fuente': 'Federación Nacional de Cafeteros',
                        'error': False,
                        'detalles': {
                            'precio_arroba': precio_carga * 12.5,
                            'precio_libra': precio_carga / 2.20462
                        }
                    }
                else:
                    logger.error("No se encontró el precio en la página")
                    return self._get_last_saved_price()
            else:
                logger.error(f"Error en la respuesta de la FNC: {response.status_code}")
                return self._get_last_saved_price()
                
        except Exception as e:
            logger.error(f"Error al obtener precio del café: {str(e)}")
            return self._get_last_saved_price()

    def _get_last_saved_price(self):
        """Obtiene el último precio guardado en la base de datos"""
        try:
            logger.info("Obteniendo último precio guardado...")
            with self.db.connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT precio_kg, fecha_actualizacion 
                        FROM precios_cafe 
                        ORDER BY fecha_actualizacion DESC 
                        LIMIT 1
                    """)
                    result = cur.fetchone()
                    
                    if result:
                        precio_kg = float(result['precio_kg'])
                        precio_carga = precio_kg * 125.0
                        logger.info(f"Precio encontrado en BD: Carga={precio_carga}, Kg={precio_kg}")
                        return {
                            'precio': precio_kg,
                            'precio_carga': precio_carga,
                            'fecha': result['fecha_actualizacion'],
                            'fuente': 'base de datos local',
                            'error': True,
                            'detalles': {
                                'precio_arroba': precio_kg * 12.5,
                                'precio_libra': precio_kg / 2.20462
                            }
                        }
                    else:
                        logger.error("No se encontraron precios en la base de datos")
                        raise ValueError("No hay precios disponibles en la base de datos")
                        
        except Exception as e:
            logger.error(f"Error al obtener último precio guardado: {str(e)}")
            raise ValueError("No se pudo obtener el precio del café")

    def get_historical_prices(self, days=30):
        """Obtiene el historial de precios de los últimos días"""
        try:
            logger.info(f"Obteniendo historial de precios de los últimos {days} días...")
            with self.db.connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT precio_kg, fecha_actualizacion, fuente
                        FROM precios_cafe 
                        WHERE fecha_actualizacion >= NOW() - INTERVAL '%s days'
                        ORDER BY fecha_actualizacion DESC
                    """, (days,))
                    results = cur.fetchall()
                    
                    if not results:
                        raise ValueError("No hay datos históricos disponibles")
                    
                    return [{
                        'precio': float(row['precio_kg']),
                        'fecha': row['fecha_actualizacion'],
                        'fuente': row['fuente'],
                        'detalles': {
                            'precio_arroba': float(row['precio_kg']) * 12.5,
                            'precio_libra': float(row['precio_kg']) / 2.20462
                        }
                    } for row in results]
        except Exception as e:
            logger.error(f"Error al obtener historial de precios: {str(e)}")
            raise ValueError("No se pudo obtener el historial de precios")

# Crear instancia de la API
coffee_api = CoffeePriceAPI()

@router.get("/precio-actual")
async def get_current_price():
    return coffee_api.get_current_price()

@router.get("/precios-historicos/{days}")
async def get_historical_prices(days: int = 30):
    return coffee_api.get_historical_prices(days) 