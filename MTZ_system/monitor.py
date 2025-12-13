import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout,
    QWidget, QLineEdit, QPushButton, QStackedWidget
)
from PyQt6.QtCore import QTimer, Qt
from database import Database

# --- AQUÍ SOLO QUEDA LA VENTANA PRINCIPAL (MONITOR) ---

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sistema MTZ - Control de Acceso")
        self.setGeometry(100, 100, 800, 600)
        self.db = Database()

        self.stacked_widget = QStackedWidget()
        self.setCentralWidget(self.stacked_widget)

        self.pantalla_buscador = self.crear_pantalla_buscador()
        self.stacked_widget.addWidget(self.pantalla_buscador)

        self.pantalla_resultado = self.crear_pantalla_resultado()
        self.stacked_widget.addWidget(self.pantalla_resultado)

        self.timer = QTimer()
        self.timer.setInterval(3000) # 3 segundos
        self.timer.timeout.connect(self.volver_al_inicio)

    def crear_pantalla_buscador(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        titulo = QLabel("Bienvenido a MTZ\nIngrese su DNI")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        titulo.setStyleSheet("font-size: 28px; font-weight: bold; margin-bottom: 20px; color: #eeeeee;")
        layout.addWidget(titulo)

        self.input_dni = QLineEdit()
        self.input_dni.setPlaceholderText("DNI sin puntos")
        self.input_dni.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input_dni.setStyleSheet("QLineEdit { font-size: 24px; padding: 10px; border-radius: 10px; border: 2px solid #555; } QLineEdit:focus { border: 2px solid #0078d7; }")
        self.input_dni.setFixedWidth(300)
        self.input_dni.returnPressed.connect(self.procesar_ingreso)
        layout.addWidget(self.input_dni, alignment=Qt.AlignmentFlag.AlignCenter)

        btn_buscar = QPushButton("INGRESAR")
        btn_buscar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_buscar.setStyleSheet("QPushButton { background-color: #0078d7; color: white; font-size: 18px; padding: 10px 40px; border-radius: 5px; margin-top: 20px; } QPushButton:hover { background-color: #005a9e; }")
        btn_buscar.clicked.connect(self.procesar_ingreso)
        layout.addWidget(btn_buscar, alignment=Qt.AlignmentFlag.AlignCenter)

        self.lbl_error = QLabel("")
        self.lbl_error.setStyleSheet("color: #ff4444; font-size: 18px; margin-top: 15px; font-weight: bold;")
        self.lbl_error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_error)
        
        # --- AQUÍ BORRÉ EL BOTÓN DE ADMINISTRACIÓN ---

        widget.setLayout(layout)
        return widget
    
    def crear_pantalla_resultado(self):
        widget = QWidget()
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.lbl_saludo = QLabel()
        self.lbl_saludo.setStyleSheet("font-size: 40px; font-weight: bold; color: #ffffff;")
        self.lbl_saludo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_saludo)
        
        self.lbl_detalles = QLabel()
        self.lbl_detalles.setStyleSheet("font-size: 24px; color: #cccccc; margin: 20px 0;")
        self.lbl_detalles.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_detalles)
        
        self.lbl_acceso = QLabel()
        self.lbl_acceso.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_acceso)
        
        widget.setLayout(layout)
        return widget

    def procesar_ingreso(self):
        dni = self.input_dni.text().strip()
        if not dni:
            return
        
        datos_socio = self.db.registrar_ingreso(dni)
        
        if datos_socio:
            nombre = datos_socio['nombre']
            apellido = datos_socio['apellido']
            plan = datos_socio['plan']
            ultimo_pago = datos_socio['ultimo_pago']
            restantes = datos_socio['ingresos_restantes']
            acceso_permitido = datos_socio['acceso']

            self.lbl_saludo.setText(f"Bienvenido/a {nombre} {apellido}!")
            self.lbl_detalles.setText(f"Plan: {plan}\nÚltimo pago: {ultimo_pago}")
            
            if acceso_permitido:
                self.lbl_acceso.setText(f"PASE HABILITADO\nTe quedan {restantes} ingresos")
                self.lbl_acceso.setStyleSheet("font-size: 32px; color: #44ff44; font-weight: bold; border: 2px solid #44ff44; padding: 20px; border-radius: 10px;")
            else:
                self.lbl_acceso.setText(f"ACCESO DENEGADO\nSin ingresos disponibles")
                self.lbl_acceso.setStyleSheet("font-size: 32px; color: #ff4444; font-weight: bold; border: 2px solid #ff4444; padding: 20px; border-radius: 10px;")
            
            self.stacked_widget.setCurrentIndex(1)
            self.lbl_error.setText("")
            self.timer.start()
        else:
            self.lbl_error.setText("DNI no encontrado")
            self.input_dni.selectAll()
        
    def volver_al_inicio(self):
        self.timer.stop()
        self.input_dni.clear()
        self.stacked_widget.setCurrentIndex(0)
        self.input_dni.setFocus()

def main():
    db = Database()
    db.crear_tablas()
    
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())
    
if __name__ == "__main__":
    main()