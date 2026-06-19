# pages/2_Empresas.py
import streamlit as st
import sqlite3
import pandas as pd
from utils.database import Database

def show():
    db = Database()
    st.markdown("### 🏢 Gestión de Empresas")
    
    tab1, tab2 = st.tabs(["📋 Lista de Empresas", "➕ Nueva Empresa"])
    
    # ===== TAB 1: Lista =====
    with tab1:
        conn = sqlite3.connect('data/sigevi.db')
        c = conn.cursor()
        c.execute("""
            SELECT id, nombre, rfc, regimen_fiscal, representante_legal, 
                   telefono, email, fecha_registro
            FROM empresas 
            WHERE activo = 1
            ORDER BY nombre
        """)
        empresas = c.fetchall()
        conn.close()
        
        if empresas:
            df = pd.DataFrame(empresas, columns=[
                'ID', 'Nombre', 'RFC', 'Régimen', 'Representante',
                'Teléfono', 'Email', 'Registro'
            ])
            st.dataframe(
                df[['Nombre', 'RFC', 'Representante', 'Registro']],
                use_container_width=True,
                hide_index=True
            )
            
            for empresa in empresas:
                with st.expander(f"🏢 {empresa[1]}"):
                    col1, col2 = st.columns(2)
                    with col1:
                        st.write(f"**RFC:** {empresa[2] or 'No registrado'}")
                        st.write(f"**Régimen:** {empresa[3] or 'No registrado'}")
                    with col2:
                        st.write(f"**Representante:** {empresa[4] or 'No registrado'}")
                        st.write(f"**Registro:** {empresa[7][:10]}")
        else:
            st.info("ℹ️ No hay empresas registradas")
    
    # ===== TAB 2: Nueva Empresa =====
    with tab2:
        with st.form("form_empresa", clear_on_submit=True):
            st.markdown("#### 📝 Datos de la Empresa")
            
            col1, col2 = st.columns(2)
            
            with col1:
                nombre = st.text_input("📛 Nombre *", placeholder="Ej: Constructora ABC")
                rfc = st.text_input("🔢 RFC", placeholder="Ej: ABC123456789")
                regimen = st.text_input("📋 Régimen fiscal", placeholder="Ej: Régimen General")
            
            with col2:
                representante = st.text_input("👤 Representante legal")
                telefono = st.text_input("📞 Teléfono", placeholder="55-1234-5678")
                email = st.text_input("📧 Email", placeholder="contacto@empresa.com")
            
            direccion = st.text_area("📍 Dirección", placeholder="Calle, número, colonia, ciudad", height=80)
            
            submitted = st.form_submit_button("💾 Registrar Empresa", use_container_width=True)
            
            if submitted:
                if not nombre:
                    st.error("❌ El nombre es obligatorio")
                else:
                    try:
                        conn = sqlite3.connect('data/sigevi.db')
                        c = conn.cursor()
                        c.execute("""
                            INSERT INTO empresas 
                            (nombre, rfc, regimen_fiscal, direccion, representante_legal, telefono, email)
                            VALUES (?, ?, ?, ?, ?, ?, ?)
                        """, (nombre, rfc, regimen, direccion, representante, telefono, email))
                        conn.commit()
                        conn.close()
                        
                        db.registrar_bitacora(
                            "Empresa registrada",
                            "Empresas",
                            "Admin",
                            f"Nombre: {nombre}"
                        )
                        
                        st.success(f"✅ ¡Empresa '{nombre}' registrada!")
                        st.balloons()
                        st.rerun()
                    except sqlite3.IntegrityError:
                        st.error("❌ Ya existe una empresa con ese nombre")
                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")