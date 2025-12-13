import sys
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QLineEdit, QPushButton, 
    QHBoxLayout, QTableWidget, QTableWidgetItem, 
    QHeaderView, QMessageBox, QLabel
)
from PyQt6.QtCore import Qt
from database import Database

class VentanaGestion(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Gestión de Socios - MTZ")
        self.setFixedSize(800, 600) # Más grande para que quepa la tabla
        
        # --- ESTILO OSCURO (Igual que Registro) ---
        self.setStyleSheet("""
            QDialog {
                background-color: #2b2b2b;
                color: white;
            }
            QLineEdit {
                background-color: #404040;
                color: white;
                border: 1px solid #666;
                padding: 8px;
                border-radius: 4px;
                font-size: 14px;
            }
            QPushButton {
                background-color: #3498db;
                color: white;
                padding: 10px;
                border-radius: 4px;
                font-weight: bold;
                border: none;
            }
            QPushButton:hover { background-color: #2980b9; }
            
            /* ESTILO DE LA TABLA */
            QTableWidget {
                background-color: #333;
                color: white;
                gridline-color: #555;
                border: none;
                font-size: 13px;
            }
            QHeaderView::section {
                background-color: #222;
                color: white;
                padding: 5px;
                border: 1px solid #555;
            }
            QTableWidget::item:selected {
                background-color: #3498db;
            }
        """)

        self.db = Database()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # 1. BARRA DE BÚSQUEDA
        layout_buscar = QHBoxLayout()
        self.input_buscar = QLineEdit()
        self.input_buscar.setPlaceholderText("Buscar por Nombre, Apellido o DNI...")
        self.input_buscar.textChanged.connect(self.cargar_socios) # Busca mientras escribes
        
        btn_refrescar = QPushButton("🔄 Actualizar")
        btn_refrescar.setFixedWidth(100)
        btn_refrescar.clicked.connect(self.cargar_socios)

        layout_buscar.addWidget(self.input_buscar)
        layout_buscar.addWidget(btn_refrescar)
        layout.addLayout(layout_buscar)

        # 2. TABLA DE RESULTADOS
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(6) # ID, Nombre, Apellido, DNI, Plan, Pases
        self.tabla.setHorizontalHeaderLabels(["ID", "Nombre", "Apellido", "DNI", "Plan", "Pases Restantes"])
        
        # Ajustar columnas automáticamente
        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        # Ocultamos la columna ID (la necesitamos por código pero no hace falta verla)
        self.tabla.setColumnHidden(0, True) 
        
        layout.addWidget(self.tabla)

        # 3. BOTONERA DE ACCIONES (Abajo)
        layout_botones = QHBoxLayout()
        
        btn_editar = QPushButton("✏️ Editar / Ver")
        btn_editar.setStyleSheet("background-color: #f39c12;")
        btn_editar.clicked.connect(self.accion_editar) # Aún no hace nada
        
        btn_renovar = QPushButton("💰 Renovar Cuota")
        btn_renovar.setStyleSheet("background-color: #27ae60;")
        btn_renovar.clicked.connect(self.accion_renovar) # Aún no hace nada
        
        btn_borrar = QPushButton("🗑️ Eliminar")
        btn_borrar.setStyleSheet("background-color: #c0392b;")
        btn_borrar.clicked.connect(self.accion_borrar) # Aún no hace nada

        layout_botones.addWidget(btn_editar)
        layout_botones.addWidget(btn_renovar)
        layout_botones.addWidget(btn_borrar)
        layout.addLayout(layout_botones)

        self.setLayout(layout)
        
        # Cargar datos al iniciar
        self.cargar_socios()

    def cargar_socios(self):
        """Consulta la base de datos y llena la tabla"""
        filtro = self.input_buscar.text().strip()
        
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor()
            
            # Consulta SQL con JOIN para traer el nombre del plan en vez del ID
            sql = """
                SELECT m.id, m.nombre, m.apellido, m.dni, p.nombre, m.ingresos_restantes 
                FROM miembros m
                LEFT JOIN planes p ON m.plan_id = p.id
                WHERE m.activo = 1 AND (
                      m.nombre LIKE ? OR 
                      m.apellido LIKE ? OR 
                      m.dni LIKE ?
                )
                ORDER BY m.id DESC
            """
            # Los % sirven para buscar "algo que contenga el texto"
            param = f"%{filtro}%"
            cursor.execute(sql, (param, param, param))
            resultados = cursor.fetchall()
            
            self.tabla.setRowCount(0) # Limpiar tabla
            
            for row_idx, datos in enumerate(resultados):
                self.tabla.insertRow(row_idx)
                for col_idx, dato in enumerate(datos):
                    item = QTableWidgetItem(str(dato))
                    # Alineamos al centro el DNI y los Pases
                    if col_idx in [3, 5]: 
                        item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                    self.tabla.setItem(row_idx, col_idx, item)
            
            conn.close()

    # --- Placeholder para futuras funciones ---
    def accion_editar(self):
        QMessageBox.information(self, "Próximamente", "Aquí abriremos una ventana para modificar los datos.")

    def accion_renovar(self):
        fila = self.tabla.currentRow()
        if fila == -1:
            QMessageBox.warning(self, "Alerta", "Selecciona un socio de la tabla primero.")
            return
        nombre = self.tabla.item(fila, 1).text()
        QMessageBox.information(self, "Próximamente", f"Aquí renovaremos la cuota de {nombre}.")

    def accion_borrar(self):
        QMessageBox.warning(self, "Cuidado", "Función de borrar en construcción.")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaGestion()
    ventana.show()
    sys.exit(app.exec())