import sqlite3
import os
import sys
from datetime import datetime, timedelta

class Database:
    def __init__(self, db_name="gym_mtz.db"):
        if getattr(sys, 'frozen', False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            
        self.db_path = os.path.join(base_dir, db_name)

    def conectar(self):
        try:
            conn = sqlite3.connect(self.db_path)
            conn.execute("PRAGMA journal_mode=WAL;")
            return conn
        except sqlite3.Error as e:
            print(f"Error conectando a la BD: {e}")
            return None

    def crear_tablas(self):
        conn = self.conectar()
        if conn:
            cursor = conn.cursor()
            
            #tabla planes
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS planes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT UNIQUE NOT NULL,
                    precio REAL NOT NULL
                )
            ''')

            #tabla miembros
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS miembros (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nombre TEXT NOT NULL,
                    apellido TEXT NOT NULL,
                    dni TEXT UNIQUE NOT NULL,
                    plan_id INTEGER,
                    ingresos_restantes INTEGER DEFAULT 0,
                    ultimo_pago DATE,
                    fecha_vencimiento DATE,  -- <--- NUEVO CAMPO
                    fecha_registro DATE DEFAULT CURRENT_DATE,
                    activo BOOLEAN DEFAULT 1,
                    FOREIGN KEY(plan_id) REFERENCES planes(id)
                )
            ''')

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

    def inicializar_planes(self, cursor):
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

                # Calculamos vencimiento: Hoy + 30 días
                hoy = datetime.now()
                vencimiento = hoy + timedelta(days=30)
                fecha_venc_str = vencimiento.strftime('%Y-%m-%d')

                cursor.execute('''
                    INSERT INTO miembros (nombre, apellido, dni, plan_id, ingresos_restantes, ultimo_pago, fecha_vencimiento)
                    VALUES (?, ?, ?, ?, ?, DATE('now'), ?)
                ''', (nombre, apellido, dni, plan_id, ingresos, fecha_venc_str))
                
                conn.commit()
                return True
            except Exception as e:
                print(f"Error al registrar: {e}")
                return False
            finally:
                conn.close()
        return False

    def renovar_socio(self, id_socio, plan_nombre, pases_a_sumar):
        conn = self.conectar()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT id FROM planes WHERE nombre = ?", (plan_nombre,))
                plan_result = cursor.fetchone()
                plan_id = plan_result[0] if plan_result else None

                hoy = datetime.now()
                vencimiento = hoy + timedelta(days=30)
                fecha_venc_str = vencimiento.strftime('%Y-%m-%d')

                cursor.execute('''
                    UPDATE miembros 
                    SET plan_id = ?, 
                        ingresos_restantes = ?, 
                        ultimo_pago = DATE('now'),
                        fecha_vencimiento = ?
                    WHERE id = ?
                ''', (plan_id, pases_a_sumar, fecha_venc_str, id_socio))
                
                conn.commit()
                return True
            except Exception as e:
                print(f"Error al renovar: {e}")
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
                
                cursor.execute('''
                    SELECT m.id, m.nombre, m.apellido, p.nombre, m.ingresos_restantes, m.fecha_vencimiento 
                    FROM miembros m
                    LEFT JOIN planes p ON m.plan_id = p.id
                    WHERE m.dni = ? AND m.activo = 1
                ''', (dni,))
                
                resultado = cursor.fetchone()
                ahora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                
                if resultado:
                    m_id, nombre, apellido, plan, ingresos, fecha_venc = resultado
                    
                    hoy_str = datetime.now().strftime('%Y-%m-%d')
                    
                    es_vencido = False
                    if fecha_venc and hoy_str >= fecha_venc:
                        es_vencido = True
                    
                    if ingresos > 0 and not es_vencido:
                        
                        cursor.execute("UPDATE miembros SET ingresos_restantes = ingresos_restantes - 1 WHERE id = ?", (m_id,))
                        
                        cursor.execute("INSERT INTO historial_acceso (miembro_id, fecha_hora, tipo_acceso) VALUES (?, ?, 'Ingreso')", (m_id, ahora))
                        
                        conn.commit()
                        
                        info_socio = {
                            "nombre": nombre, 
                            "apellido": apellido, 
                            "plan": plan,
                            "vencimiento": fecha_venc,
                            "ingresos_restantes": ingresos - 1,
                            "acceso": True,
                            "mensaje": "PASE HABILITADO"
                        }
                    else:
                        motivo = "Rechazado"
                        mensaje_pantalla = "ACCESO DENEGADO"
                        
                        if es_vencido:
                            motivo = "Vencido"
                            mensaje_pantalla = "⛔ CUOTA VENCIDA"
                        elif ingresos <= 0:
                            motivo = "Sin Pases"
                            mensaje_pantalla = "⛔ SIN PASES"

                        cursor.execute("INSERT INTO historial_acceso (miembro_id, fecha_hora, tipo_acceso) VALUES (?, ?, ?)", (m_id, ahora, motivo))
                        conn.commit()
                        
                        info_socio = {
                            "nombre": nombre, 
                            "apellido": apellido, 
                            "plan": plan,
                            "vencimiento": fecha_venc,
                            "ingresos_restantes": ingresos,
                            "acceso": False,
                            "mensaje": mensaje_pantalla
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
    def editar_socio(self, id_socio, nombre, apellido, dni):
        """Modifica los datos personales de un socio existente"""
        conn = self.conectar()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE miembros 
                    SET nombre = ?, apellido = ?, dni = ?
                    WHERE id = ?
                ''', (nombre, apellido, dni, id_socio))
                
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                print("Error: El DNI ya existe en otro socio.")
                return False
            except Exception as e:
                print(f"Error al editar: {e}")
                return False
            finally:
                conn.close()
        return False
    
    def eliminar_socio(self, id_socio):
        """Marca al socio como inactivo (Borrado lógico) para que no aparezca más"""
        conn = self.conectar()
        if conn:
            try:
                cursor = conn.cursor()
                cursor.execute("UPDATE miembros SET activo = 0 WHERE id = ?", (id_socio,))
                conn.commit()
                return True
            except Exception as e:
                print(f"Error al eliminar: {e}")
                return False
            finally:
                conn.close()
        return False
    def verificar_dni_existente(self, dni):
        conn = self.conectar()
        if conn:
            cursor = conn.cursor()
            cursor.execute("SELECT activo FROM miembros WHERE dni = ?", (dni,))
            resultado = cursor.fetchone()
            conn.close()
            if resultado:
                return True, resultado[0] # (Existe: Sí, Activo: 0 o 1)
            return False, False # (Existe: No)
        return False, False

    def reactivar_socio(self, nombre, apellido, dni, plan_nombre, ingresos):
        """Revive a un socio inactivo actualizando sus datos"""
        conn = self.conectar()
        if conn:
            try:
                cursor = conn.cursor()
                
                cursor.execute("SELECT id FROM planes WHERE nombre = ?", (plan_nombre,))
                plan_result = cursor.fetchone()
                plan_id = plan_result[0] if plan_result else None

                hoy = datetime.now()
                vencimiento = hoy + timedelta(days=30)
                fecha_venc_str = vencimiento.strftime('%Y-%m-%d')

                cursor.execute('''
                    UPDATE miembros 
                    SET nombre = ?, apellido = ?, plan_id = ?, 
                        ingresos_restantes = ?, ultimo_pago = DATE('now'),
                        fecha_vencimiento = ?, activo = 1
                    WHERE dni = ?
                ''', (nombre, apellido, plan_id, ingresos, fecha_venc_str, dni))
                
                conn.commit()
                return True
            except Exception as e:
                print(f"Error al reactivar: {e}")
                return False
            finally:
                conn.close()
        return False