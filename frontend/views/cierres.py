from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QFileDialog, QMessageBox, QGroupBox,
    QTableWidget, QTableWidgetItem, QHeaderView
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from database.conexion import get_connection
from datetime import datetime
import os
import requests

class CierreContableWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.cargar_datos_iniciales()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Grupo de selección
        sel_group = QGroupBox("Seleccionar Mes y Año para Cierre Contable")
        sel_layout = QHBoxLayout()
        
        # Combo boxes
        self.combo_anio = QComboBox()
        self.combo_mes = QComboBox()
        
        # Labels
        sel_layout.addWidget(QLabel("Año:"))
        sel_layout.addWidget(self.combo_anio)
        sel_layout.addWidget(QLabel("Mes:"))
        sel_layout.addWidget(self.combo_mes)
        
        sel_group.setLayout(sel_layout)
        layout.addWidget(sel_group)

        # Tabla de resumen
        self.tabla_resumen = QTableWidget()
        self.tabla_resumen.setColumnCount(2)
        self.tabla_resumen.setHorizontalHeaderLabels(["Concepto", "Valor"])
        self.tabla_resumen.horizontalHeader().setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch)
        self.tabla_resumen.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.ResizeToContents)
        layout.addWidget(self.tabla_resumen)

        # Tabla de todos los cierres
        self.tabla_todos = QTableWidget()
        self.tabla_todos.setColumnCount(9)
        self.tabla_todos.setHorizontalHeaderLabels([
            "ID", "Mes", "Año", "Total Ventas", "Total Compras", "Utilidad", "Fecha Cierre", "PDF Path", "Usuario ID"
        ])
        self.tabla_todos.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        layout.addWidget(QLabel("Todos los cierres contables registrados:"))
        layout.addWidget(self.tabla_todos)

        # Gráfico
        self.figure = Figure(figsize=(4, 3))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Botón para generar PDF
        self.btn_generar = QPushButton("Generar y Descargar Cierre PDF")
        self.btn_generar.clicked.connect(self.generar_y_ver_pdf)
        layout.addWidget(self.btn_generar)

        # Conectar señales
        self.combo_anio.currentIndexChanged.connect(self.actualizar_combo_mes)
        self.combo_anio.currentIndexChanged.connect(self.actualizar_metricas)
        self.combo_mes.currentIndexChanged.connect(self.actualizar_metricas)

    def cargar_datos_iniciales(self):
        print("Iniciando carga de datos...")
        self.combo_anio.clear()  # Limpiar antes de llenar
        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Error", "No se pudo conectar a la base de datos")
            return

        try:
            cur = conn.cursor()
            print("Consultando años disponibles...")
            cur.execute("SELECT DISTINCT anio FROM cierres_contables ORDER BY anio")
            anios = [str(row[0]) for row in cur.fetchall()]
            print(f"Años encontrados: {anios}")
            cur.close()
            conn.close()

            if anios:
                self.combo_anio.addItems(anios)
                self.actualizar_combo_mes()
            else:
                print("No se encontraron años en la tabla")
                self.combo_mes.clear()
                self.tabla_resumen.setRowCount(0)
                self.tabla_todos.setRowCount(0)
                self.limpiar_grafico()
                QMessageBox.warning(self, "Aviso", "No hay cierres disponibles en la base de datos")
        except Exception as e:
            print(f"Error al cargar años: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error al cargar años: {str(e)}")
        self.cargar_todos_los_cierres()

    def cargar_todos_los_cierres(self):
        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Error", "No se pudo conectar a la base de datos")
            return
        try:
            cur = conn.cursor()
            cur.execute("SELECT id, mes, anio, total_ventas, total_compras, utilidad, fecha_cierre, pdf_path, usuario_id FROM cierres_contables ORDER BY anio DESC, mes DESC")
            rows = cur.fetchall()
            self.tabla_todos.setRowCount(0)
            if not rows:
                print("No hay cierres contables registrados.")
            for row in rows:
                row_idx = self.tabla_todos.rowCount()
                self.tabla_todos.insertRow(row_idx)
                for col_idx, value in enumerate(row):
                    if isinstance(value, float):
                        value = f"${value:,.2f}" if col_idx in [3,4,5] else str(value)
                    elif isinstance(value, datetime):
                        value = value.strftime("%d/%m/%Y %H:%M")
                    self.tabla_todos.setItem(row_idx, col_idx, QTableWidgetItem(str(value)))
            cur.close()
            conn.close()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error al cargar todos los cierres: {str(e)}")

    def actualizar_combo_mes(self):
        self.combo_mes.clear()  # Limpiar antes de llenar
        if self.combo_anio.count() == 0:
            return

        print("Actualizando meses...")
        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Error", "No se pudo conectar a la base de datos")
            return

        try:
            anio = int(self.combo_anio.currentText())
            print(f"Consultando meses para el año {anio}")
            cur = conn.cursor()
            cur.execute("SELECT DISTINCT mes FROM cierres_contables WHERE anio = %s ORDER BY mes", (anio,))
            meses = [str(row[0]) for row in cur.fetchall()]
            print(f"Meses encontrados: {meses}")
            cur.close()
            conn.close()

            if meses:
                self.combo_mes.addItems(meses)
                self.combo_mes.setCurrentIndex(0)
                self.actualizar_metricas()
            else:
                print(f"No se encontraron meses para el año {anio}")
                self.tabla_resumen.setRowCount(0)
                self.limpiar_grafico()
        except Exception as e:
            print(f"Error al cargar meses: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error al cargar meses: {str(e)}")

    def actualizar_metricas(self):
        if self.combo_mes.count() == 0 or self.combo_anio.count() == 0:
            self.tabla_resumen.setRowCount(0)
            self.limpiar_grafico()
            return

        print("Actualizando métricas...")
        conn = get_connection()
        if not conn:
            QMessageBox.critical(self, "Error", "No se pudo conectar a la base de datos")
            return

        try:
            anio = int(self.combo_anio.currentText())
            mes = int(self.combo_mes.currentText())
            print(f"Consultando datos para {anio}-{mes}")
            cur = conn.cursor()
            cur.execute("""
                SELECT total_ventas, total_compras, utilidad, fecha_cierre
                FROM cierres_contables
                WHERE anio = %s AND mes = %s
            """, (anio, mes))
            resultado = cur.fetchone()
            print(f"Datos encontrados: {resultado}")
            cur.close()
            conn.close()

            self.tabla_resumen.setRowCount(0)
            if resultado:
                total_ventas, total_compras, utilidad, fecha_cierre = resultado
                print(f"Procesando datos: Ventas=${total_ventas}, Compras=${total_compras}, Utilidad=${utilidad}")
                self.agregar_fila_tabla("Total Ventas", f"${total_ventas:,.2f}")
                self.agregar_fila_tabla("Total Compras", f"${total_compras:,.2f}")
                self.agregar_fila_tabla("Utilidad", f"${utilidad:,.2f}")
                if fecha_cierre:
                    self.agregar_fila_tabla("Fecha de Cierre", fecha_cierre.strftime("%d/%m/%Y %H:%M"))
                self.actualizar_grafico(total_ventas, total_compras)
            else:
                print(f"No se encontraron datos para {anio}-{mes}")
                self.limpiar_grafico()
        except Exception as e:
            print(f"Error al cargar métricas: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error al cargar métricas: {str(e)}")

    def agregar_fila_tabla(self, concepto, valor):
        row = self.tabla_resumen.rowCount()
        self.tabla_resumen.insertRow(row)
        self.tabla_resumen.setItem(row, 0, QTableWidgetItem(concepto))
        self.tabla_resumen.setItem(row, 1, QTableWidgetItem(str(valor)))

    def actualizar_grafico(self, ventas, compras):
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        
        if ventas > 0 or compras > 0:
            ax.pie(
                [ventas, compras],
                labels=['Ventas', 'Compras'],
                autopct='%1.1f%%',
                colors=['#27ae60', '#2980b9']
            )
            ax.set_title('Distribución Ingresos/Egresos')
        
        self.canvas.draw()

    def limpiar_grafico(self):
        self.figure.clear()
        self.canvas.draw()

    def generar_y_ver_pdf(self):
        if self.combo_mes.count() == 0 or self.combo_anio.count() == 0:
            QMessageBox.warning(self, "Aviso", "Seleccione un mes y año válido")
            return

        fila = self.tabla_todos.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Aviso", "Seleccione un cierre de la tabla")
            return

        cierre_id_item = self.tabla_todos.item(fila, 0)
        if not cierre_id_item:
            QMessageBox.warning(self, "Aviso", "No se pudo obtener el ID del cierre")
            return

        cierre_id_str = cierre_id_item.text().strip()
        print(f"[DEBUG] ID seleccionado (str): {cierre_id_str}")

        try:
            cierre_id = int(cierre_id_str)
            if cierre_id <= 0:
                raise ValueError("ID debe ser un número positivo")
        except ValueError as e:
            print(f"[ERROR] ID de cierre inválido: {cierre_id_str} - {str(e)}")
            QMessageBox.warning(self, "Aviso", f"ID de cierre inválido: {cierre_id_str}")
            return

        print(f"[DEBUG] ID seleccionado (int): {cierre_id}")
        print(f"[DEBUG] URL a solicitar: http://localhost:8000/cierres/pdf/por-id/{cierre_id}")

        try:
            response = requests.get(f"http://localhost:8000/cierres/pdf/por-id/{cierre_id}")
            print(f"[DEBUG] Código de respuesta: {response.status_code}")
            
            if response.status_code == 200:
                file_path, _ = QFileDialog.getSaveFileName(
                    self,
                    "Guardar PDF",
                    f"cierre_{cierre_id}.pdf",
                    "PDF Files (*.pdf)"
                )
                if file_path:
                    with open(file_path, 'wb') as f:
                        f.write(response.content)
                    QMessageBox.information(self, "Éxito", f"PDF generado y guardado en:\n{file_path}")
            else:
                error_msg = f"No se pudo generar el PDF. Código: {response.status_code}"
                try:
                    error_detail = response.json().get('detail', '')
                    if error_detail:
                        error_msg += f"\nDetalle: {error_detail}"
                except:
                    pass
                print(f"[ERROR] {error_msg}")
                QMessageBox.warning(self, "Aviso", error_msg)
        except requests.exceptions.RequestException as e:
            print(f"[ERROR] Error de conexión: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error de conexión al servidor: {str(e)}")
        except Exception as e:
            print(f"[ERROR] Error inesperado: {str(e)}")
            QMessageBox.critical(self, "Error", f"Error al generar PDF: {str(e)}") 