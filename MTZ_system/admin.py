import sys
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QVBoxLayout,
    QWidget,
    QPushButton,
    QHBoxLayout,
    QFrame,
    QStackedWidget,
    QGridLayout,
)
from PyQt6.QtCore import Qt
from registro import VentanaRegistro
from gestion import VentanaGestion
from reportes import VentanaReportes
from monitor import VentanaPrincipal as VentanaMonitor
from herramientas import VentanaHerramientas
from database import Database
from datetime import datetime
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QHeaderView


class VentanaHistorial(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = Database()
        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)

        lbl_titulo = QLabel("Historial de Accesos (Últimos 100)")
        lbl_titulo.setStyleSheet("font-size: 24px; font-weight: bold; color: #333;")
        layout.addWidget(lbl_titulo)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(
            ["Fecha", "Hora", "Nombre", "Apellido", "Evento"]
        )
        self.tabla.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.tabla.setStyleSheet(
            "QTableWidget { background-color: white; color: #333; gridline-color: #ccc; border: 1px solid #ccc; } QHeaderView::section { background-color: #eee; color: #333; padding: 5px; }"
        )
        layout.addWidget(self.tabla)

        btn_refresh = QPushButton("🔄 Actualizar Lista")
        btn_refresh.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_refresh.setStyleSheet(
            "background-color: #3498db; color: white; padding: 10px; border-radius: 5px; font-weight: bold;"
        )
        btn_refresh.clicked.connect(self.cargar_historial)
        layout.addWidget(btn_refresh)

        self.setLayout(layout)
        self.cargar_historial()

    def cargar_historial(self):
        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor()
            sql = """
                SELECT h.fecha_hora, m.nombre, m.apellido, h.tipo_acceso
                FROM historial_acceso h
                JOIN miembros m ON h.miembro_id = m.id
                ORDER BY h.id DESC
                LIMIT 100
            """
            cursor.execute(sql)
            datos = cursor.fetchall()
            self.tabla.setRowCount(0)
            for row_idx, fila in enumerate(datos):
                self.tabla.insertRow(row_idx)
                fecha_hora = fila[0]
                try:
                    dt = datetime.strptime(fecha_hora, "%Y-%m-%d %H:%M:%S")
                    fecha_str = dt.strftime("%d/%m/%Y")
                    hora_str = dt.strftime("%H:%M")
                except:
                    fecha_str, hora_str = fecha_hora, ""

                self.tabla.setItem(row_idx, 0, QTableWidgetItem(fecha_str))
                self.tabla.setItem(row_idx, 1, QTableWidgetItem(hora_str))
                self.tabla.setItem(row_idx, 2, QTableWidgetItem(fila[1]))
                self.tabla.setItem(row_idx, 3, QTableWidgetItem(fila[2]))
                item_evento = QTableWidgetItem(fila[3])
                if "Rechazado" in fila[3] or "Vencido" in fila[3]:
                    item_evento.setForeground(Qt.GlobalColor.red)
                elif "Ingreso" in fila[3]:
                    item_evento.setForeground(Qt.GlobalColor.darkGreen)
                self.tabla.setItem(row_idx, 4, item_evento)
            conn.close()


# --- CLASE TARJETA DATO ---
class TarjetaDato(QFrame):
    def __init__(self, titulo, valor, color_fondo, parent=None):
        super().__init__(parent)
        self.setStyleSheet(
            f"QFrame {{ background-color: {color_fondo}; border-radius: 10px; }} QLabel {{ background-color: transparent; color: white; border: none; }}"
        )
        self.setFixedSize(200, 120)
        layout = QVBoxLayout()
        lbl_valor = QLabel(str(valor))
        lbl_valor.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_valor.setStyleSheet("font-size: 32px; font-weight: bold;")
        lbl_titulo = QLabel(titulo)
        lbl_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        lbl_titulo.setStyleSheet("font-size: 14px;")
        layout.addWidget(lbl_valor)
        layout.addWidget(lbl_titulo)
        self.setLayout(layout)


# --- WIDGET INICIO ---
class DashboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.db = Database()
        layout = QVBoxLayout()
        layout.setContentsMargins(40, 40, 40, 40)
        lbl_bienvenida = QLabel("Resumen del Gimnasio")
        lbl_bienvenida.setStyleSheet(
            "font-size: 28px; color: #333; font-weight: bold; margin-bottom: 20px;"
        )
        layout.addWidget(lbl_bienvenida)
        self.grid = QGridLayout()
        self.grid.setSpacing(20)
        self.grid.setAlignment(Qt.AlignmentFlag.AlignLeft)
        layout.addLayout(self.grid)
        layout.addStretch()
        self.setLayout(layout)
        self.actualizar_metricas()

    def actualizar_metricas(self):
        while self.grid.count():
            item = self.grid.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        conn = self.db.conectar()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM miembros WHERE activo = 1")
            activos = cursor.fetchone()[0]
            hoy = datetime.now().strftime("%Y-%m-%d")
            cursor.execute(
                "SELECT COUNT(*) FROM miembros WHERE activo = 1 AND fecha_vencimiento < ?",
                (hoy,),
            )
            vencidos = cursor.fetchone()[0]
            cursor.execute(
                "SELECT SUM(p.precio) FROM miembros m JOIN planes p ON m.plan_id = p.id WHERE m.activo = 1"
            )
            res = cursor.fetchone()[0]
            caja = res if res else 0
            conn.close()
            self.grid.addWidget(TarjetaDato("Socios Activos", activos, "#2980b9"), 0, 0)
            self.grid.addWidget(
                TarjetaDato("Cuotas Vencidas", vencidos, "#c0392b"), 0, 1
            )
            txt_caja = f"${caja:,.0f}".replace(",", ".")
            card_caja = TarjetaDato("Caja Mensual Est.", txt_caja, "#27ae60")
            card_caja.setFixedWidth(420)
            self.grid.addWidget(card_caja, 1, 0, 1, 2)


class PanelAdmin(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Panel de Administración - MTZ")
        self.setGeometry(100, 100, 1100, 700)
        self.setStyleSheet("background-color: #f0f0f0;")
        self.ventana_monitor = None

        widget_central = QWidget()
        layout_principal = QHBoxLayout()

        # --- MENÚ LATERAL ---
        barra_lateral = QFrame()
        barra_lateral.setStyleSheet("background-color: #2c3e50; min-width: 200px;")
        layout_menu = QVBoxLayout()

        titulo = QLabel("MTZ ADMIN")
        titulo.setStyleSheet(
            "color: white; font-size: 24px; font-weight: bold; margin-bottom: 30px;"
        )
        titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout_menu.addWidget(titulo)

        # BOTONES
        btn_inicio = QPushButton(" 🏠 Inicio")
        btn_nuevo = QPushButton(" + Nuevo Socio")
        btn_gestion = QPushButton(" 🔍 Buscar / Editar")
        btn_reportes = QPushButton(" 📊 Reportes Full")
        btn_historial = QPushButton(" 📜 Historial Visitas")

        # --- BOTÓN NUEVO ---
        btn_herramientas = QPushButton(" 🛠️ Herramientas")
        btn_herramientas.clicked.connect(self.abrir_herramientas)
        # -------------------

        btn_monitor = QPushButton(" 📺 Pantalla Acceso")
        btn_monitor.setStyleSheet(
            """
            QPushButton { 
                background-color: #222; color: #00ff00; padding: 15px; 
                border: 1px solid #00ff00; font-size: 16px; text-align: left; padding-left: 20px; margin-top: 20px;
                border-radius: 5px; font-weight: bold;
            }
            QPushButton:hover { background-color: #00ff00; color: #000; }
        """
        )
        btn_monitor.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_monitor.clicked.connect(self.abrir_monitor)

        # Conexiones Stack
        btn_inicio.clicked.connect(lambda: self.cambiar_pagina(0))
        btn_nuevo.clicked.connect(lambda: self.cambiar_pagina(1))
        btn_gestion.clicked.connect(lambda: self.cambiar_pagina(2))
        btn_historial.clicked.connect(lambda: self.cambiar_pagina(3))
        # Reportes (Popup)
        btn_reportes.clicked.connect(self.abrir_reportes)

        # Agregar botones al layout
        lista_botones = [
            btn_inicio,
            btn_nuevo,
            btn_gestion,
            btn_reportes,
            btn_historial,
            btn_herramientas,
        ]
        for btn in lista_botones:
            if btn != btn_monitor:
                btn.setStyleSheet(self.estilo_boton())
            layout_menu.addWidget(btn)

        layout_menu.addWidget(btn_monitor)
        layout_menu.addStretch()
        barra_lateral.setLayout(layout_menu)

        # --- STACK ---
        self.stack = QStackedWidget()
        self.pagina_inicio = DashboardWidget()
        self.pagina_registro = VentanaRegistro()
        self.pagina_gestion = VentanaGestion()
        self.pagina_historial = VentanaHistorial()

        self.stack.addWidget(self.pagina_inicio)  # 0
        self.stack.addWidget(self.pagina_registro)  # 1
        self.stack.addWidget(self.pagina_gestion)  # 2
        self.stack.addWidget(self.pagina_historial)  # 3

        layout_principal.addWidget(barra_lateral)
        layout_principal.addWidget(self.stack)
        layout_principal.setContentsMargins(0, 0, 0, 0)
        widget_central.setLayout(layout_principal)
        self.setCentralWidget(widget_central)

    def cambiar_pagina(self, indice):
        self.stack.setCurrentIndex(indice)
        if indice == 0:
            self.pagina_inicio.actualizar_metricas()
        elif indice == 2:
            self.pagina_gestion.cargar_socios()
        elif indice == 3:
            self.pagina_historial.cargar_historial()

    def estilo_boton(self):
        return """
            QPushButton { 
                background-color: transparent; color: #bdc3c7; padding: 15px; 
                border: none; font-size: 16px; text-align: left; padding-left: 20px; 
            }
            QPushButton:hover { background-color: #34495e; color: white; }
        """

    def abrir_reportes(self):
        dialogo = VentanaReportes()
        dialogo.exec()

    def abrir_herramientas(self):
        dialogo = VentanaHerramientas()
        dialogo.exec()

    def abrir_monitor(self):
        if self.ventana_monitor is None:
            self.ventana_monitor = VentanaMonitor()
        pantallas = QApplication.screens()
        if len(pantallas) > 1:
            monitor_externo = pantallas[1]
            geometria = monitor_externo.geometry()
            self.ventana_monitor.move(geometria.x(), geometria.y())
            self.ventana_monitor.showFullScreen()
        else:
            self.ventana_monitor.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    db = Database()
    db.crear_tablas()

    ventana = PanelAdmin()
    ventana.show()
    sys.exit(app.exec())
