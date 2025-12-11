import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout,
    QWidget, QLineEdit, QPushButton, QStackedWidget,
    QDialog, QFormLayout, QSpinBox, QComboBox, QMessageBox
)
from PyQt6.QtCore import QTimer, Qt
from database import Database

class VentanaRegistro(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Nuevo Socio - MTZ")
        self.setFixedSize(400, 300)
        self.db = Database()
        
        layout = QFormLayout()
        
        self.input_nombre = QLineEdit()
        self.input_apellido = QLineEdit()
        self.input_dni = QLineEdit()
        self.input_dni.setPlaceholderText("Solo números")
        
        # --- PLANES ---
        self.combo_actividad = QComboBox()
        planes = self.db.obtener_planes()
        if planes:
            self.combo_actividad.addItems(planes)
        else:
            self.combo_actividad.addItem("Sin planes cargados")
        
        # Conectamos el cambio de plan a la función mágica         self.combo_actividad.currentTextChanged.connect(self.actualizar_pases)

        # --- PASES (SPINBOX) ---
        self.spin_ingresos = QSpinBox()
        self.spin_ingresos.setRange(0, 60) # Pongo 0 por si es ilimitado
        self.spin_ingresos.setValue(30)    # Valor inicial (Libre)
        
        self.btn_guardar = QPushButton("Registrar Socio")
        self.btn_guardar.setStyleSheet("background-color: #28a745; color: white; padding: 10px; font-weight: bold;")
        self.btn_guardar.clicked.connect(self.guardar_socio)
        
        layout.addRow("Nombre: ", self.input_nombre)
        layout.addRow("Apellido:", self.input_apellido)
        layout.addRow("DNI:", self.input_dni)
        layout.addRow("Planes:", self.combo_actividad)
        layout.addRow("Pases Iniciales:", self.spin_ingresos)
        layout.addRow(self.btn_guardar)
        
        self.setLayout(layout)
        
        # Llamamos a la función una vez al inicio para configurar el primer valor
        self.actualizar_pases() 

    def actualizar_pases(self):
        """Cambia el número de pases según el plan elegido"""
        plan = self.combo_actividad.currentText()
        
        if "Libre" in plan and "Pase Libre" not in plan: # Solo "Libre"
            self.spin_ingresos.setValue(30)
        elif "3 veces" in plan:
            self.spin_ingresos.setValue(12) # 4 semanas * 3 veces = 12 clases
        elif "Pase Libre" in plan:
             self.spin_ingresos.setValue(30)
        else:
            self.spin_ingresos.setValue(12) # Por defecto para el resto

    def guardar_socio(self):
        nombre = self.input_nombre.text().strip()
        apellido = self.input_apellido.text().strip()
        dni = self.input_dni.text().strip()
        plan_nombre = self.combo_actividad.currentText()
        ingresos = self.spin_ingresos.value()
        
        if not nombre or not apellido or not dni:
            QMessageBox.warning(self, "Error", "Por favor complete todos los campos.")
            return
        
        exito = self.db.registrar_socio(nombre, apellido, dni, plan_nombre, ingresos)
        
        if exito:
            QMessageBox.information(self, "Éxito", f"Socio {nombre} {apellido} registrado correctamente.")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "No se pudo registrar. ¿Quizás el DNI ya existe?")

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
        
        btn_admin = QPushButton("ADMINISTRACIÓN")
        btn_admin.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_admin.setStyleSheet("background-color: #444; color: #aaa; border: none; font-size: 12px; margin-top: 50px;")
        btn_admin.clicked.connect(self.abrir_admin)
        layout.addWidget(btn_admin)

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
        
    def abrir_admin(self):
        dialogo = VentanaRegistro()
        dialogo.exec()

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