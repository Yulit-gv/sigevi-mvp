# pages/5_Configuracion.py
import streamlit as st
import sqlite3
from utils.database import Database

def show():
    db = Database()
    st.markdown("### ⚙️ Configuración del Sistema")
    
    conn = sqlite3.connect('data/sigevi.db')
    c = conn.cursor()
    
    # Obtener configuración actual
    c.execute("SELECT clave, valor, descripcion FROM configuracion")
    config = {row[0]: row for row in c.fetchall()}
    conn.close()
    
    with st.form("form_configuracion"):
        st.markdown("#### 📁 Rutas de Almacenamiento")
        
        ruta_base = st.text_input(
            "📁 Ruta base para proyectos",
            value=config.get('ruta_base', ['', 'C:/SiGeVI/Proyectos', ''])[1],
            help="Ruta donde se almacenarán las carpetas de los proyectos"
        )
        
        ruta_plantillas = st.text_input(
            "📄 Ruta de plantillas",
            value=config.get('ruta_plantillas', ['', 'C:/SiGeVI/Plantillas', ''])[1],
            help="Ruta donde se encuentran las plantillas maestras"
        )
        
        st.markdown("---")
        st.markdown("#### ℹ️ Información del Sistema")
        st.caption("🏗️ SiGeVI v1.0 MVP")
        st.caption("Sistema de Gestión y Visibilidad Integral")
        st.caption("Base de datos: SQLite")
        
        submitted = st.form_submit_button("💾 Guardar Configuración", use_container_width=True)
        
        if submitted:
            try:
                conn = sqlite3.connect('data/sigevi.db')
                c = conn.cursor()
                
                c.execute("UPDATE configuracion SET valor = ? WHERE clave = 'ruta_base'", (ruta_base,))
                c.execute("UPDATE configuracion SET valor = ? WHERE clave = 'ruta_plantillas'", (ruta_plantillas,))
                
                conn.commit()
                conn.close()
                
                db.registrar_bitacora(
                    "Configuración actualizada",
                    "Configuración",
                    "Admin",
                    "Rutas de almacenamiento"
                )
                
                st.success("✅ Configuración guardada exitosamente!")
                st.balloons()
                
            except Exception as e:
                st.error(f"❌ Error: {str(e)}")