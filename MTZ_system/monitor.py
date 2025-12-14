import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QLabel, QVBoxLayout,
    QWidget, QLineEdit, QFrame
)
from PyQt6.QtCore import Qt, QTimer, QTime, QRect
from PyQt6.QtGui import QFont, QPixmap, QPalette, QBrush, QColor, QKeyEvent, QPainter
from database import Database
from datetime import datetime

class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Monitor de Acceso - MTZ")
        self.showFullScreen() 
        
        self.db = Database()
        
        # --- 1. CONFIGURACIÓN DEL FONDO ---
        self.configurar_fondo()

        # --- 2. LAYOUT PRINCIPAL ---
        widget_central = QWidget()
        widget_central.setStyleSheet("background-color: transparent;") 
        
        self.layout_principal = QVBoxLayout()
        self.layout_principal.setAlignment(Qt.AlignmentFlag.AlignCenter)
        widget_central.setLayout(self.layout_principal)
        self.setCentralWidget(widget_central)

        # --- 3. LA TARJETA BLANCA (MÁS COMPACTA) ---
        self.card = QFrame()
        # CAMBIO: Reducimos tamaño para quitar espacio blanco sobrante
        self.card.setFixedSize(550, 350) 
        self.card.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 30px;
                border: 2px solid #ddd;
            }
        """)
        
        self.layout_card = QVBoxLayout()
        # CAMBIO: Menos margen interno
        self.layout_card.setContentsMargins(30, 30, 30, 30)
        self.layout_card.setSpacing(5) # Menos espacio entre elementos
        self.card.setLayout(self.layout_card)
        
        self.layout_principal.addWidget(self.card)

        # --- 4. ELEMENTOS ---
        self.crear_elementos_ui()
        self.input_dni.setFocus()

    def configurar_fondo(self):
        """Carga fondo.png O fondo.jpg y lo centra sobre negro sin zoom excesivo"""
        base_path = os.path.join(os.path.dirname(__file__), "assets")
        
        # 1. Buscamos el archivo (png o jpg)
        ruta_fondo = os.path.join(base_path, "fondo.png")
        if not os.path.exists(ruta_fondo):
            ruta_fondo = os.path.join(base_path, "fondo.jpg")

        if os.path.exists(ruta_fondo):
            screen_size = QApplication.primaryScreen().size()
            
            fondo_final = QPixmap(screen_size)
            fondo_final.fill(Qt.GlobalColor.black)
            
            logo = QPixmap(ruta_fondo)
            
            logo_scaled = logo.scaled(
                screen_size, 
                Qt.AspectRatioMode.KeepAspectRatio, 
                Qt.TransformationMode.SmoothTransformation
            )
            
            painter = QPainter(fondo_final)
            x = (screen_size.width() - logo_scaled.width()) // 2
            y = (screen_size.height() - logo_scaled.height()) // 2
            painter.drawPixmap(x, y, logo_scaled)
            painter.end()
            
            palette = QPalette()
            palette.setBrush(QPalette.ColorRole.Window, QBrush(fondo_final))
            self.setPalette(palette)
        else:
            self.setStyleSheet("QMainWindow { background-color: #2c3e50; }") 
            print(f"AVISO: No se encontró fondo en {base_path}")

    def crear_elementos_ui(self):
        # RELOJ (Un poco más chico)
        self.lbl_reloj = QLabel("00:00")
        self.lbl_reloj.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_reloj.setStyleSheet("color: #333; font-size: 42px; font-weight: 300; background: transparent; border: none;")
        self.layout_card.addWidget(self.lbl_reloj)
        
        self.timer_reloj = QTimer(self)
        self.timer_reloj.timeout.connect(self.actualizar_reloj)
        self.timer_reloj.start(1000)
        self.actualizar_reloj()
        
        # TITULO
        self.lbl_titulo = QLabel("Bienvenido a MTZ")
        self.lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_titulo.setStyleSheet("color: #000; font-size: 32px; font-weight: bold; background: transparent; border: none; margin-bottom: 10px;")
        self.layout_card.addWidget(self.lbl_titulo)
        
        # INSTRUCCION
        self.lbl_instruccion = QLabel("Ingresar DNI")
        self.lbl_instruccion.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_instruccion.setStyleSheet("color: #555; font-size: 20px; font-weight: bold; background: transparent; border: none;")
        self.layout_card.addWidget(self.lbl_instruccion)

        # INPUT DNI
        self.input_dni = QLineEdit()
        self.input_dni.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.input_dni.setPlaceholderText("...")
        self.input_dni.setStyleSheet("""
            QLineEdit {
                background-color: #f0f0f0;
                border: 2px solid #ccc;
                border-radius: 25px;
                padding: 5px;
                font-size: 26px;
                color: #333;
                margin-top: 5px;
            }
            QLineEdit:focus {
                border: 2px solid #e74c3c;
                background-color: #fff;
            }
        """)
        self.input_dni.returnPressed.connect(self.procesar_dni)
        self.layout_card.addWidget(self.input_dni)
        
        self.layout_card.addStretch()
        
        # RESULTADO
        self.lbl_resultado = QLabel("")
        self.lbl_resultado.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.lbl_resultado.setStyleSheet("font-size: 22px; font-weight: bold; background: transparent; border: none;")
        self.lbl_resultado.hide()
        self.layout_card.addWidget(self.lbl_resultado)

        self.timer_limpieza = QTimer()
        self.timer_limpieza.setSingleShot(True)
        self.timer_limpieza.timeout.connect(self.resetear_pantalla)

    def actualizar_reloj(self):
        self.lbl_reloj.setText(QTime.currentTime().toString("HH:mm"))

    def procesar_dni(self):
        dni = self.input_dni.text().strip()
        if not dni: return
        self.input_dni.clear()
        resultado = self.db.registrar_ingreso(dni)
        if resultado:
            self.mostrar_resultado_acceso(resultado)
        else:
            self.mostrar_error("DNI NO ENCONTRADO")

    def mostrar_resultado_acceso(self, info):
        self.lbl_reloj.hide()
        self.lbl_titulo.hide()
        self.lbl_instruccion.hide()
        self.input_dni.hide()
        
        if info['acceso']:
            color_borde = "#2ecc71"
            icono = "✅"
            texto_saldo = f"Ingresos restantes: {info['ingresos_restantes']}"
            if info['ingresos_restantes'] > 900: texto_saldo = "PASE LIBRE"
        else:
            color_borde = "#e74c3c"
            icono = "⛔"
            texto_saldo = info['mensaje']

        self.card.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border-radius: 30px;
                border: 5px solid {color_borde};
            }}
        """)
        
        venc = datetime.strptime(info['vencimiento'], '%Y-%m-%d').strftime('%d/%m/%Y') if info['vencimiento'] else "--/--/--"
        
        # CAMBIO: Ajustamos tamaños de fuente y márgenes para que quepan bien
        texto_html = f"""
            <h1 style='font-size: 50px; margin:0;'>{icono}</h1>
            <h2 style='font-size: 28px; color: #333; margin:5px;'>{info['nombre']} {info['apellido']}</h2>
            <h3 style='font-size: 20px; color: #555; margin:0;'>Plan: {info['plan']}</h3>
            <h3 style='font-size: 24px; color: {color_borde}; font-weight: bold; margin:10px;'>{texto_saldo}</h3>
            <p style='font-size: 16px; color: #777; margin:0;'>Vence: {venc}</p>
        """
        self.lbl_resultado.setText(texto_html)
        self.lbl_resultado.show()
        self.timer_limpieza.start(4000)

    def mostrar_error(self, mensaje):
        self.lbl_reloj.hide()
        self.lbl_titulo.hide()
        self.lbl_instruccion.hide()
        self.input_dni.hide()

        self.card.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 30px;
                border: 5px solid #e74c3c;
            }
        """)

        texto_html = f"""
            <h1 style='font-size: 50px; margin:0;'>⚠️</h1>
            <h2 style='font-size: 28px; color: #e74c3c; margin:20px;'>{mensaje}</h2>
            <p style='font-size: 16px; color: #555;'>Por favor consulta en administración</p>
        """
        self.lbl_resultado.setText(texto_html)
        self.lbl_resultado.show()
        self.timer_limpieza.start(3000)

    def resetear_pantalla(self):
        self.card.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.95);
                border-radius: 30px;
                border: 2px solid #ddd;
            }
        """)
        self.lbl_resultado.hide()
        self.lbl_resultado.clear()
        self.lbl_reloj.show()
        self.lbl_titulo.show()
        self.lbl_instruccion.show()
        self.input_dni.show()
        self.input_dni.setFocus()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            self.close()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())