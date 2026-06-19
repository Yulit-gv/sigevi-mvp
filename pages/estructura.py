# pages/4_Estructura.py
import streamlit as st
import sqlite3
import os
from utils.estructura import GeneradorEstructura
from utils.database import Database

def show():
    db = Database()
    generador = GeneradorEstructura()
    st.markdown("### 📂 Generación de Estructura de Carpetas")
    
    # Obtener proyectos sin estructura
    conn = sqlite3.connect('data/sigevi.db')
    c = conn.cursor()
    c.execute("""
        SELECT p.id, p.nombre, e.nombre as empresa, e.id as empresa_id
        FROM proyectos p
        JOIN empresas e ON p.empresa_id = e.id
        WHERE p.activo = 1 AND p.carpeta_ruta IS NULL
        ORDER BY p.nombre
    """)
    proyectos_sin_estructura = c.fetchall()
    
    c.execute("""
        SELECT p.id, p.nombre, e.nombre as empresa, p.carpeta_ruta
        FROM proyectos p
        JOIN empresas e ON p.empresa_id = e.id
        WHERE p.activo = 1 AND p.carpeta_ruta IS NOT NULL
        ORDER BY p.nombre
    """)
    proyectos_con_estructura = c.fetchall()
    conn.close()
    
    # ===== Proyectos sin estructura =====
    st.subheader("🚀 Generar Nueva Estructura")
    
    if proyectos_sin_estructura:
        with st.form("form_generar_estructura"):
            proyecto_seleccionado = st.selectbox(
                "Selecciona un proyecto para generar su estructura:",
                options=proyectos_sin_estructura,
                format_func=lambda x: f"{x[1]} ({x[2]})"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                copiar_plantillas = st.checkbox("📄 Copiar plantillas", value=False)
            with col2:
                ruta_base = st.text_input(
                    "📁 Ruta base",
                    value="C:/SiGeVI/Proyectos",
                    help="Ruta donde se crearán las carpetas"
                )
            
            submitted = st.form_submit_button("🚀 Generar Estructura", use_container_width=True)
            
            if submitted:
                with st.spinner("Generando estructura..."):
                    exito, resultado = generador.generar(
                        ruta_base,
                        proyecto_seleccionado[2],  # nombre empresa
                        proyecto_seleccionado[1],  # nombre proyecto
                        copiar_plantillas
                    )
                    
                    if exito:
                        st.success("✅ ¡Estructura generada exitosamente!")
                        db.registrar_bitacora(
                            "Estructura generada",
                            "Estructura",
                            "Admin",
                            f"Proyecto: {proyecto_seleccionado[1]}"
                        )
                        
                        with st.expander("📂 Ver estructura generada", expanded=True):
                            for linea in resultado:
                                st.text(linea)
                        
                        st.info(f"📁 Ubicación: {ruta_base}/{proyecto_seleccionado[2]}/{proyecto_seleccionado[1]}")
                        st.balloons()
                    else:
                        st.error(resultado)
    else:
        st.info("ℹ️ Todos los proyectos ya tienen estructura generada")
    
    # ===== Proyectos con estructura =====
    st.markdown("---")
    st.subheader("📂 Proyectos con Estructura")
    
    if proyectos_con_estructura:
        for p in proyectos_con_estructura:
            with st.container():
                col1, col2, col3 = st.columns([2, 2, 1])
                with col1:
                    st.markdown(f"**{p[1]}**")
                    st.caption(f"Empresa: {p[2]}")
                with col2:
                    st.caption(f"📁 {p[3]}")
                with col3:
                    if st.button("🔄 Regenerar", key=f"reg_{p[0]}"):
                        # Lógica de regeneración
                        exito, resultado = generador.regenerar_estructura(p[3])
                        if exito:
                            st.success("✅ Estructura regenerada")
                        else:
                            st.error(resultado)
                st.divider()
    else:
        st.info("ℹ️ No hay proyectos con estructura generada")