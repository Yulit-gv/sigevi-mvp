# utils/database.py
import sqlite3
import os

class Database:
    def __init__(self):
        self.db_path = 'data/sigevi.db'
    
    def ejecutar_consulta(self, query, params=None):
        """Ejecuta una consulta y retorna los resultados"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        if params:
            c.execute(query, params)
        else:
            c.execute(query)
        
        resultados = c.fetchall()
        conn.commit()
        conn.close()
        return resultados
    
    def ejecutar_insercion(self, query, params):
        """Ejecuta una inserción y retorna el ID generado"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(query, params)
        id_generado = c.lastrowid
        conn.commit()
        conn.close()
        return id_generado
    
    def registrar_bitacora(self, accion, modulo="Sistema", usuario="Admin", detalles=""):
        """Registra una acción en la bitácora"""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            INSERT INTO bitacora (accion, modulo, usuario, detalles)
            VALUES (?, ?, ?, ?)
        """, (accion, modulo, usuario, detalles))
        conn.commit()
        conn.close()