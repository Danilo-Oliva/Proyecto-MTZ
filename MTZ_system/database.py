import sqlite3
import os


class Database:
    def __init__(self, db_name="gym_mtz.db"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(base_dir, db_name)

    def conectar(self):
        try:
            conn = sqlite3.connect(self.db_path)
            return conn
        except sqlite3.Error as e:
            print(f"Error conectando a la BD: {e}")
            return None

    def crear_tablas(self):
        conn = self.conectar()
        if conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS miembros (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    apellido TEXT NOT NULL,
                    dni TEXT UNIQUE NOT NULL,
                    telefono TEXT,
                    actividad TEXT,               -- Ej: "Musculación", "Boxeo"
                    ingresos_restantes INTEGER DEFAULT 0, -- Para controlar el acceso
                    ultimo_pago DATE,             -- Fecha del pago
                    fecha_registro DATE DEFAULT CURRENT_DATE,
                    activo BOOLEAN DEFAULT 1
                )
            """
            )

            conn.commit()
            conn.close()
            print("Base de datos actualizada creada con éxito.")
    def descontar_ingreso(self, dni):
        '''restamos 1 a los ingresos del socio'''
        conn = self.conectar()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("UPDATE miembros SET ingresos_restantes = ingresos_restantes - 1 WHERE dni = ?", (dni,))
                conn.commit()
            except sqlite3.Error as e:
                print(f"Error al descontar ingreso: {e}")
            finally:
                conn.close()
            
    # Función nueva para simular un socio y probar el sistema
    def insertar_socio_prueba(self):
        conn = self.conectar()
        if conn:
            cursor = conn.cursor()
            try:
                # Insertamos un usuario falso para probar
                cursor.execute(
                    """
                    INSERT INTO miembros (nombre, apellido, dni, actividad, ingresos_restantes, ultimo_pago)
                    VALUES (?, ?, ?, ?, ?, ?)
                """,
                    ("Juan", "Pérez", "12345678", "Musculación", 12, "2023-12-01"),
                )
                conn.commit()
                print("Socio de prueba creado (DNI: C)")
            except sqlite3.IntegrityError:
                print("El socio de prueba ya existe.")
            finally:
                conn.close()
    def registrar_socio(self, nombre, apellido, dni, actividad, ingresos):
        '''guardar un nuevo socio en la base de datos'''
        conn = self.conectar()
        if conn:
            try:
                cursor = conn.cursor()
                #la fecha de ultimo pago la ponemos como hoy automaticamente
                cursor.execute('''
                                INSERT INTO miembros (nombre, apellido, dni, actividad, ingresos_restantes, ultimo_pago)
                                VALUES (?, ?,
                                ?, ?, ?, DATE('now'))
                               ''', (nombre, apellido, dni, actividad, ingresos))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                return False
            except Exception as e:
                print(f"Error al registrar: {e}")
                return False
            finally:
                conn.close()

if __name__ == "__main__":
    db = Database()
    db.crear_tablas()
    db.insertar_socio_prueba()
