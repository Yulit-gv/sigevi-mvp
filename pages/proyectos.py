# pages/3_Proyectos.py
import streamlit as st
import sqlite3
from datetime import date
from utils.database import Database

def show():
    db = Database()
    st.markdown("### 📁 Gestión de Proyectos")
    
    # Verificar empresas
    conn = sqlite3.connect('data/sigevi.db')
    c = conn.cursor()
    c.execute("SELECT id, nombre FROM empresas WHERE activo = 1 ORDER BY nombre")
    empresas = c.fetchall()
    conn.close()
    
    if not empresas:
        st.warning("⚠️ Primero debes registrar una empresa")
        return
    
    tab1, tab2 = st.tabs(["📋 Lista de Proyectos", "➕ Nuevo Proyecto"])
    
    # ===== TAB 1: Lista =====
    with tab1:
        conn = sqlite3.connect('data/sigevi.db')
        c = conn.cursor()
        c.execute("""
            SELECT p.id, p.nombre, e.nombre as empresa, p.descripcion, 
                   p.fecha_inicio, p.fecha_fin, p.fecha_registro, p.carpeta_ruta
            FROM proyectos p
            JOIN empresas e ON p.empresa_id = e.id
            WHERE p.activo = 1
            ORDER BY p.fecha_registro DESC
        """)
        proyectos = c.fetchall()
        conn.close()
        
        if proyectos:
            for p in proyectos:
                with st.container():
                    col1, col2, col3 = st.columns([3, 2, 2])
                    
                    with col1:
                        st.markdown(f"**🏗️ {p[1]}**")
                        st.caption(f"📝 {p[3] or 'Sin descripción'}")
                    
                    with col2:
                        st.write(f"**Empresa:** {p[2]}")
                        if p[4] and p[5]:
                            st.caption(f"📅 {p[4]} → {p[5]}")
                    
                    with col3:
                        if p[7]:
                            st.success("✅ Estructura generada")
                        else:
                            st.warning("⏳ Sin estructura")
                    
                    st.divider()
        else:
            st.info("ℹ️ No hay proyectos registrados")
    
    # ===== TAB 2: Nuevo Proyecto =====
    with tab2:
        with st.form("form_proyecto", clear_on_submit=True):
            st.markdown("#### 📝 Datos del Proyecto")
            
            col1, col2 = st.columns(2)
            
            with col1:
                empresa_id = st.selectbox(
                    "🏢 Empresa *",
                    options=empresas,
                    format_func=lambda x: x[1]
                )
                nombre = st.text_input("📛 Nombre del proyecto *", placeholder="Ej: Edificio Torre Sur")
            
            with col2:
                descripcion = st.text_area("📝 Descripción", placeholder="Descripción del proyecto", height=80)
                fecha_inicio = st.date_input("📅 Fecha inicio", value=date.today())
                fecha_fin = st.date_input("📅 Fecha fin")
            
            generar_estructura = st.checkbox("🚀 Generar estructura automáticamente", value=True)
            
            submitted = st.form_submit_button("💾 Registrar Proyecto", use_container_width=True)
            
            if submitted:
                if not nombre:
                    st.error("❌ El nombre es obligatorio")
                else:
                    try:
                        conn = sqlite3.connect('data/sigevi.db')
                        c = conn.cursor()
                        c.execute("""
                            INSERT INTO proyectos 
                            (nombre, empresa_id, descripcion, fecha_inicio, fecha_fin)
                            VALUES (?, ?, ?, ?, ?)
                        """, (nombre, empresa_id[0], descripcion, fecha_inicio, fecha_fin))
                        
                        proyecto_id = c.lastrowid
                        conn.commit()
                        conn.close()
                        
                        db.registrar_bitacora(
                            "Proyecto registrado",
                            "Proyectos",
                            "Admin",
                            f"Proyecto: {nombre}, Empresa: {empresa_id[1]}"
                        )
                        
                        st.success(f"✅ ¡Proyecto '{nombre}' registrado!")
                        st.balloons()
                        st.rerun()
                        
                    except sqlite3.IntegrityError:
                        st.error("❌ Ya existe un proyecto con ese nombre")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")