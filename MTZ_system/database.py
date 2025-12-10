import sqlite3
import os

class Database:
  def __init__(self, db_name="gym_mtz.db"):
    #por las dudas aseguro que la db se cree en la carpeta correcta
    base_dir = os.path.dirname(os.path.abspath(__file__))
    self.db_path = os.path.join(base_dir, db_name)
    
  def conectar(self):
    """Establece conexión con la base de datos"""
    try:
      conn = sqlite3.connect(self.db_path)
      return conn
    except sqlite3.Error as e:
      print(f"Error conectando a la BD: {e}")
      return None
  
  def crear_tablas(self):
    """Crea las tablas necesarios si no existen"""
    conn = self.conectar()
    if conn:
      cursor = conn.cursor()
      
      #tabla de socios
      cursor.execute('''
          CREATE TABLE IF NOT EXISTS miembros (
              id INTEGER PRIMARY KEY AUTOINCREMENT,
              nombre TEXT NOT NULL,
              apellido TEXT NOT NULL,
              dni TEXT UNIQUE NOT NULL,
              telefono TEXT,
              fecha_registro DATE DEFAULT CURRENT_DATE,
              activo BOOLEAN DEFAULT 1
                )
      ''')
      
      #agrego más tablas para el futuro, como planes, pagos
      conn.commit()
      conn.close()
      print("Base de datos y tablas verificadas con éxito")

if __name__ == "__main__":
  db = Database()
  db.crear_tablas()