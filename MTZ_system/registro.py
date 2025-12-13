import sys
from PyQt6.QtWidgets import (
    QWidget, QFormLayout, QLineEdit,
    QComboBox, QSpinBox, QPushButton, QMessageBox, QLabel,
    QVBoxLayout, QAbstractSpinBox
)
from PyQt6.QtCore import Qt
from database import Database

class VentanaRegistro(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.db = Database()
        
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(40, 40, 40, 40)
        
        # Título Interno
        lbl_titulo = QLabel("Registrar Nuevo Socio")
        lbl_titulo.setStyleSheet("font-size: 24px; font-weight: bold; color: #333; margin-bottom: 20px;")
        main_layout.addWidget(lbl_titulo)

        # Layout del Formulario
        form_layout = QFormLayout()
        form_layout.setSpacing(20)
        
        # Estilos adaptados para fondo blanco (Panel)
        self.setStyleSheet("""
            QWidget { background-color: transparent; }
            QLabel { color: #333; font-size: 14px; font-weight: bold; }
            QLineEdit, QComboBox, QSpinBox {
                background-color: white; color: #333; border: 1px solid #ccc;
                padding: 8px; border-radius: 4px; font-size: 14px; min-width: 300px;
            }
            QLineEdit:focus, QComboBox:focus, QSpinBox:focus {
                border: 2px solid #3498db;
            }
        """)
        
        self.input_nombre = QLineEdit()
        self.input_apellido = QLineEdit()
        self.input_dni = QLineEdit()
        self.input_dni.setPlaceholderText("Solo números")
        
        self.combo_actividad = QComboBox()
        planes = self.db.obtener_planes()
        if planes:
            self.combo_actividad.addItems(planes)
        else:
            self.combo_actividad.addItem("Sin planes cargados")
        
        self.combo_actividad.currentTextChanged.connect(self.actualizar_pases)

        self.spin_ingresos = QSpinBox()
        self.spin_ingresos.setRange(0, 999)
        self.spin_ingresos.setValue(30)
        self.spin_ingresos.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        
        self.btn_guardar = QPushButton("GUARDAR FICHA")
        self.btn_guardar.setCursor(Qt.CursorShape.PointingHandCursor)
        self.btn_guardar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60; color: white; padding: 12px;
                font-weight: bold; border-radius: 5px; font-size: 14px; border: none; margin-top: 20px;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        self.btn_guardar.clicked.connect(self.guardar_socio)
        
        form_layout.addRow("Nombre:", self.input_nombre)
        form_layout.addRow("Apellido:", self.input_apellido)
        form_layout.addRow("DNI:", self.input_dni)
        form_layout.addRow("Plan:", self.combo_actividad)
        form_layout.addRow("Pases:", self.spin_ingresos)
        form_layout.addRow("", self.btn_guardar)
        
        main_layout.addLayout(form_layout)
        main_layout.addStretch()
        self.setLayout(main_layout)
        
        self.actualizar_pases() 

    def actualizar_pases(self):
        plan = self.combo_actividad.currentText()
        if "Libre" in plan and "Pase Libre" not in plan:
            self.spin_ingresos.setValue(30)
        elif "3 veces" in plan:
            self.spin_ingresos.setValue(12)
        elif "Pase Libre" in plan:
             self.spin_ingresos.setValue(30)
        else:
            self.spin_ingresos.setValue(12)

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
                QMessageBox.critical(self, "Error", "Ese DNI ya está registrado y activo.")
                return
            else:
                respuesta = QMessageBox.question(
                    self, "Socio Encontrado",
                    f"El DNI {dni} pertenece a un socio inactivo.\n¿Deseas REACTIVARLO con este nuevo plan?",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                    QMessageBox.StandardButton.Yes
                )
                
                if respuesta == QMessageBox.StandardButton.Yes:
                    if self.db.reactivar_socio(nombre, apellido, dni, plan_nombre, ingresos):
                        QMessageBox.information(self, "Reactivado", "¡Socio reactivado exitosamente!")
                        self.limpiar_formulario() 
                    else:
                        QMessageBox.critical(self, "Error", "No se pudo reactivar.")
                return
        
        exito = self.db.registrar_socio(nombre, apellido, dni, plan_nombre, ingresos)
        
        if exito:
            QMessageBox.information(self, "Éxito", f"Socio {nombre} {apellido} registrado correctamente.")
            self.limpiar_formulario()
        else:
            QMessageBox.critical(self, "Error", "No se pudo registrar. ¿Quizás el DNI ya existe?")

    def limpiar_formulario(self):
        self.input_nombre.clear()
        self.input_apellido.clear()
        self.input_dni.clear()
        self.actualizar_pases()

if __name__ == "__main__":
    app = sys.modules.get('PyQt6.QtWidgets').QApplication(sys.argv)
    ventana = VentanaRegistro()
    ventana.show()
    sys.exit(app.exec())