# utils/estructura.py
import os
import shutil
from datetime import datetime
import sqlite3

class GeneradorEstructura:
    def __init__(self):
        self.estructura = {
            'Obras': [
                'Presupuesto Autorizado',
                'Cronograma de Trabajo',
                'Lista de Insumos',
                'Requisición de Material'
            ],
            'Compras': [
                'Cotizaciones',
                'Autorización de Compra',
                'Orden de Compra',
                'Solicitud de Pedido'
            ],
            'Gastos': [
                'Materiales',
                'Mano de Obra',
                'Maquinaria',
                'Otros Gastos'
            ],
            'Inventarios': [
                'Recepción de Material',
                'Entradas',
                'Salidas'
            ],
            'Reportes': [
                'Financieros',
                'Operativos',
                'Administrativos'
            ]
        }
        self.log = []
    
    def generar(self, ruta_base, nombre_empresa, nombre_proyecto, copiar_plantillas=False):
        """
        Genera toda la estructura de carpetas para un proyecto
        """
        # Limpiar nombres
        nombre_empresa = self._limpiar_nombre(nombre_empresa)
        nombre_proyecto = self._limpiar_nombre(nombre_proyecto)
        
        ruta_proyecto = os.path.join(ruta_base, nombre_empresa, nombre_proyecto)
        self.log = []
        
        try:
            if os.path.exists(ruta_proyecto):
                return False, f"⚠️ Ya existe una estructura para '{nombre_proyecto}'"
            
            # Crear carpeta principal
            os.makedirs(ruta_proyecto, exist_ok=True)
            self.log.append(f"✅ Carpeta principal: {ruta_proyecto}")
            
            # Crear carpetas y subcarpetas
            for carpeta, subcarpetas in self.estructura.items():
                ruta_carpeta = os.path.join(ruta_proyecto, carpeta)
                os.makedirs(ruta_carpeta, exist_ok=True)
                self.log.append(f"  ✅ {carpeta}/")
                
                for sub in subcarpetas:
                    ruta_sub = os.path.join(ruta_carpeta, sub)
                    os.makedirs(ruta_sub, exist_ok=True)
                    self.log.append(f"    ✅ {sub}/")
                    
                    if copiar_plantillas:
                        self._copiar_plantilla(ruta_sub, sub)
            
            # Crear README
            self._crear_readme(ruta_proyecto, nombre_empresa, nombre_proyecto)
            
            # Guardar bitácora
            self._guardar_bitacora(ruta_proyecto)
            
            # Actualizar ruta en BD
            self._actualizar_ruta_proyecto(nombre_proyecto, ruta_proyecto)
            
            return True, self.log
            
        except Exception as e:
            return False, f"❌ Error: {str(e)}"
    
    def _limpiar_nombre(self, nombre):
        caracteres_invalidos = ['/', '\\', ':', '*', '?', '"', '<', '>', '|']
        for char in caracteres_invalidos:
            nombre = nombre.replace(char, '')
        return nombre.strip()
    
    def _copiar_plantilla(self, ruta_destino, nombre_carpeta):
        """Copia plantillas si existen"""
        try:
            conn = sqlite3.connect('data/sigevi.db')
            c = conn.cursor()
            c.execute("SELECT valor FROM configuracion WHERE clave = 'ruta_plantillas'")
            resultado = c.fetchone()
            conn.close()
            
            if not resultado:
                return
            
            ruta_plantillas = resultado[0]
            archivo = f"plantilla_{nombre_carpeta.replace(' ', '_')}.xlsx"
            
            origen = os.path.join(ruta_plantillas, archivo)
            destino = os.path.join(ruta_destino, archivo)
            
            if os.path.exists(origen):
                shutil.copy2(origen, destino)
                self.log.append(f"      📄 Plantilla: {archivo}")
        except:
            pass
    
    def _crear_readme(self, ruta_proyecto, empresa, proyecto):
        archivo = os.path.join(ruta_proyecto, 'README.md')
        with open(archivo, 'w', encoding='utf-8') as f:
            f.write(f"# {proyecto}\n\n")
            f.write(f"**Empresa:** {empresa}\n")
            f.write(f"**Fecha:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("## Estructura\n\n```\n")
            f.write(f"{proyecto}/\n")
            for carpeta in self.estructura.keys():
                f.write(f"├── {carpeta}/\n")
                for sub in self.estructura[carpeta]:
                    f.write(f"│   └── {sub}/\n")
            f.write("```\n")
    
    def _guardar_bitacora(self, ruta_proyecto):
        with open(os.path.join(ruta_proyecto, 'bitacora_generacion.txt'), 'w', encoding='utf-8') as f:
            f.write("="*60 + "\n")
            f.write("BITÁCORA DE GENERACIÓN\n")
            f.write("="*60 + "\n\n")
            f.write(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("\n".join(self.log))
            f.write(f"\n\nTotal carpetas: {len(self.log)}")
    
    def _actualizar_ruta_proyecto(self, nombre_proyecto, ruta_proyecto):
        try:
            conn = sqlite3.connect('data/sigevi.db')
            c = conn.cursor()
            c.execute("""
                UPDATE proyectos 
                SET carpeta_ruta = ? 
                WHERE nombre = ?
            """, (ruta_proyecto, nombre_proyecto))
            conn.commit()
            conn.close()
        except:
            pass