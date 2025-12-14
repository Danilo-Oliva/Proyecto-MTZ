import sys
from PyQt6.QtWidgets import (
    QApplication, QDialog, QVBoxLayout, QLabel, QGridLayout, QFrame, 
    QPushButton, QHBoxLayout
)
from PyQt6.QtCore import Qt
from database import Database
from datetime import datetime

class TarjetaDato(QFrame):
    """Una tarjetita bonita para mostrar un número y un título"""
    def __init__(self, titulo, valor, color_fondo, parent=None):
        super().__init__(parent)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color_fondo};
                border-radius: 10px;
            }}
            QLabel {{
                background-color: transparent;
                color: white;
                border: none;
            }}
        """)
        self.setFixedSize(200, 120)
        
        layout = QVBoxLayout()
        
        lbl_valor = QLabel(str(valor))
        lbl_valor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_valor.setStyleSheet("font-size: 36px; font-weight: bold;")
        
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_titulo.setStyleSheet("font-size: 16px;")
        
        layout.addWidget(lbl_valor)
        layout.addWidget(lbl_titulo)
        self.setLayout(layout)

class VentanaReportes(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Reportes y Estadísticas - MTZ")
        self.setFixedSize(800, 500)
        self.setStyleSheet("background-color: #2b2b2b; color: white;")
        
        self.db = Database()
        
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Título
        lbl_titulo = QLabel("Estado del Gimnasio")
        lbl_titulo.setStyleSheet("font-size: 24px; font-weight: bold; margin-bottom: 20px;")
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(lbl_titulo)
        
        # Grid de Tarjetas
        self.grid = QGridLayout()
        self.grid.setSpacing(20)
        layout.addLayout(self.grid)
        
        # Botón para recalcular
        btn_actualizar = QPushButton("🔄 Actualizar Métricas")
        btn_actualizar.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_actualizar.setStyleSheet("""
            QPushButton {
                background-color: #3498db; color: white; padding: 12px;
                font-weight: bold; border-radius: 5px; border: none; font-size: 14px;
                margin-top: 30px;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        btn_actualizar.clicked.connect(self.calcular_metricas)
        layout.addWidget(btn_actualizar)
        
        layout.addStretch()
        self.setLayout(layout)
        
        self.calcular_metricas()

    def calcular_metricas(self):
        # Limpiamos el grid si ya tenía cosas (para no duplicar al actualizar)
        while self.grid.count():
            item = self.grid.takeAt(0)
            widget = item.widget()
            if widget:
                widget.deleteLater()

        # 1. OBTENER DATOS DE LA DB
        conn = self.db.conectar()
        if not conn:
            return
        
        cursor = conn.cursor()
        
        # A. Total Socios Activos
        cursor.execute("SELECT COUNT(*) FROM miembros WHERE activo = 1")
        total_socios = cursor.fetchone()[0]
        
        # B. Socios Vencidos (Fecha vencimiento < Hoy)
        hoy = datetime.now().strftime('%Y-%m-%d')
        cursor.execute("SELECT COUNT(*) FROM miembros WHERE activo = 1 AND fecha_vencimiento < ?", (hoy,))
        total_vencidos = cursor.fetchone()[0]
        
        # C. Socios al Día (Activos - Vencidos)
        total_al_dia = total_socios - total_vencidos
        
        # D. Estimación de Ingresos (Suma de precios de planes activos)
        # Esto asume que todos pagaron su plan actual. Es una estimación de "Caja Mensual Potencial".
        sql_ingresos = """
            SELECT SUM(p.precio) 
            FROM miembros m 
            JOIN planes p ON m.plan_id = p.id 
            WHERE m.activo = 1
        """
        cursor.execute(sql_ingresos)
        resultado_ingresos = cursor.fetchone()[0]
        ingresos_estimados = resultado_ingresos if resultado_ingresos else 0
        
        conn.close()
        
        # 2. CREAR LAS TARJETAS VISUALES
        
        # Tarjeta 1: Total Socios (Azul)
        card_total = TarjetaDato("Socios Activos", total_socios, "#2980b9")
        self.grid.addWidget(card_total, 0, 0)
        
        # Tarjeta 2: Al Día (Verde)
        card_dia = TarjetaDato("Cuota al Día", total_al_dia, "#27ae60")
        self.grid.addWidget(card_dia, 0, 1)
        
        # Tarjeta 3: Vencidos (Rojo)
        card_vencidos = TarjetaDato("Vencidos (A cobrar)", total_vencidos, "#c0392b")
        self.grid.addWidget(card_vencidos, 0, 2)
        
        # Tarjeta 4: Caja Estimada (Dorado) - Ocupa todo el ancho abajo
        txt_dinero = f"${ingresos_estimados:,.0f}".replace(",", ".")
        card_plata = TarjetaDato("Ingreso Mensual Est.", txt_dinero, "#f39c12")
        card_plata.setFixedWidth(640)
        self.grid.addWidget(card_plata, 1, 0, 1, 3, Qt.AlignmentFlag.AlignCenter)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaReportes()
    ventana.show()
    sys.exit(app.exec())