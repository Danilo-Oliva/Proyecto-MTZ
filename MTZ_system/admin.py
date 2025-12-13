import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout,
    QWidget, QPushButton, QHBoxLayout, QFrame
)
from PyQt6.QtCore import Qt
from registro import VentanaRegistro 
from gestion import VentanaGestion
from reportes import VentanaReportes

class PanelAdmin(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Panel de Administración - MTZ")
        self.setGeometry(100, 100, 1000, 700)
        self.setStyleSheet("background-color: #f0f0f0;")

        widget_central = QWidget()
        layout_principal = QHBoxLayout()
        
        # 1. MENÚ LATERAL
        barra_lateral = QFrame()
        barra_lateral.setStyleSheet("background-color: #2c3e50; min-width: 200px;")
        layout_menu = QVBoxLayout()
        
        titulo = QLabel("MTZ ADMIN")
        titulo.setStyleSheet("color: white; font-size: 24px; font-weight: bold; margin-bottom: 30px;")
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_menu.addWidget(titulo)
        
        # BOTONES
        btn_nuevo = QPushButton(" + Nuevo Socio")
        btn_nuevo.setStyleSheet(self.estilo_boton())
        btn_nuevo.clicked.connect(self.abrir_registro) 
        layout_menu.addWidget(btn_nuevo)
        
        btn_gestion = QPushButton("🔍 Buscar / Editar")
        btn_gestion.setStyleSheet(self.estilo_boton())
        btn_gestion.clicked.connect(self.abrir_gestion)
        layout_menu.addWidget(btn_gestion)
        
        btn_reportes = QPushButton("📊 Reportes")
        btn_reportes.setStyleSheet(self.estilo_boton())
        btn_reportes.clicked.connect(self.abrir_reportes)
        layout_menu.addWidget(btn_reportes)

        layout_menu.addStretch()
        barra_lateral.setLayout(layout_menu)
        
        # 2. ÁREA DE TRABAJO (DERECHA)
        area_contenido = QFrame()
        layout_contenido = QVBoxLayout()
        
        lbl_bienvenida = QLabel("Bienvenido al Panel de Gestión")
        lbl_bienvenida.setStyleSheet("font-size: 28px; color: #333; font-weight: bold;")
        
        layout_contenido.addWidget(lbl_bienvenida)
        layout_contenido.addStretch()
        area_contenido.setLayout(layout_contenido)

        layout_principal.addWidget(barra_lateral)
        layout_principal.addWidget(area_contenido)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        
        widget_central.setLayout(layout_principal)
        self.setCentralWidget(widget_central)
        
    def estilo_boton(self):
        return """
            QPushButton { 
                background-color: transparent; color: #bdc3c7; padding: 10px; 
                border: none; font-size: 16px; text-align: left; padding-left: 20px; 
            }
            QPushButton:hover { background-color: #34495e; color: white; }
        """
    def abrir_registro(self):
        dialogo = VentanaRegistro()
        dialogo.exec()
        
    def abrir_gestion(self):
        dialogo = VentanaGestion()
        dialogo.exec()
        
    def abrir_reportes(self):
        dialogo = VentanaReportes()
        dialogo.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = PanelAdmin()
    ventana.show()
    sys.exit(app.exec())