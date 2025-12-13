import sys
from PyQt6.QtWidgets import (
    QWidget, QDialog, QVBoxLayout, QLineEdit, QPushButton,
    QHBoxLayout, QTableWidget, QTableWidgetItem, 
    QHeaderView, QMessageBox, QLabel, QComboBox, 
    QSpinBox, QFormLayout, QAbstractSpinBox
)
from PyQt6.QtCore import Qt
from database import Database

# --- LAS VENTANAS PEQUEÑAS SIGUEN SIENDO DIALOGOS (FLOTANTES) ---
class VentanaEdicion(QDialog):
    def __init__(self, id_socio, nombre, apellido, dni, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Editar Datos del Socio")
        self.setFixedSize(400, 300)
        self.id_socio = id_socio
        self.db = Database()

        # Estilo Oscuro (Pop-up)
        self.setStyleSheet("""
            QDialog { background-color: #2b2b2b; color: white; }
            QLabel { color: white; font-weight: bold; font-size: 14px; }
            QLineEdit {
                background-color: #404040; color: white;
                border: 1px solid #666; padding: 8px; border-radius: 4px; font-size: 14px;
            }
        """)

        layout = QFormLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        self.input_nombre = QLineEdit(nombre)
        self.input_apellido = QLineEdit(apellido)
        self.input_dni = QLineEdit(dni)
        self.input_dni.setPlaceholderText("Solo números")

        btn_guardar = QPushButton("GUARDAR CAMBIOS")
        btn_guardar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_guardar.setStyleSheet("""
            QPushButton {
                background-color: #f39c12; color: white; padding: 12px;
                font-weight: bold; border-radius: 5px; border: none; margin-top: 15px;
            }
            QPushButton:hover { background-color: #e67e22; }
        """)
        btn_guardar.clicked.connect(self.guardar_cambios)

        layout.addRow("Nombre:", self.input_nombre)
        layout.addRow("Apellido:", self.input_apellido)
        layout.addRow("DNI:", self.input_dni)
        layout.addRow("", btn_guardar)

        self.setLayout(layout)

    def guardar_cambios(self):
        nuevo_nombre = self.input_nombre.text().strip()
        nuevo_apellido = self.input_apellido.text().strip()
        nuevo_dni = self.input_dni.text().strip()

        if not nuevo_nombre or not nuevo_apellido or not nuevo_dni:
            QMessageBox.warning(self, "Error", "Ningún campo puede quedar vacío.")
            return

        exito = self.db.editar_socio(self.id_socio, nuevo_nombre, nuevo_apellido, nuevo_dni)
        if exito:
            QMessageBox.information(self, "Éxito", "Datos actualizados correctamente.")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "No se pudo guardar.\n¿Quizás el DNI ya lo usa otro socio?")

class VentanaRenovacion(QDialog):
    def __init__(self, id_socio, nombre_socio, parent=None):
        super().__init__(parent)
        self.setWindowTitle(f"Renovar: {nombre_socio}")
        self.setFixedSize(400, 300)
        self.id_socio = id_socio
        self.db = Database()

        # Estilo Oscuro (Pop-up)
        self.setStyleSheet("""
            QDialog { background-color: #2b2b2b; color: white; }
            QLabel { color: white; font-weight: bold; font-size: 14px; }
            QComboBox, QSpinBox {
                background-color: #404040; color: white;
                border: 1px solid #666; padding: 8px; border-radius: 4px; font-size: 14px;
            }
            QComboBox::drop-down { border: 0px; }
            QSpinBox { padding-right: 0px; }
        """)

        layout = QFormLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(15)

        self.combo_plan = QComboBox()
        self.combo_plan.addItems(self.db.obtener_planes())
        self.combo_plan.currentTextChanged.connect(self.actualizar_pases)

        self.spin_pases = QSpinBox()
        self.spin_pases.setRange(0, 999)
        self.spin_pases.setButtonSymbols(QAbstractSpinBox.ButtonSymbols.NoButtons)
        
        btn_confirmar = QPushButton("CONFIRMAR PAGO")
        btn_confirmar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_confirmar.setStyleSheet("""
            QPushButton {
                background-color: #27ae60; color: white; padding: 12px;
                font-weight: bold; border-radius: 5px; border: none; margin-top: 15px;
            }
            QPushButton:hover { background-color: #2ecc71; }
        """)
        btn_confirmar.clicked.connect(self.confirmar_renovacion)

        layout.addRow("Plan a Pagar:", self.combo_plan)
        layout.addRow("Sumar Pases:", self.spin_pases)
        layout.addRow("", btn_confirmar)

        self.setLayout(layout)
        self.actualizar_pases() 

    def actualizar_pases(self):
        plan = self.combo_plan.currentText()
        if "Libre" in plan and "Pase Libre" not in plan:
            self.spin_pases.setValue(30)
        elif "3 veces" in plan:
            self.spin_pases.setValue(12)
        elif "Pase Libre" in plan:
             self.spin_pases.setValue(30)
        else:
            self.spin_pases.setValue(12)

    def confirmar_renovacion(self):
        plan = self.combo_plan.currentText()
        pases = self.spin_pases.value()
        exito = self.db.renovar_socio(self.id_socio, plan, pases)
        if exito:
            QMessageBox.information(self, "Pago Registrado", "La cuota se renovó correctamente.")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", "No se pudo renovar la cuota.")

#TABLA PRINCIPAL
class VentanaGestion(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Estilos adaptados para fondo CLARO (Panel blanco)
        self.setStyleSheet("""
            QWidget { background-color: transparent; }
            QLineEdit {
                background-color: white; color: #333; border: 1px solid #ccc;
                padding: 8px; border-radius: 4px; font-size: 14px;
            }
            QPushButton {
                padding: 8px 12px; border-radius: 4px; font-weight: bold; border: none;
            }
            QTableWidget {
                background-color: white; color: #333; gridline-color: #ccc;
                border: 1px solid #ccc; font-size: 13px;
            }
            QHeaderView::section {
                background-color: #eee; color: #333; padding: 5px; border: 1px solid #ccc;
            }
            QTableWidget::item:selected { background-color: #3498db; color: white; }
        """)

        self.db = Database()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Título Interno
        lbl_titulo = QLabel("Gestión de Socios")
        lbl_titulo.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        layout.addWidget(lbl_titulo)

        # Buscador
        layout_buscar = QHBoxLayout()
        self.input_buscar = QLineEdit()
        self.input_buscar.setPlaceholderText("Buscar por Nombre, Apellido o DNI...")
        self.input_buscar.textChanged.connect(self.cargar_socios)
        
        btn_refrescar = QPushButton("🔄")
        btn_refrescar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refrescar.setStyleSheet("background-color: #3498db; color: white;")
        btn_refrescar.setFixedWidth(40)
        btn_refrescar.clicked.connect(self.cargar_socios)

        layout_buscar.addWidget(self.input_buscar)
        layout_buscar.addWidget(btn_refrescar)
        layout.addLayout(layout_buscar)

        # Tabla
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6)
        self.tabla.setHorizontalHeaderLabels(["ID", "Nombre", "Apellido", "DNI", "Plan", "Pases"])
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.tabla.setColumnHidden(0, True) 
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        layout.addWidget(self.tabla)

        # Botones
        layout_botones = QHBoxLayout()
        
        btn_editar = QPushButton("✏️ Editar")
        btn_editar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_editar.setStyleSheet("background-color: #f39c12; color: white;")
        btn_editar.clicked.connect(self.accion_editar)
        
        btn_renovar = QPushButton("💰 Renovar Cuota")
        btn_renovar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_renovar.setStyleSheet("background-color: #27ae60; color: white;")
        btn_renovar.clicked.connect(self.accion_renovar)
        
        btn_borrar = QPushButton("🗑️ Eliminar") 
        btn_borrar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_borrar.setStyleSheet("background-color: #c0392b; color: white;")
        btn_borrar.clicked.connect(self.accion_borrar)

        layout_botones.addWidget(btn_editar)
        layout_botones.addWidget(btn_renovar)
        layout_botones.addWidget(btn_borrar)
        layout.addLayout(layout_botones)

        self.setLayout(layout)
        self.cargar_socios()

    def cargar_socios(self):
        filtro = self.input_buscar.text().strip()
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor()
            sql = """
                SELECT m.id, m.nombre, m.apellido, m.dni, p.nombre, m.ingresos_restantes 
                FROM miembros m
                LEFT JOIN planes p ON m.plan_id = p.id
                WHERE m.activo = 1 AND (m.nombre LIKE ? OR m.apellido LIKE ? OR m.dni LIKE ?)
                ORDER BY m.id DESC
            """
            param = f"%{filtro}%"
            cursor.execute(sql, (param, param, param))
            resultados = cursor.fetchall()
            
            self.tabla.setRowCount(0)
            for row_idx, datos in enumerate(resultados):
                self.tabla.insertRow(row_idx)
                for col_idx, dato in enumerate(datos):
                    item = QTableWidgetItem(str(dato))
                    if col_idx in [3, 5]: 
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tabla.setItem(row_idx, col_idx, item)
            conn.close()

    def accion_renovar(self):
        fila = self.tabla.currentRow()
        if fila == -1:
            QMessageBox.warning(self, "Atención", "Por favor, selecciona un socio de la tabla.")
            return

        id_socio = self.tabla.item(fila, 0).text()
        nombre = self.tabla.item(fila, 1).text()
        apellido = self.tabla.item(fila, 2).text()

        # Dialogo FLOTANTE (se mantiene QDialog)
        dialogo = VentanaRenovacion(id_socio, f"{nombre} {apellido}", self)
        if dialogo.exec():
            self.cargar_socios()
    
    def accion_editar(self):
        fila = self.tabla.currentRow()
        if fila == -1:
            QMessageBox.warning(self, "Atención", "Selecciona un socio para editar.")
            return

        id_socio = self.tabla.item(fila, 0).text()
        nombre = self.tabla.item(fila, 1).text()
        apellido = self.tabla.item(fila, 2).text()
        dni = self.tabla.item(fila, 3).text()

        # Dialogo FLOTANTE (se mantiene QDialog)
        dialogo = VentanaEdicion(id_socio, nombre, apellido, dni, self)
        if dialogo.exec():
            self.cargar_socios()

    def accion_borrar(self):
        fila = self.tabla.currentRow()
        if fila == -1:
            QMessageBox.warning(self, "Atención", "Selecciona un socio para eliminar.")
            return

        id_socio = self.tabla.item(fila, 0).text()
        nombre = self.tabla.item(fila, 1).text()
        apellido = self.tabla.item(fila, 2).text()

        confirmacion = QMessageBox.question(
            self, "Confirmar Eliminación",
            f"¿Estás seguro de que deseas eliminar a {nombre} {apellido}?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )

        if confirmacion == QMessageBox.StandardButton.Yes:
            if self.db.eliminar_socio(id_socio):
                QMessageBox.information(self, "Eliminado", "El socio ha sido eliminado correctamente.")
                self.cargar_socios()
            else:
                QMessageBox.critical(self, "Error", "No se pudo eliminar al socio.")

if __name__ == "__main__":
    app = sys.modules.get('PyQt6.QtWidgets').QApplication(sys.argv)
    ventana = VentanaGestion()
    ventana.show()
    sys.exit(app.exec())