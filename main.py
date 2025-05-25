# cd qt_app; python main.py (Windows)
# cd qt_app && python main.py (Linux)

import os, sys
import aiohttp
import asyncio
from datetime import datetime
import matplotlib
matplotlib.use('QtAgg')  # Usar el backend de Qt6 para matplotlib
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QWidget,
    QLabel,
    QGridLayout,
    QPushButton,
    QDialog,
    QTextEdit,
    QFileDialog,
    QMessageBox
)
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt, QTimer
from matplotlib.backends.backend_pdf import PdfPages

API_BASE_URL = "http://localhost:8000"

class StartWindow(QMainWindow):
    """
    Ventana principal de la aplicación que muestra los gráficos de sensores y permite generar análisis.
    """
    def __init__(self):
        super().__init__()

        # Configuración básica de la ventana
        self.setWindowTitle("Farm_app")
        self.setGeometry(0, 0, 900, 730)
        self.move(320, 40)

        # Configuración del widget central y layout principal
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(10)

        # Inicialización de componentes
        self.setup_background(central_widget)
        self.setup_graphs(central_widget, main_layout)
        self.setup_buttons(main_layout)

        # Inicialización de variables de datos
        self.sensor_data = {}
        self.sensor_descriptions = {}
        self.last_analysis_text = None

        # Carga inicial de datos
        self.update_sensor_descriptions()
        self.update_readings()

    def setup_background(self, central_widget):
        """
        Configura el fondo de la aplicación con una imagen y un overlay oscuro.
        """
        # Configuración de la imagen de fondo
        self.back_label = QLabel(central_widget)
        self.back_label.setScaledContents(True)
        self.back_label.setGeometry(0, 0, 900, 730)
        
        # Carga de la imagen de fondo
        file_route = os.path.abspath(__file__)
        directory = os.path.dirname(file_route)
        init_background = os.path.join(directory, "Fons_app.png")
        
        # Aplicar efecto de oscurecimiento al fondo
        self.pixmap = QPixmap(init_background)
        painter = QPainter(self.pixmap)
        painter.fillRect(self.pixmap.rect(), QColor(0, 0, 0, 128))
        painter.end()
        
        self.back_label.setPixmap(self.pixmap)
        self.back_label.lower()

        # Añadir overlay oscuro para mejorar la legibilidad
        self.overlay = QLabel(central_widget)
        self.overlay.setGeometry(0, 0, 900, 730)
        self.overlay.setStyleSheet("background-color: rgba(0, 0, 0, 0.3);")
        self.overlay.lower()

    def setup_graphs(self, central_widget, main_layout):
        """
        Configura los gráficos para mostrar los datos de los sensores.
        """
        # Contenedor para la cuadrícula de gráficos
        grid_container = QWidget(central_widget)
        grid_layout = QGridLayout(grid_container)
        grid_layout.setContentsMargins(60, 5, 60, 20)
        grid_layout.setSpacing(30)

        # Inicialización de gráficos para cada sensor
        self.sensor_canvases = {}
        self.sensor_axes = {}
        self.sensor_figures = {}
        for idx, sensor_id in enumerate(range(1, 7)):
            # Configuración de cada gráfico
            fig = Figure(figsize=(6, 2), dpi=100)
            canvas = FigureCanvas(fig)
            ax = fig.add_subplot(111)
            ax.grid(True)
            ax.tick_params(axis='x', labelsize=6)
            ax.tick_params(axis='y', labelsize=6)
            fig.subplots_adjust(left=0.18, right=0.95, top=0.82, bottom=0.18)
            
            # Almacenamiento de referencias
            self.sensor_canvases[sensor_id] = canvas
            self.sensor_axes[sensor_id] = ax
            self.sensor_figures[sensor_id] = fig
            
            # Posicionamiento en la cuadrícula
            row = idx // 2
            col = idx % 2
            grid_layout.addWidget(canvas, row, col)

        main_layout.addWidget(grid_container)
        main_layout.setSpacing(0)

    def setup_buttons(self, main_layout):
        """
        Configura los botones de la interfaz.
        """
        # Contenedor para los botones
        button_container = QWidget()
        button_layout = QGridLayout(button_container)
        button_layout.setContentsMargins(60, 0, 60, 0)
        button_layout.setSpacing(30)
        
        # Botón de análisis IA
        self.ia_button = QPushButton("Generar análisis IA")
        self.ia_button.clicked.connect(self.on_generate_analysis)
        self.ia_button.setStyleSheet(
            """
            QPushButton {
                background-color: #FF1493;
                color: black;
                border: 1px solid black;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #C71585;
                color: black;
            }
        """
        )

        # Botón de exportar PDF
        self.export_pdf_button = QPushButton("Exportar PDF")
        self.export_pdf_button.setStyleSheet(
            """
            QPushButton {
                background-color: #00FFFF;
                color: black;
                border: 1px solid black;
                border-radius: 5px;
                padding: 10px 20px;
                font-size: 14px;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #87CEEB;
                color: black;
            }
        """
        )
        self.export_pdf_button.setEnabled(False)
        self.export_pdf_button.clicked.connect(self.on_export_pdf)
        
        # Posicionamiento de botones
        button_layout.addWidget(self.ia_button, 0, 0)
        button_layout.addWidget(self.export_pdf_button, 0, 1)
        
        main_layout.addWidget(button_container)

    def update_sensor_descriptions(self):
        """
        Actualiza las descripciones de los sensores y refresca los gráficos.
        """
        try:
            descriptions = asyncio.run(self.fetch_sensor_descriptions())
            for sensor in descriptions:
                self.sensor_descriptions[sensor['id']] = sensor['description']
            self.update_all_graphs()
        except Exception as e:
            print(f"Error en la actualización de descripciones de sensores: {str(e)}")

    async def fetch_sensor_descriptions(self):
        """
        Obtiene las descripciones de los sensores desde la API.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'{API_BASE_URL}/enviroment_readings/sensors/') as response:
                    if response.status == 200:
                        return await response.json()
                    return []
        except Exception as e:
            print(f"Error en la obtención de descripciones de sensores: {str(e)}")
            return []

    def update_readings(self):
        """
        Actualiza las lecturas de todos los sensores y tags.
        """
        try:
            # Obtener lecturas de sensores ambientales
            for sensor_id in range(1, 6):
                readings = asyncio.run(self.fetch_sensor_readings(sensor_id))
                if readings:
                    self.sensor_data[sensor_id] = readings[-20:]
            
            # Obtener lecturas de tags
            tag_readings = asyncio.run(self.fetch_tag_readings())
            if tag_readings:
                self.sensor_data[6] = tag_readings[-20:]
            
            self.update_all_graphs()
        except Exception as e:
            print(f"Error en la actualización de lecturas: {str(e)}")

    async def fetch_sensor_readings(self, sensor_id):
        """
        Obtiene las lecturas de un sensor específico desde la API.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'{API_BASE_URL}/enviroment_readings/{sensor_id}') as response:
                    if response.status == 200:
                        return await response.json()
                    return []
        except Exception as e:
            print(f"Error en la obtención de datos del sensor {sensor_id}: {str(e)}")
            return []

    async def fetch_tag_readings(self):
        """
        Obtiene las lecturas de tags desde la API.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(f'{API_BASE_URL}/tag_readings/') as response:
                    if response.status == 200:
                        return await response.json()
                    return []
        except Exception as e:
            print(f"Error en la obtención de lecturas de tags: {str(e)}")
            return []

    def update_all_graphs(self):
        """
        Actualiza todos los gráficos con los datos más recientes.
        """
        for sensor_id in range(1, 7):
            ax = self.sensor_axes[sensor_id]
            fig = self.sensor_figures[sensor_id]
            ax.clear()
            
            if sensor_id == 6:
                # Gráfico especial para tags
                ax.set_title("Lecturas de Tags", fontsize=12)
                ax.grid(True)
                data = self.sensor_data.get(sensor_id, [])
                if data:
                    timestamps = [datetime.fromisoformat(d['timestamp'].replace('Z', '+00:00')) for d in data]
                    counts = list(range(1, len(timestamps) + 1))
                    ax.plot(timestamps, counts, marker='o')
                    ax.set_ylabel('Número total de lecturas')
            else:
                # Gráficos para sensores ambientales
                title = self.sensor_descriptions.get(sensor_id, f'Sensor {sensor_id}')
                ax.set_title(title)
                ax.grid(True)
                data = self.sensor_data.get(sensor_id, [])
                if data:
                    values = [d['value'] for d in data]
                    timestamps = [datetime.fromisoformat(d['timestamp'].replace('Z', '+00:00')) for d in data]
                    if len(values) > 1:
                        ax.plot(timestamps, values, marker='o')
                    else:
                        ax.plot(timestamps, values, marker='o', linestyle='None')
            fig.autofmt_xdate()
            self.sensor_canvases[sensor_id].draw()

    def on_generate_analysis(self):
        """
        Inicia el proceso de generación de análisis.
        """
        self.ia_button.setEnabled(False)
        self.ia_button.setText("Procesando...")
        
        try:
            import requests
            resp = requests.post(f"{API_BASE_URL}/data_analysis/process")
            if resp.status_code not in (200, 201, 204):
                self.show_analysis_dialog(f"Error en la iniciación del análisis: {resp.status_code}")
                self.ia_button.setEnabled(True)
                self.ia_button.setText("Generar análisis IA")
                return

            # Timer para verificar el resultado
            self.analysis_timer = QTimer()
            self.analysis_timer.timeout.connect(self.check_analysis_result)
            self.analysis_timer.start(5000)  # Verificar cada 5 segundos

        except Exception as e:
            self.show_analysis_dialog(f"Error en la generación del análisis: {str(e)}")
            self.ia_button.setEnabled(True)
            self.ia_button.setText("Generar análisis IA")

    def check_analysis_result(self):
        """
        Verifica si el análisis está listo y muestra el resultado.
        """
        try:
            import requests
            resp = requests.get(f"{API_BASE_URL}/data_analysis/latest")
            if resp.status_code == 200:
                data = resp.json()
                texto = data.get("analysis", str(data))
                self.last_analysis_text = texto
                self.export_pdf_button.setEnabled(True)
                self.show_analysis_dialog(texto)
                self.analysis_timer.stop()
                self.ia_button.setEnabled(True)
                self.ia_button.setText("Generar análisis IA")
            elif resp.status_code == 404:
                # Si no hay análisis aún, continuar esperando
                pass
            else:
                self.show_analysis_dialog(f"Error en la obtención del análisis: {resp.status_code}")
                self.analysis_timer.stop()
                self.ia_button.setEnabled(True)
                self.ia_button.setText("Generar análisis IA")
        except Exception as e:
            self.show_analysis_dialog(f"Error en la verificación del análisis: {str(e)}")
            self.analysis_timer.stop()
            self.ia_button.setEnabled(True)
            self.ia_button.setText("Generar análisis IA")

    def show_analysis_dialog(self, text):
        """
        Muestra el diálogo con el análisis generado.
        """
        dialog = QDialog(self)
        dialog.setWindowTitle("Weekly Report")
        dialog.setMinimumSize(600, 300)
        layout = QVBoxLayout(dialog)
        text_edit = QTextEdit()
        text_edit.setReadOnly(True)
        text_edit.setStyleSheet("""
            QTextEdit {
                font-size: 14px;
                line-height: 1.5;
                padding: 20px;
            }
        """)
        
        # Procesamiento del texto
        if isinstance(text, dict):
            if 'analysis' in text:
                analysis_data = text['analysis']
            else:
                analysis_data = text
                
            report = analysis_data.get('report', '')
            report = report.replace('\\n', '\n')
            report = report.replace('{', '').replace('}', '')
            report = report.replace('[', '').replace(']', '')
            report = report.replace('"', '').replace("'", '')
            
            if "Recommendations:" in report:
                report = report.split("Recommendations:")[0].strip()
            
            formatted_text = report
        else:
            formatted_text = str(text)
            
        text_edit.setText(formatted_text)
        layout.addWidget(text_edit)
        dialog.setLayout(layout)
        dialog.exec()

    def on_export_pdf(self):
        """
        Exporta el análisis y los gráficos a un archivo PDF.
        """
        if not self.last_analysis_text:
            QMessageBox.warning(self, "Error", "No hay análisis para exportar.")
            return
        file_path, _ = QFileDialog.getSaveFileName(self, "Guardar PDF", "analisis.pdf", "PDF Files (*.pdf)")
        if not file_path:
            return
        try:
            with PdfPages(file_path) as pdf:
                # Gráficos de sensores
                fig, axs = plt.subplots(3, 2, figsize=(12, 10))
                sensor_ids = list(self.sensor_axes.keys())
                for idx, sensor_id in enumerate(sensor_ids):
                    ax = axs[idx // 2, idx % 2]
                    if sensor_id == 6:
                        # Gráfico de tags
                        ax.set_title("Lecturas de Tags", fontsize=10)
                        ax.grid(True)
                        data = self.sensor_data.get(sensor_id, [])
                        if data:
                            timestamps = [datetime.fromisoformat(d['timestamp'].replace('Z', '+00:00')) for d in data]
                            counts = list(range(1, len(timestamps) + 1))
                            ax.plot(timestamps, counts, marker='o')
                            ax.set_ylabel('Número total de lecturas')
                    else:
                        # Gráficos de sensores ambientales
                        data = self.sensor_data.get(sensor_id, [])
                        title = self.sensor_descriptions.get(sensor_id, f'Sensor {sensor_id}')
                        ax.set_title(title)
                        ax.grid(True)
                        if data:
                            values = [d['value'] for d in data]
                            timestamps = [datetime.fromisoformat(d['timestamp'].replace('Z', '+00:00')) for d in data]
                            if len(values) > 1:
                                ax.plot(timestamps, values, marker='o')
                            else:
                                ax.plot(timestamps, values, marker='o', linestyle='None')
                    fig.autofmt_xdate()
                fig.suptitle('Análisis', fontsize=16)
                pdf.savefig(fig, bbox_inches='tight')
                plt.close(fig)

                # Página de texto con el análisis
                fig2 = Figure(figsize=(8.5, 11))
                ax2 = fig2.add_subplot(111)
                ax2.axis('off')
                ax2.text(0.5, 0.98, 'Informe d\'Anàlisi', fontsize=18, ha='center', va='top', fontweight='bold')
                
                # Formatear el texto del análisis para el PDF
                if isinstance(self.last_analysis_text, dict):
                    if 'analysis' in self.last_analysis_text:
                        analysis_data = self.last_analysis_text['analysis']
                        if isinstance(analysis_data, dict) and 'report' in analysis_data:
                            report = analysis_data['report']
                        else:
                            report = str(analysis_data)
                    elif 'report' in self.last_analysis_text:
                        report = self.last_analysis_text['report']
                    else:
                        report = str(self.last_analysis_text)
                else:
                    report = str(self.last_analysis_text)

                # Limpiar el texto
                report = report.replace('"', '').replace("'", '')
                report = report.replace('{', '').replace('}', '')
                report = report.replace('[', '').replace(']', '')
                report = report.replace('\\n', '\n')
                
                # Eliminar la parte de recomendaciones si existe
                if "Recommendations:" in report:
                    report = report.split("Recommendations:")[0].strip()
                
                formatted_text = report
                
                ax2.text(0.02, 0.92, formatted_text, fontsize=12, ha='left', va='top', wrap=True)
                pdf.savefig(fig2, bbox_inches='tight')
                plt.close(fig2)
            QMessageBox.information(self, "Éxito", f"PDF guardado en: {file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error en la generación del PDF: {str(e)}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = StartWindow()
    window.show()
    sys.exit(app.exec())