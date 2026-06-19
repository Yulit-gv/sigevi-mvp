import streamlit as st
import os
import sqlite3
from datetime import datetime

# Configuración de la página
st.set_page_config(
    page_title="SiGeVI - Sistema de Gestión Integral",
    page_icon="🏗️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
        /* Header principal */
        .main-header {
            background: linear-gradient(135deg, #1a237e, #0d47a1);
            padding: 1.5rem;
            border-radius: 12px;
            color: white;
            text-align: center;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        }
        .main-header h1 {
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
            letter-spacing: 1px;
        }
        .main-header p {
            margin: 0.5rem 0 0 0;
            opacity: 0.9;
            font-size: 1.1rem;
        }
        
        /* Tarjetas */
        .card {
            background: white;
            padding: 1.5rem;
            border-radius: 12px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.08);
            margin: 1rem 0;
            border: 1px solid #e8eaf6;
            transition: all 0.3s ease;
        }
        .card:hover {
            box-shadow: 0 4px 20px rgba(0,0,0,0.12);
            transform: translateY(-2px);
        }
        
        /* Métricas */
        .metric-card {
            background: linear-gradient(135deg, #f5f7fa, #e8eaf6);
            padding: 1.5rem;
            border-radius: 12px;
            text-align: center;
            border-left: 4px solid #1a237e;
        }
        .metric-number {
            font-size: 2.5rem;
            font-weight: 700;
            color: #1a237e;
            margin: 0.5rem 0;
        }
        
        /* Botones */
        .stButton > button {
            background: #1a237e;
            color: white;
            border-radius: 8px;
            padding: 0.5rem 2rem;
            font-weight: 600;
            transition: all 0.3s ease;
            border: none;
        }
        .stButton > button:hover {
            background: #0d47a1;
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(26, 35, 126, 0.3);
        }
        
        /* Divider */
        .custom-divider {
            margin: 1.5rem 0;
            border: 0;
            height: 2px;
            background: linear-gradient(to right, #e8eaf6, #1a237e, #e8eaf6);
        }
        
        /* Footer */
        .footer {
            text-align: center;
            padding: 1.5rem;
            color: #666;
            font-size: 0.9rem;
            border-top: 1px solid #e8eaf6;
            margin-top: 2rem;
        }
        
        /* Badges */
        .badge-success {
            background: #e8f5e9;
            color: #2e7d32;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            display: inline-block;
        }
        .badge-warning {
            background: #fff3e0;
            color: #e65100;
            padding: 0.25rem 0.75rem;
            border-radius: 20px;
            font-size: 0.8rem;
            font-weight: 600;
            display: inline-block;
        }
    </style>
""", unsafe_allow_html=True)

# Inicializar base de datos
def init_db():
    """Crea las tablas necesarias si no existen"""
    os.makedirs('data', exist_ok=True)
    conn = sqlite3.connect('data/sigevi.db')
    c = conn.cursor()
    
    # Tabla Empresas
    c.execute('''CREATE TABLE IF NOT EXISTS empresas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT UNIQUE NOT NULL,
        rfc TEXT,
        regimen_fiscal TEXT,
        direccion TEXT,
        representante_legal TEXT,
        telefono TEXT,
        email TEXT,
        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        carpeta_ruta TEXT,
        activo INTEGER DEFAULT 1
    )''')
    
    # Tabla Proyectos
    c.execute('''CREATE TABLE IF NOT EXISTS proyectos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nombre TEXT UNIQUE NOT NULL,
        empresa_id INTEGER,
        descripcion TEXT,
        fecha_inicio DATE,
        fecha_fin DATE,
        fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        carpeta_ruta TEXT,
        activo INTEGER DEFAULT 1,
        FOREIGN KEY (empresa_id) REFERENCES empresas (id)
    )''')
    
    # Tabla Bitácora
    c.execute('''CREATE TABLE IF NOT EXISTS bitacora (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        accion TEXT,
        modulo TEXT,
        usuario TEXT,
        detalles TEXT,
        fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Tabla Configuración
    c.execute('''CREATE TABLE IF NOT EXISTS configuracion (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        clave TEXT UNIQUE NOT NULL,
        valor TEXT,
        descripcion TEXT,
        fecha_actualizacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )''')
    
    # Insertar configuración por defecto si no existe
    c.execute("SELECT COUNT(*) FROM configuracion WHERE clave = 'ruta_base'")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO configuracion (clave, valor, descripcion) VALUES (?, ?, ?)",
                  ('ruta_base', 'C:/SiGeVI/Proyectos', 'Ruta base para almacenar proyectos'))
    
    c.execute("SELECT COUNT(*) FROM configuracion WHERE clave = 'ruta_plantillas'")
    if c.fetchone()[0] == 0:
        c.execute("INSERT INTO configuracion (clave, valor, descripcion) VALUES (?, ?, ?)",
                  ('ruta_plantillas', 'C:/SiGeVI/Plantillas', 'Ruta de las plantillas maestras'))
    
    conn.commit()
    conn.close()

# Ejecutar inicialización
init_db()

# ============================================
# SIDEBAR - Navegación
# ============================================

with st.sidebar:
    st.markdown("""
        <div style="text-align: center; padding: 1rem 0;">
            <h2 style="color: #1a237e; margin: 0;">🏗️ SiGeVI</h2>
            <p style="color: #666; margin: 0; font-size: 0.9rem;">Sistema de Gestión Integral</p>
        </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    menu = st.radio(
        "📋 NAVEGACIÓN",
        [
            "🏠 Inicio",
            "🏢 Empresas",
            "📁 Proyectos",
            "📂 Estructura",
            "⚙️ Configuración"
        ],
        index=0
    )
    
    st.markdown("---")
    st.caption(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    st.caption("v1.0 MVP")

# ============================================
# CONTENIDO PRINCIPAL - HEADER
# ============================================

st.markdown("""
    <div class="main-header">
        <h1>🏗️ SiGeVI</h1>
        <p>Sistema de Gestión y Visibilidad Integral</p>
    </div>
""", unsafe_allow_html=True)

# ============================================
# IMPORTAR PÁGINAS
# ============================================

if menu == "🏠 Inicio":
    import pages.inicio as inicio
    inicio.show()
elif menu == "🏢 Empresas":
    import pages.empresas as empresas
    empresas.show()
elif menu == "📁 Proyectos":
    import pages.proyectos as proyectos
    proyectos.show()
elif menu == "📂 Estructura":
    import pages.estructura as estructura
    estructura.show()
elif menu == "⚙️ Configuración":
    import pages.configuracion as configuracion
    configuracion.show()

# ============================================
# FOOTER
# ============================================

st.markdown("""
    <div class="footer">
        <p> SiGeVI - Sistema de Gestión y Visibilidad Integral</p>
        <p style="font-size: 0.8rem; color: #999;">MVP - Generación de Estructura de Carpetas</p>
    </div>
""", unsafe_allow_html=True)