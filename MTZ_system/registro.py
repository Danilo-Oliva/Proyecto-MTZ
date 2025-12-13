import sys
from PyQt6.QtWidgets import (
    QApplication, QDialog, QFormLayout, QLineEdit, 
    QComboBox, QSpinBox, QPushButton, QMessageBox, QLabel
)
from database import Database
from datetime import datetime

# --- TU LÓGICA INTACTA ---
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
        
        # Conectamos el cambio de plan a la función
        self.combo_actividad.currentTextChanged.connect(self.actualizar_pases)

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
        
        existe, activo = self.db.verificar_dni_existente(dni)
        
        if existe:
            if activo == 1:
                # Caso A: El socio ya existe y está activo -> Error normal
                QMessageBox.critical(self, "Error", "Ese DNI ya está registrado y activo.")
                return
            else:
                # Caso B: El socio existe pero estaba ELIMINADO -> Preguntar reactivación
                respuesta = QMessageBox.question(
                    self, "Socio Encontrado",
                    f"El DNI {dni} pertenece a un socio inactivo.\n¿Deseas REACTIVARLO con este nuevo plan?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                
                if respuesta == QMessageBox.StandardButton.Yes:
                    if self.db.reactivar_socio(nombre, apellido, dni, plan_nombre, ingresos):
                        QMessageBox.information(self, "Reactivado", "¡Socio reactivado exitosamente!")
                        self.accept()
                    else:
                        QMessageBox.critical(self, "Error", "No se pudo reactivar.")
                return
        
        exito = self.db.registrar_socio(nombre, apellido, dni, plan_nombre, ingresos)
        
        if exito:
            QMessageBox.information(self, "Éxito", f"Socio {nombre} {apellido} registrado correctamente.")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "No se pudo registrar. ¿Quizás el DNI ya existe?")

# Esto permite probar este archivo solo si quieres
if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaRegistro()
    ventana.show()
    sys.exit(app.exec())