import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QVBoxLayout, QWidget

def main():
  #1 - creo la instancia de la app
  app = QApplication(sys.argv)
  
  #2 - creo la ventana principal
  ventana = QMainWindow()
  ventana.setWindowTitle("Systema MTZ - Panel de Control")
  ventana.setGeometry(100, 100, 800, 600)
  
  #3 - contenido de prueba
  central_widget = QWidget()
  layout = QVBoxLayout()
  
  texto = QLabel("El sistema está funcionando correctamente")
  texto.setStyleSheet("font-size: 20px; color: blue; font-weight: bold;")
  
  layout.addWidget(texto)
  central_widget.setLayout(layout)
  ventana.setCentralWidget(central_widget)
  
  #4 - muestro la ventana
  ventana.show()
  
  #5 - loop de ejecución para mantener siempre abierto el programa
  sys.exit(app.exec())

if __name__ == "__main__":
  main()