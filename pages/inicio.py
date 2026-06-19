# pages/1_Inicio.py
import streamlit as st
import sqlite3

def show():
    st.markdown("### 📊 Dashboard Principal")
    
    # Métricas
    col1, col2, col3, col4 = st.columns(4)
    
    conn = sqlite3.connect('data/sigevi.db')
    c = conn.cursor()
    
    c.execute("SELECT COUNT(*) FROM empresas WHERE activo = 1")
    total_empresas = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM proyectos WHERE activo = 1")
    total_proyectos = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM proyectos WHERE carpeta_ruta IS NOT NULL")
    proyectos_con_estructura = c.fetchone()[0]
    
    c.execute("SELECT COUNT(*) FROM bitacora")
    total_acciones = c.fetchone()[0]
    
    conn.close()
    
    with col1:
        st.markdown(f"""
            <div class="metric-card">
                <div>🏢 Empresas</div>
                <div class="metric-number">{total_empresas}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown(f"""
            <div class="metric-card">
                <div>📁 Proyectos</div>
                <div class="metric-number">{total_proyectos}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col3:
        st.markdown(f"""
            <div class="metric-card">
                <div>📂 Estructuras</div>
                <div class="metric-number">{proyectos_con_estructura}</div>
            </div>
        """, unsafe_allow_html=True)
    
    with col4:
        st.markdown(f"""
            <div class="metric-card">
                <div>📝 Acciones</div>
                <div class="metric-number">{total_acciones}</div>
            </div>
        """, unsafe_allow_html=True)
    
    st.markdown("<hr class='custom-divider'>", unsafe_allow_html=True)
    
    # Últimas acciones
    st.markdown("### 📋 Últimas Acciones")
    
    conn = sqlite3.connect('data/sigevi.db')
    c = conn.cursor()
    c.execute("""
        SELECT fecha, modulo, accion, detalles 
        FROM bitacora 
        ORDER BY fecha DESC 
        LIMIT 10
    """)
    acciones = c.fetchall()
    conn.close()
    
    if acciones:
        for fecha, modulo, accion, detalles in acciones:
            st.info(f"🕐 {fecha} - **{modulo}**: {accion} {detalles}")
    else:
        st.info("ℹ️ No hay acciones registradas aún")