import sqlite3
import os

class Database:
    def __init__(self, db_name="gym_mtz.db"):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        self.db_path = os.path.join(base_dir, db_name)

    def conectar(self):
        try:
            conn = sqlite3.connect(self.db_path)
            # Modo WAL para evitar bloqueos (database locked)
            conn.execute("PRAGMA journal_mode=WAL;")
            return conn
        except sqlite3.Error as e:
            print(f"Error conectando a la BD: {e}")
            return None

    def crear_tablas(self):
        conn = self.conectar()
        if conn:
            cursor = conn.cursor()
            
            # 1. Tabla PLANES
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS planes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT UNIQUE NOT NULL,
                    precio REAL NOT NULL
                )
            ''')
            
            # 2. Tabla MIEMBROS
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS miembros (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    apellido TEXT NOT NULL,
                    dni TEXT UNIQUE NOT NULL,
                    plan_id INTEGER,
                    ingresos_restantes INTEGER DEFAULT 0,
                    ultimo_pago DATE,
                    fecha_registro DATE DEFAULT CURRENT_DATE,
                    activo BOOLEAN DEFAULT 1,
                    FOREIGN KEY(plan_id) REFERENCES planes(id)
                )
            ''')
            
            # 3. Tabla HISTORIAL
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS historial_acceso (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    miembro_id INTEGER,
                    fecha_hora DATETIME DEFAULT CURRENT_TIMESTAMP,
                    tipo_acceso TEXT, 
                    FOREIGN KEY(miembro_id) REFERENCES miembros(id)
                )
            ''')
            
            self.inicializar_planes(cursor)
            conn.commit()
            conn.close()
            print("Base de datos verificada con éxito.")

    def inicializar_planes(self, cursor):
        """Carga los precios base si no existen"""
        planes_base = [
            ("Libre", 38000),
            ("3 veces x semana", 35000),
            ("Menores", 34000),
            ("Box/Funcional", 33000),
            ("Pase Libre (+1 actividad)", 42000)
        ]
        for nombre, precio in planes_base:
            try:
                cursor.execute("INSERT INTO planes (nombre, precio) VALUES (?, ?)", (nombre, precio))
            except sqlite3.IntegrityError:
                pass 

    def registrar_socio(self, nombre, apellido, dni, plan_nombre, ingresos):
        conn = self.conectar()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM planes WHERE nombre = ?", (plan_nombre,))
                plan_result = cursor.fetchone()
                plan_id = plan_result[0] if plan_result else None
                
                cursor.execute('''
                    INSERT INTO miembros (nombre, apellido, dni, plan_id, ingresos_restantes, ultimo_pago)
                    VALUES (?, ?, ?, ?, ?, DATE('now'))
                ''', (nombre, apellido, dni, plan_id, ingresos))
                conn.commit()
                return True
            except Exception as e:
                print(f"Error al registrar: {e}")
                return False
            finally:
                conn.close()
        return False

    def registrar_ingreso(self, dni):
        conn = self.conectar()
        info_socio = None
        
        if conn:
            try:
                cursor = conn.cursor()
                
                # CORRECCIÓN IMPORTANTE: Ahora el SELECT trae los 6 datos que necesitamos
                cursor.execute('''
                    SELECT m.id, m.nombre, m.apellido, p.nombre, m.ingresos_restantes, m.ultimo_pago 
                    FROM miembros m
                    LEFT JOIN planes p ON m.plan_id = p.id
                    WHERE m.dni = ?
                ''', (dni,))
                
                resultado = cursor.fetchone()
                
                if resultado:
                    # Ahora sí coinciden las variables con las columnas
                    m_id, nombre, apellido, plan, ingresos, ultimo_pago = resultado
                    
                    if ingresos > 0:
                        cursor.execute("UPDATE miembros SET ingresos_restantes = ingresos_restantes - 1 WHERE id = ?", (m_id,))
                        cursor.execute("INSERT INTO historial_acceso (miembro_id, tipo_acceso) VALUES (?, 'Ingreso')", (m_id,))
                        
                        conn.commit()
                        info_socio = {
                            "nombre": nombre, "apellido": apellido, "plan": plan,
                            "ultimo_pago": ultimo_pago, "ingresos_restantes": ingresos - 1,
                            "acceso": True
                        }
                    else:
                        cursor.execute("INSERT INTO historial_acceso (miembro_id, tipo_acceso) VALUES (?, 'Rechazado')", (m_id,))
                        conn.commit()
                        
                        info_socio = {
                            "nombre": nombre, "apellido": apellido, "plan": plan,
                            "ultimo_pago": ultimo_pago, "ingresos_restantes": 0,
                            "acceso": False
                        }
            except Exception as e:
                print(f"Error en ingreso: {e}")
            finally:
                conn.close()
        
        return info_socio

    def obtener_planes(self):
        conn = self.conectar()
        planes = []
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT nombre FROM planes")
            planes = [row[0] for row in cursor.fetchall()]
            conn.close()
        return planes

if __name__ == "__main__":
    db = Database()
    db.crear_tablas()