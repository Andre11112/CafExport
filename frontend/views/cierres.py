from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QComboBox, QFileDialog, QMessageBox, QGroupBox
)
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import requests
from datetime import datetime

class CierreContableWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)

        # Selección de año y mes
        sel_group = QGroupBox("Seleccionar Mes y Año para Cierre Contable")
        sel_layout = QHBoxLayout()
        self.combo_anio = QComboBox()
        self.combo_mes = QComboBox()
        self.combo_anio.addItems([str(a) for a in range(2023, 2031)])
        self.combo_mes.addItems([str(m).zfill(2) for m in range(1, 13)])
        # Seleccionar año y mes actual por defecto
        now = datetime.now()
        self.combo_anio.setCurrentText(str(now.year))
        self.combo_mes.setCurrentText(str(now.month).zfill(2))
        sel_layout.addWidget(QLabel("Año:"))
        sel_layout.addWidget(self.combo_anio)
        sel_layout.addWidget(QLabel("Mes:"))
        sel_layout.addWidget(self.combo_mes)
        sel_group.setLayout(sel_layout)
        layout.addWidget(sel_group)

        # Métricas
        self.label_metricas = QLabel("Seleccione mes y año y presione 'Generar Cierre' para ver las métricas.")
        layout.addWidget(self.label_metricas)

        # Gráfico
        self.figure = Figure(figsize=(4, 3))
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(self.canvas)

        # Botón para generar y ver PDF
        self.btn_generar = QPushButton("Generar y Descargar Cierre PDF")
        self.btn_generar.clicked.connect(self.generar_y_ver_pdf)
        layout.addWidget(self.btn_generar)

        # Conectar los cambios de selección a la actualización de métricas
        self.combo_anio.currentIndexChanged.connect(self.actualizar_metricas)
        self.combo_mes.currentIndexChanged.connect(self.actualizar_metricas)
        self.actualizar_metricas()

    def actualizar_metricas(self):
        anio = int(self.combo_anio.currentText())
        mes = int(self.combo_mes.currentText())
        url_generar = f"http://localhost:8000/cierres/generar/{anio}/{mes}"
        try:
            resp = requests.post(url_generar)
            if resp.status_code == 200:
                data = resp.json()
                ventas = data.get('total_ventas') or 0
                compras = data.get('total_compras') or 0
                utilidad = data.get('utilidad') or 0
                kg_vendidos = data.get('kg_vendidos') or 0
                kg_comprados = data.get('kg_comprados') or 0
                prom_venta = data.get('prom_venta') or 0
                prom_compra = data.get('prom_compra') or 0
                facturas_ventas = data.get('facturas_ventas') or 0
                facturas_compras = data.get('facturas_compras') or 0
                cobros = data.get('cobros') or 0
                pagos = data.get('pagos') or 0

                if ventas == 0 and compras == 0:
                    self.label_metricas.setText("Sin datos para este mes.")
                    self.figure.clear()
                    self.canvas.draw()
                    return

                self.label_metricas.setText(
                    f"<b>Cierre {anio}-{mes:02d}</b><br>"
                    f"Total Ventas: <b>${ventas:,.2f}</b><br>"
                    f"Total Compras: <b>${compras:,.2f}</b><br>"
                    f"Utilidad: <b>${utilidad:,.2f}</b><br>"
                    f"Vendido: {kg_vendidos} kg (Prom: ${prom_venta:.2f}/kg)<br>"
                    f"Comprado: {kg_comprados} kg (Prom: ${prom_compra:.2f}/kg)<br>"
                    f"Facturas emitidas: {facturas_ventas}<br>"
                    f"Facturas recibidas: {facturas_compras}<br>"
                    f"Cobros: <b>${cobros:,.2f}</b><br>"
                    f"Pagos: <b>${pagos:,.2f}</b>"
                )
                self.figure.clear()
                ax = self.figure.add_subplot(111)
                ax.pie(
                    [ventas, compras],
                    labels=['Ventas', 'Compras'],
                    autopct='%1.1f%%',
                    colors=['#27ae60', '#2980b9']
                )
                ax.set_title('Distribución Ingresos/Egresos')
                self.canvas.draw()
            else:
                self.label_metricas.setText("No se pudo obtener el cierre contable.")
                self.figure.clear()
                self.canvas.draw()
        except Exception as e:
            self.label_metricas.setText(f"Error de conexión: {str(e)}")
            self.figure.clear()
            self.canvas.draw()

    def generar_y_ver_pdf(self):
        anio = int(self.combo_anio.currentText())
        mes = int(self.combo_mes.currentText())
        url_pdf = f"http://localhost:8000/cierres/pdf/{anio}/{mes}"
        try:
            resp_pdf = requests.get(url_pdf)
            if resp_pdf.status_code == 200:
                file_path, _ = QFileDialog.getSaveFileName(self, "Guardar PDF", f"cierre_{anio}_{mes:02d}.pdf", "PDF Files (*.pdf)")
                if file_path:
                    with open(file_path, 'wb') as f:
                        f.write(resp_pdf.content)
                    QMessageBox.information(self, "Éxito", f"Cierre generado y PDF guardado en:\n{file_path}")
            else:
                QMessageBox.warning(self, "Error", "No se pudo descargar el PDF del cierre.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error de conexión: {str(e)}") 