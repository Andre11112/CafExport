from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                            QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
                            QFormLayout, QMessageBox, QGroupBox, QTabWidget)
from backend.database import DatabaseConnection

class ProveedoresView(QWidget):
    def __init__(self, user_id=1):
        super().__init__()
        self.user_id = user_id
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Crear pestañas
        tabs = QTabWidget()
        
        # Pestaña de registro de campesinos
        tab_registro = QWidget()
        registro_layout = QVBoxLayout(tab_registro)
        
        # Formulario de registro
        form_group = QGroupBox("Registro de Nuevo Campesino")
        form_layout = QFormLayout()
        
        # Campos del formulario
        self.nombre = QLineEdit()
        self.apellido = QLineEdit()
        self.cedula = QLineEdit()
        self.telefono = QLineEdit()
        self.direccion = QLineEdit()
        
        form_layout.addRow("Nombre:", self.nombre)
        form_layout.addRow("Apellido:", self.apellido)
        form_layout.addRow("Cédula:", self.cedula)
        form_layout.addRow("Teléfono:", self.telefono)
        form_layout.addRow("Dirección:", self.direccion)
        
        # Botones
        btn_layout = QHBoxLayout()
        self.btn_guardar = QPushButton("Guardar Campesino")
        self.btn_limpiar = QPushButton("Limpiar")
        btn_layout.addWidget(self.btn_guardar)
        btn_layout.addWidget(self.btn_limpiar)
        
        form_group.setLayout(form_layout)
        registro_layout.addWidget(form_group)
        registro_layout.addLayout(btn_layout)
        
        # Pestaña de lista de campesinos
        tab_lista = QWidget()
        lista_layout = QVBoxLayout(tab_lista)
        
        # Tabla de campesinos
        self.tabla_campesinos = QTableWidget()
        self.tabla_campesinos.setColumnCount(6)
        self.tabla_campesinos.setHorizontalHeaderLabels([
            "ID", "Nombre", "Cédula", "Teléfono", "Total Compras (kg)", "Estado"
        ])
        
        # Botones de acción
        btn_acciones = QHBoxLayout()
        self.btn_editar = QPushButton("Editar")
        self.btn_ver_historial = QPushButton("Ver Historial")
        self.btn_ver_estadisticas = QPushButton("Ver Estadísticas")
        btn_acciones.addWidget(self.btn_editar)
        btn_acciones.addWidget(self.btn_ver_historial)
        btn_acciones.addWidget(self.btn_ver_estadisticas)
        
        lista_layout.addWidget(self.tabla_campesinos)
        lista_layout.addLayout(btn_acciones)
        
        # Agregar pestañas
        tabs.addTab(tab_registro, "Registro")
        tabs.addTab(tab_lista, "Lista de Campesinos")
        
        layout.addWidget(tabs)
        
        # Conectar señales
        self.btn_guardar.clicked.connect(self.guardar_campesino)
        self.btn_limpiar.clicked.connect(self.limpiar_formulario)
        self.btn_editar.clicked.connect(self.editar_campesino)
        self.btn_ver_historial.clicked.connect(self.ver_historial)
        self.btn_ver_estadisticas.clicked.connect(self.ver_estadisticas)
        
        # Cargar datos iniciales
        self.cargar_campesinos()
        
    def guardar_campesino(self):
        try:
            # Obtener datos del formulario
            nombre = self.nombre.text()
            apellido = self.apellido.text()
            cedula = self.cedula.text()
            telefono = self.telefono.text()
            direccion = self.direccion.text()
            
            if not all([nombre, apellido, cedula, telefono, direccion]):
                self.mostrar_mensaje("Error", "Todos los campos son obligatorios")
                return
            
            # Conectar con la base de datos
            with DatabaseConnection().connect() as conn:
                with conn.cursor() as cur:
                    # Verificar si ya existe el campesino
                    cur.execute("""
                        SELECT id FROM proveedores 
                        WHERE documento_identidad = %s
                    """, (cedula,))
                    if cur.fetchone():
                        self.mostrar_mensaje("Error", "Ya existe un campesino con esta cédula")
                        return
                    
                    # Insertar nuevo campesino
                    cur.execute("""
                        INSERT INTO proveedores (nombre, apellido, documento_identidad,
                                               telefono, direccion, creado_por)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, (nombre, apellido, cedula, telefono, direccion, self.user_id))
                    
                    conn.commit()
                    
                    self.mostrar_mensaje("Éxito", "Campesino registrado correctamente")
                    self.limpiar_formulario()
                    self.cargar_campesinos()
                    
        except Exception as e:
            self.mostrar_mensaje("Error", f"Error al registrar el campesino: {str(e)}")
            
    def cargar_campesinos(self):
        try:
            with DatabaseConnection().connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT p.*, 
                               COALESCE(SUM(c.cantidad_kg), 0) as total_compras,
                               CASE 
                                   WHEN EXISTS (
                                       SELECT 1 FROM compras 
                                       WHERE proveedor_id = p.id 
                                       AND estado_pago = 'pendiente'
                                   ) THEN 'Pendiente'
                                   ELSE 'Al día'
                               END as estado
                        FROM proveedores p
                        LEFT JOIN compras c ON p.id = c.proveedor_id
                        GROUP BY p.id
                        ORDER BY p.nombre, p.apellido
                    """)
                    campesinos = cur.fetchall()
                    
                    self.tabla_campesinos.setRowCount(len(campesinos))
                    for i, campesino in enumerate(campesinos):
                        self.tabla_campesinos.setItem(i, 0, QTableWidgetItem(str(campesino['id'])))
                        self.tabla_campesinos.setItem(i, 1, QTableWidgetItem(f"{campesino['nombre']} {campesino['apellido']}"))
                        self.tabla_campesinos.setItem(i, 2, QTableWidgetItem(campesino['documento_identidad']))
                        self.tabla_campesinos.setItem(i, 3, QTableWidgetItem(campesino['telefono']))
                        self.tabla_campesinos.setItem(i, 4, QTableWidgetItem(f"{campesino['total_compras']:.2f}"))
                        self.tabla_campesinos.setItem(i, 5, QTableWidgetItem(campesino['estado']))
                        
        except Exception as e:
            self.mostrar_mensaje("Error", f"Error al cargar campesinos: {str(e)}")
            
    def editar_campesino(self):
        # TODO: Implementar edición de campesino
        self.mostrar_mensaje("Info", "Función en desarrollo")
        
    def ver_historial(self):
        # TODO: Implementar vista de historial de compras
        self.mostrar_mensaje("Info", "Función en desarrollo")
        
    def ver_estadisticas(self):
        # TODO: Implementar vista de estadísticas
        self.mostrar_mensaje("Info", "Función en desarrollo")
        
    def limpiar_formulario(self):
        self.nombre.clear()
        self.apellido.clear()
        self.cedula.clear()
        self.telefono.clear()
        self.direccion.clear()
        
    def mostrar_mensaje(self, titulo, mensaje):
        QMessageBox.information(self, titulo, mensaje) 