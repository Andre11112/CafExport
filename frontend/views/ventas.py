from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton,
                            QLabel, QLineEdit, QTableWidget, QTableWidgetItem,
                            QSpinBox, QDoubleSpinBox, QFormLayout,
                            QMessageBox, QGroupBox, QComboBox, QTabWidget)
from backend.api.coffee_price import CoffeePriceAPI
from backend.database import DatabaseConnection
from PyQt6.QtCore import QTimer

class VentasView(QWidget):
    def __init__(self, user_id=1):
        super().__init__()
        self.user_id = user_id
        self.coffee_api = CoffeePriceAPI()
        self.clientes = []
        self.init_ui()
        
        # Actualizar precio cada 5 minutos
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_precio_mercado)
        self.timer.start(300000)
        
    def init_ui(self):
        layout = QVBoxLayout(self)
        
        # Crear pestañas
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane { border: 2px solid #ddd; border-radius: 8px; background-color: #f5f5f5; }
            QTabBar::tab { background-color: #e0e0e0; padding: 8px 20px; margin-right: 2px; 
                          border-top-left-radius: 4px; border-top-right-radius: 4px; }
            QTabBar::tab:selected { background-color: #f5f5f5; border: 2px solid #ddd; border-bottom: none; }
        """)
        
        # Pestaña de Registro de Ventas
        tab_ventas = QWidget()
        self.init_tab_ventas(tab_ventas)
        tabs.addTab(tab_ventas, "Registro de Ventas")
        
        # Pestaña de Registro de Clientes
        tab_clientes = QWidget()
        self.init_tab_clientes(tab_clientes)
        tabs.addTab(tab_clientes, "Registro de Clientes")
        
        layout.addWidget(tabs)
        
    def init_tab_ventas(self, tab):
        layout = QVBoxLayout(tab)
        
        # Precio del mercado
        self.label_precio_mercado = QLabel()
        self.label_precio_mercado.setStyleSheet("""
            QLabel { font-size: 12pt; color: #2c3e50; padding: 10px; 
                    background-color: white; border-radius: 4px; }
        """)
        layout.addWidget(self.label_precio_mercado)
        
        # Formulario de venta
        form_group = QGroupBox("Registro de Venta")
        form_layout = QFormLayout()
        
        # Búsqueda y selección del cliente
        busqueda_layout = QHBoxLayout()
        self.busqueda = QLineEdit()
        self.busqueda.setPlaceholderText("🔍 Buscar por nombre de empresa o NIT...")
        self.busqueda.textChanged.connect(self.filtrar_clientes)
        
        self.combo_cliente = QComboBox()
        self.combo_cliente.setMinimumWidth(300)
        
        busqueda_layout.addWidget(self.busqueda)
        busqueda_layout.addWidget(self.combo_cliente)
        form_layout.addRow("Cliente:", busqueda_layout)
        
        # Campos de venta
        self.cantidad = QDoubleSpinBox()
        self.cantidad.setMaximum(100000)
        self.cantidad.setDecimals(2)
        self.cantidad.valueChanged.connect(self.calcular_total)
        
        self.precio_kg = QDoubleSpinBox()
        self.precio_kg.setMaximum(100000)
        self.precio_kg.setDecimals(2)
        self.precio_kg.valueChanged.connect(self.calcular_total)
        
        self.total = QLineEdit()
        self.total.setReadOnly(True)
        
        form_layout.addRow("Cantidad (kg):", self.cantidad)
        form_layout.addRow("Precio por kg:", self.precio_kg)
        form_layout.addRow("Total:", self.total)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Botones
        btn_layout = QHBoxLayout()
        self.btn_registrar = QPushButton("💾 Registrar Venta")
        self.btn_cancelar = QPushButton("❌ Cancelar")
        self.btn_registrar.clicked.connect(self.registrar_venta)
        self.btn_cancelar.clicked.connect(self.limpiar_formulario)
        btn_layout.addWidget(self.btn_registrar)
        btn_layout.addWidget(self.btn_cancelar)
        layout.addLayout(btn_layout)
        
        # Tabla de ventas
        self.tabla_ventas = QTableWidget()
        self.tabla_ventas.setColumnCount(7)
        self.tabla_ventas.setHorizontalHeaderLabels([
            "ID", "Empresa", "Cantidad (kg)", "Precio/kg", 
            "Total", "Fecha", "Estado"
        ])
        layout.addWidget(QLabel("Últimas Ventas"))
        layout.addWidget(self.tabla_ventas)
        
        # Cargar datos iniciales
        self.cargar_clientes()
        self.actualizar_precio_mercado()
        self.cargar_ventas()
        
    def init_tab_clientes(self, tab):
        layout = QVBoxLayout(tab)
        
        # Formulario de registro
        form_group = QGroupBox("Registro de Cliente")
        form_layout = QFormLayout()
        
        self.nombre_empresa = QLineEdit()
        self.nit = QLineEdit()
        self.telefono_cliente = QLineEdit()
        self.email_cliente = QLineEdit()
        self.direccion_cliente = QLineEdit()
        
        form_layout.addRow("Nombre de la Empresa:", self.nombre_empresa)
        form_layout.addRow("NIT:", self.nit)
        form_layout.addRow("Teléfono:", self.telefono_cliente)
        form_layout.addRow("Email:", self.email_cliente)
        form_layout.addRow("Dirección:", self.direccion_cliente)
        
        # Botones
        btn_layout = QHBoxLayout()
        self.btn_guardar = QPushButton("💾 Guardar Cliente")
        self.btn_limpiar = QPushButton("🔄 Limpiar")
        self.btn_guardar.clicked.connect(self.guardar_cliente)
        self.btn_limpiar.clicked.connect(self.limpiar_formulario_cliente)
        btn_layout.addWidget(self.btn_guardar)
        btn_layout.addWidget(self.btn_limpiar)
        form_layout.addRow("", btn_layout)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Tabla de clientes
        self.tabla_clientes = QTableWidget()
        self.tabla_clientes.setColumnCount(6)
        self.tabla_clientes.setHorizontalHeaderLabels([
            "ID", "Empresa", "NIT", "Teléfono", "Email", "Dirección"
        ])
        layout.addWidget(QLabel("Lista de Clientes"))
        layout.addWidget(self.tabla_clientes)
        
        # Cargar datos iniciales
        self.cargar_tabla_clientes()
        
    def registrar_venta(self):
        try:
            cliente_id = self.combo_cliente.currentData()
            cantidad = self.cantidad.value()
            precio = self.precio_kg.value()
            total = cantidad * precio
            
            if not cliente_id:
                self.mostrar_mensaje("Error", "Debe seleccionar un cliente")
                return
                
            if cantidad <= 0:
                self.mostrar_mensaje("Error", "La cantidad debe ser mayor a 0")
                return
                
            if precio <= 0:
                self.mostrar_mensaje("Error", "El precio debe ser mayor a 0")
                return
            
            with DatabaseConnection().connect() as conn:
                with conn.cursor() as cur:
                    # Verificar inventario
                    cur.execute("""
                        SELECT COALESCE(
                            (SELECT SUM(cantidad_kg) FROM inventario_cafe WHERE tipo_movimiento = 'entrada') -
                            (SELECT COALESCE(SUM(cantidad_kg), 0) FROM inventario_cafe WHERE tipo_movimiento = 'salida'),
                            0
                        ) as disponible
                    """)
                    disponible = cur.fetchone()['disponible']
                    
                    if disponible < cantidad:
                        self.mostrar_mensaje("Error", f"No hay suficiente café. Disponible: {disponible:.2f} kg")
                        return
                    
                    # Registrar venta
                    cur.execute("""
                        INSERT INTO ventas (cliente_id, usuario_id, cantidad_kg,
                                          precio_kg, total, estado_cobro)
                        VALUES (%s, %s, %s, %s, %s, 'pendiente')
                        RETURNING id
                    """, (cliente_id, self.user_id, cantidad, precio, total))
                    
                    venta_id = cur.fetchone()['id']
                    
                    # Actualizar inventario
                    cur.execute("""
                        INSERT INTO inventario_cafe (cantidad_kg, tipo_movimiento,
                                                   referencia_id, tipo_referencia, usuario_id)
                        VALUES (%s, 'salida', %s, 'venta', %s)
                    """, (cantidad, venta_id, self.user_id))
                    
                    conn.commit()
                    
                    self.mostrar_mensaje("Éxito", "Venta registrada correctamente")
                    self.limpiar_formulario()
                    self.cargar_ventas()
                    
        except Exception as e:
            self.mostrar_mensaje("Error", f"Error al registrar venta: {str(e)}")
            
    def guardar_cliente(self):
        try:
            nombre_empresa = self.nombre_empresa.text()
            nit = self.nit.text()
            telefono = self.telefono_cliente.text()
            email = self.email_cliente.text()
            direccion = self.direccion_cliente.text()
            
            if not all([nombre_empresa, nit, telefono, email, direccion]):
                self.mostrar_mensaje("Error", "Todos los campos son obligatorios")
                return
            
            with DatabaseConnection().connect() as conn:
                with conn.cursor() as cur:
                    # Verificar si existe
                    cur.execute("SELECT id FROM clientes WHERE nit = %s", (nit,))
                    if cur.fetchone():
                        self.mostrar_mensaje("Error", "Ya existe un cliente con este NIT")
                        return
                    
                    # Insertar cliente
                    cur.execute("""
                        INSERT INTO clientes (nombre_empresa, nit, tipo_cliente,
                                            telefono, email, direccion, creado_por)
                        VALUES (%s, %s, 'exportador', %s, %s, %s, %s)
                    """, (nombre_empresa, nit, telefono, email, direccion, self.user_id))
                    
                    conn.commit()
                    
                    self.mostrar_mensaje("Éxito", "Cliente registrado correctamente")
                    self.limpiar_formulario_cliente()
                    self.cargar_tabla_clientes()
                    self.cargar_clientes()
                    
        except Exception as e:
            self.mostrar_mensaje("Error", f"Error al registrar cliente: {str(e)}")

    def limpiar_formulario(self):
        self.busqueda.clear()
        self.cantidad.setValue(0)
        self.precio_kg.setValue(0)
        self.total.clear()
        
    def calcular_total(self):
        cantidad = self.cantidad.value()
        precio = self.precio_kg.value()
        total = cantidad * precio
        self.total.setText(f"{total:.2f}")
        
    def actualizar_precio_mercado(self):
        precio_actual = self.coffee_api.get_current_price()
        if precio_actual and not precio_actual.get('error', False):
            precio_kg = precio_actual['precio']
            precio_carga = precio_actual['precio_carga']
            self.precio_kg.setValue(precio_kg)
            self.label_precio_mercado.setText(
                f"Precio del mercado:\n"
                f"Por kilogramo: ${precio_kg:,.2f}/kg\n"
                f"Por carga (125kg): ${precio_carga:,.2f}\n"
                f"Actualizado: {precio_actual['fecha'].strftime('%Y-%m-%d %H:%M')}"
            )
        else:
            self.label_precio_mercado.setText("Error al obtener el precio del mercado")

    def cargar_ventas(self):
        try:
            with DatabaseConnection().connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT v.*, c.nombre_empresa
                        FROM ventas v
                        JOIN clientes c ON v.cliente_id = c.id
                        WHERE c.tipo_cliente = 'exportador'
                        ORDER BY v.fecha_venta DESC
                        LIMIT 10
                    """)
                    ventas = cur.fetchall()
                    
                    self.tabla_ventas.setRowCount(len(ventas))
                    for i, venta in enumerate(ventas):
                        self.tabla_ventas.setItem(i, 0, QTableWidgetItem(str(venta['id'])))
                        self.tabla_ventas.setItem(i, 1, QTableWidgetItem(venta['nombre_empresa']))
                        self.tabla_ventas.setItem(i, 2, QTableWidgetItem(f"{venta['cantidad_kg']:.2f}"))
                        self.tabla_ventas.setItem(i, 3, QTableWidgetItem(f"{venta['precio_kg']:.2f}"))
                        self.tabla_ventas.setItem(i, 4, QTableWidgetItem(f"{venta['total']:.2f}"))
                        self.tabla_ventas.setItem(i, 5, QTableWidgetItem(str(venta['fecha_venta'])))
                        self.tabla_ventas.setItem(i, 6, QTableWidgetItem(venta['estado_cobro']))
        except Exception as e:
            self.mostrar_mensaje("Error", f"Error al cargar ventas: {str(e)}")

    def mostrar_mensaje(self, titulo, mensaje):
        QMessageBox.information(self, titulo, mensaje)

    def limpiar_formulario_cliente(self):
        self.nombre_empresa.clear()
        self.nit.clear()
        self.telefono_cliente.clear()
        self.email_cliente.clear()
        self.direccion_cliente.clear()

    def cargar_tabla_clientes(self):
        try:
            with DatabaseConnection().connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, nombre_empresa, nit, telefono, email, direccion
                        FROM clientes
                        WHERE tipo_cliente = 'exportador'
                        ORDER BY nombre_empresa
                    """)
                    clientes = cur.fetchall()
                    
                    self.tabla_clientes.setRowCount(len(clientes))
                    for i, cliente in enumerate(clientes):
                        self.tabla_clientes.setItem(i, 0, QTableWidgetItem(str(cliente['id'])))
                        self.tabla_clientes.setItem(i, 1, QTableWidgetItem(cliente['nombre_empresa']))
                        self.tabla_clientes.setItem(i, 2, QTableWidgetItem(cliente['nit']))
                        self.tabla_clientes.setItem(i, 3, QTableWidgetItem(cliente['telefono']))
                        self.tabla_clientes.setItem(i, 4, QTableWidgetItem(cliente['email']))
                        self.tabla_clientes.setItem(i, 5, QTableWidgetItem(cliente['direccion']))
        except Exception as e:
            self.mostrar_mensaje("Error", f"Error al cargar clientes: {str(e)}")

    def filtrar_clientes(self):
        texto_busqueda = self.busqueda.text().lower()
        if not texto_busqueda:
            self.actualizar_combo_clientes(self.clientes)
            return
            
        clientes_filtrados = [
            c for c in self.clientes
            if texto_busqueda in c['nombre_empresa'].lower() or
               texto_busqueda in c['nit'].lower()
        ]
        self.actualizar_combo_clientes(clientes_filtrados)
            
    def cargar_clientes(self):
        try:
            with DatabaseConnection().connect() as conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        SELECT id, nombre_empresa, nit 
                        FROM clientes 
                        WHERE tipo_cliente = 'exportador'
                        ORDER BY nombre_empresa
                    """)
                    self.clientes = cur.fetchall()
                    self.actualizar_combo_clientes(self.clientes)
        except Exception as e:
            self.mostrar_mensaje("Error", f"Error al cargar clientes: {str(e)}")
            
    def actualizar_combo_clientes(self, clientes):
        self.combo_cliente.clear()
        for cliente in clientes:
            self.combo_cliente.addItem(
                f"{cliente['nombre_empresa']} - {cliente['nit']}",
                cliente['id']
            ) 