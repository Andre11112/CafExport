from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field
from database import get_db_connection

class Contrato(BaseModel):
    id: Optional[int] = None
    numero_contrato: str
    fecha_creacion: datetime = Field(default_factory=datetime.now)
    fecha_vigencia_inicio: datetime
    fecha_vigencia_fin: datetime
    comprador_id: int
    comprador_nombre: str
    comprador_pais: str
    comprador_direccion: str
    comprador_contacto: str
    estado: str = "ACTIVO"  # ACTIVO, FINALIZADO, CANCELADO
    moneda: str
    terminos_pago: str
    condiciones_entrega: str
    notas: Optional[str] = None

class DetalleContrato(BaseModel):
    id: Optional[int] = None
    contrato_id: int
    lote_id: int
    cantidad: float
    precio_unitario: float
    subtotal: float

def crear_tabla_contratos():
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Tabla de contratos
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS contratos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        numero_contrato TEXT UNIQUE NOT NULL,
        fecha_creacion DATETIME NOT NULL,
        fecha_vigencia_inicio DATETIME NOT NULL,
        fecha_vigencia_fin DATETIME NOT NULL,
        comprador_id INTEGER NOT NULL,
        comprador_nombre TEXT NOT NULL,
        comprador_pais TEXT NOT NULL,
        comprador_direccion TEXT NOT NULL,
        comprador_contacto TEXT NOT NULL,
        estado TEXT NOT NULL,
        moneda TEXT NOT NULL,
        terminos_pago TEXT NOT NULL,
        condiciones_entrega TEXT NOT NULL,
        notas TEXT
    )
    ''')
    
    # Tabla de detalles de contrato
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS detalles_contrato (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        contrato_id INTEGER NOT NULL,
        lote_id INTEGER NOT NULL,
        cantidad REAL NOT NULL,
        precio_unitario REAL NOT NULL,
        subtotal REAL NOT NULL,
        FOREIGN KEY (contrato_id) REFERENCES contratos (id),
        FOREIGN KEY (lote_id) REFERENCES lotes (id)
    )
    ''')
    
    conn.commit()
    conn.close()

def crear_contrato(contrato: Contrato, detalles: List[DetalleContrato]) -> int:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    try:
        # Insertar contrato
        cursor.execute('''
        INSERT INTO contratos (
            numero_contrato, fecha_creacion, fecha_vigencia_inicio, fecha_vigencia_fin,
            comprador_id, comprador_nombre, comprador_pais, comprador_direccion,
            comprador_contacto, estado, moneda, terminos_pago, condiciones_entrega, notas
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            contrato.numero_contrato, contrato.fecha_creacion, contrato.fecha_vigencia_inicio,
            contrato.fecha_vigencia_fin, contrato.comprador_id, contrato.comprador_nombre,
            contrato.comprador_pais, contrato.comprador_direccion, contrato.comprador_contacto,
            contrato.estado, contrato.moneda, contrato.terminos_pago,
            contrato.condiciones_entrega, contrato.notas
        ))
        
        contrato_id = cursor.lastrowid
        
        # Insertar detalles
        for detalle in detalles:
            cursor.execute('''
            INSERT INTO detalles_contrato (
                contrato_id, lote_id, cantidad, precio_unitario, subtotal
            ) VALUES (?, ?, ?, ?, ?)
            ''', (
                contrato_id, detalle.lote_id, detalle.cantidad,
                detalle.precio_unitario, detalle.subtotal
            ))
        
        conn.commit()
        return contrato_id
    
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def obtener_contrato(contrato_id: int) -> tuple[Contrato, List[DetalleContrato]]:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Obtener contrato
    cursor.execute('SELECT * FROM contratos WHERE id = ?', (contrato_id,))
    contrato_data = cursor.fetchone()
    
    if not contrato_data:
        raise ValueError("Contrato no encontrado")
    
    contrato = Contrato(
        id=contrato_data[0],
        numero_contrato=contrato_data[1],
        fecha_creacion=datetime.fromisoformat(contrato_data[2]),
        fecha_vigencia_inicio=datetime.fromisoformat(contrato_data[3]),
        fecha_vigencia_fin=datetime.fromisoformat(contrato_data[4]),
        comprador_id=contrato_data[5],
        comprador_nombre=contrato_data[6],
        comprador_pais=contrato_data[7],
        comprador_direccion=contrato_data[8],
        comprador_contacto=contrato_data[9],
        estado=contrato_data[10],
        moneda=contrato_data[11],
        terminos_pago=contrato_data[12],
        condiciones_entrega=contrato_data[13],
        notas=contrato_data[14]
    )
    
    # Obtener detalles
    cursor.execute('SELECT * FROM detalles_contrato WHERE contrato_id = ?', (contrato_id,))
    detalles_data = cursor.fetchall()
    
    detalles = [
        DetalleContrato(
            id=row[0],
            contrato_id=row[1],
            lote_id=row[2],
            cantidad=row[3],
            precio_unitario=row[4],
            subtotal=row[5]
        )
        for row in detalles_data
    ]
    
    conn.close()
    return contrato, detalles

def listar_contratos(estado: Optional[str] = None) -> List[Contrato]:
    conn = get_db_connection()
    cursor = conn.cursor()
    
    if estado:
        cursor.execute('SELECT * FROM contratos WHERE estado = ?', (estado,))
    else:
        cursor.execute('SELECT * FROM contratos')
    
    contratos_data = cursor.fetchall()
    
    contratos = [
        Contrato(
            id=row[0],
            numero_contrato=row[1],
            fecha_creacion=datetime.fromisoformat(row[2]),
            fecha_vigencia_inicio=datetime.fromisoformat(row[3]),
            fecha_vigencia_fin=datetime.fromisoformat(row[4]),
            comprador_id=row[5],
            comprador_nombre=row[6],
            comprador_pais=row[7],
            comprador_direccion=row[8],
            comprador_contacto=row[9],
            estado=row[10],
            moneda=row[11],
            terminos_pago=row[12],
            condiciones_entrega=row[13],
            notas=row[14]
        )
        for row in contratos_data
    ]
    
    conn.close()
    return contratos

def actualizar_estado_contrato(contrato_id: int, nuevo_estado: str):
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
    UPDATE contratos
    SET estado = ?
    WHERE id = ?
    ''', (nuevo_estado, contrato_id))
    
    conn.commit()
    conn.close() 