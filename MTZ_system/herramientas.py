import sys
import csv
import shutil
import os
from datetime import datetime
from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QLabel, 
    QMessageBox, QFileDialog, QFrame, QApplication
)
from PyQt6.QtCore import Qt
from database import Database

class VentanaHerramientas(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Herramientas del Sistema")
        self.setFixedSize(450, 400)
        self.setStyleSheet("background-color: #f0f0f0;")
        
        self.db = Database()
        
        layout = QVBoxLayout()
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Título
        lbl_titulo = QLabel("Mantenimiento de Datos")
        lbl_titulo.setStyleSheet("font-size: 20px; font-weight: bold; color: #333; margin-bottom: 10px;")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_titulo)

        # --- SECCIÓN 1: EXPORTAR ---
        btn_csv = QPushButton("  📄 Descargar Lista de Socios (.csv)")
        btn_csv.setStyleSheet(self.estilo_boton("#3498db"))
        btn_csv.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_csv.clicked.connect(self.exportar_socios)
        layout.addWidget(btn_csv)

        # --- SECCIÓN 2: BACKUP ---
        btn_backup = QPushButton("  💾 Crear Respaldo de Base de Datos")
        btn_backup.setStyleSheet(self.estilo_boton("#27ae60"))
        btn_backup.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_backup.clicked.connect(self.crear_backup)
        layout.addWidget(btn_backup)
        
        # Texto de ayuda
        lbl_info = QLabel("Estas herramientas generan archivos externos.\nGuárdalos en una ubicación segura.")
        lbl_info.setStyleSheet("color: #777; font-size: 13px; margin-top: 20px;")
        lbl_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_info)
        
        layout.addStretch()
        self.setLayout(layout)

    def estilo_boton(self, color):
        return f"""
            QPushButton {{
                background-color: {color}; 
                color: white; 
                padding: 15px; 
                border-radius: 8px; 
                font-weight: bold; 
                font-size: 14px;
                border: none;
                text-align: left;
                padding-left: 30px;
            }}
            QPushButton:hover {{ background-color: {color}AA; }}
        """

    def exportar_socios(self):
        fecha = datetime.now().strftime("%Y-%m-%d")
        nombre_default = f"Socios_MTZ_{fecha}.csv"
        archivo, _ = QFileDialog.getSaveFileName(self, "Guardar Lista de Socios", nombre_default, "Archivos CSV (*.csv)")
        
        if not archivo: return

        conn = self.db.conectar()
        cursor = conn.cursor()
        cursor.execute("""
            SELECT m.nombre, m.apellido, m.dni, p.nombre, m.ingresos_restantes, m.fecha_vencimiento, m.activo
            FROM miembros m
            LEFT JOIN planes p ON m.plan_id = p.id
        """)
        datos = cursor.fetchall()
        conn.close()

        try:
            with open(archivo, mode='w', newline='', encoding='utf-8-sig') as file:
                writer = csv.writer(file, delimiter=';')
                writer.writerow(["Nombre", "Apellido", "DNI", "Plan", "Pases Restantes", "Vencimiento", "Activo"])
                for fila in datos:
                    estado = "SI" if fila[6] else "NO"
                    writer.writerow([fila[0], fila[1], fila[2], fila[3], fila[4], fila[5], estado])
            QMessageBox.information(self, "Éxito", "La lista se exportó correctamente.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"No se pudo guardar.\nError: {e}")

    def crear_backup(self):
        ruta_db_original = self.db.db_path
        if not os.path.exists(ruta_db_original):
            QMessageBox.critical(self, "Error", "No encuentro la base de datos original.")
            return

        fecha = datetime.now().strftime("%Y-%m-%d")
        nombre_default = f"Respaldo_MTZ_{fecha}.db"
        archivo_destino, _ = QFileDialog.getSaveFileName(self, "Guardar Copia de Seguridad", nombre_default, "Archivos DB (*.db)")
        
        if not archivo_destino: return

        try:
            shutil.copy2(ruta_db_original, archivo_destino)
            QMessageBox.information(self, "Respaldo Creado", "Copia de seguridad exitosa.")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Falló la copia de seguridad.\nError: {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaHerramientas()
    ventana.show()
    sys.exit(app.exec())