import streamlit as st
import google.generativeai as genai
import time

# 1. CONFIGURACIÓN ESTÉTICA (PACS DARK MODE)
st.set_page_config(page_title="Radiology AI PACS", layout="wide", initial_sidebar_state="expanded")

# Inyección de CSS para diseño premium y minimalista
st.markdown("""
    <style>
    /* Fondo principal y tipografía */
    .stApp {
        background-color: #0b0b0f;
        color: #cbd5e1;
        font-family: 'Inter', sans-serif;
    }
    
    /* Paneles laterales y contenedores */
    [data-testid="stSidebar"] {
        background-color: #111116;
        border-right: 1px solid #1f1f27;
    }
    
    /* Estilo para los paneles (Glassmorphism ligero) */
    .pacs-panel {
        background: rgba(17, 17, 22, 0.7);
        border: 1px solid rgba(139, 92, 246, 0.2);
        border-radius: 12px;
        padding: 20px;
        margin-bottom: 20px;
    }

    /* Títulos y acentos */
    h1, h2, h3 {
        color: #ffffff !important;
        font-weight: 600 !important;
    }
    
    .stButton>button {
        background-color: #8b5cf6 !important;
        color: white !important;
        border-radius: 8px !important;
        border: none !important;
        width: 100%;
        transition: 0.3s;
    }
    
    .stButton>button:hover {
        background-color: #7c3aed !important;
        box-shadow: 0 0 15px rgba(139, 92, 246, 0.4);
    }

    /* Editor de texto */
    .stTextArea textarea {
        background-color: #16161d !important;
        color: #e2e8f0 !important;
        border: 1px solid #2d2d39 !important;
        border-radius: 8px !important;
        font-family: 'Courier New', monospace;
    }
    </style>
    """, unsafe_allow_html=True)

# 2. LÓGICA DE SESIÓN (Para mantener el reporte editable)
if 'reporte_final' not in st.session_state:
    st.session_state.reporte_final = ""

# 3. BARRA LATERAL (Configuración y RADS)
with st.sidebar:
    st.title("⚙️ Panel de Control")
    api_key = st.text_input("Google API Key", type="password")
    
    st.divider()
    st.subheader("📚 Panel de Referencia")
    tab_rads, tab_diff = st.tabs(["RADS", "Diferenciales"])
    
    with tab_rads:
        st.caption("Guías rápidas de clasificación")
        rad_select = st.selectbox("Seleccionar escala:", ["BI-RADS", "PI-RADS", "LI-RADS", "Lung-RADS"])
        st.info(f"Mostrando criterios para {rad_select}...")
        
    with tab_diff:
        st.caption("Sugerencias automáticas")
        st.write("• Quiste vs Sólido\n• Infeccioso vs Neoplásico")

# 4. CUERPO PRINCIPAL (Layout Dual)
if api_key:
    genai.configure(api_key=api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')

    # Encabezado Médico
    col_title, col_status = st.columns([3, 1])
    with col_title:
        st.title("🩺 Estación de Trabajo Radiológica IA")
    with col_status:
        st.success("IA Conectada")

    # Layout de Paneles
    panel_izq, panel_der = st.columns([1, 1.2], gap="large")

    with panel_izq:
        st.subheader("🎙️ Transcripción & Dictado")
        
        # Selector de Modalidad y Subespecialidad
        mod_col, sub_col = st.columns(2)
        with mod_col:
            modalidad = st.selectbox("Modalidad", ["Rayos X", "Tomografía", "Resonancia", "Ultrasonido", "US Doppler", "Fluoroscopia"])
        with sub_col:
            subesp = st.selectbox("Subespecialidad", ["Neurorradiología", "MSK", "Tórax", "Abdomen", "Ultrasonido"])
        
        # Área de entrada (Audio o Texto)
        audio_file = st.audio_input("Dictar hallazgos (Presiona para iniciar)")
        hallazgos_dictado = st.text_area("Hallazgos crudos / Notas:", height=200, placeholder="Dicta o escribe aquí tus hallazgos...")
        
        # Opciones de IA
        comp_col, style_col = st.columns(2)
        with comp_col:
            complejidad = st.select_slider("Complejidad", options=["Residente", "Adjunto", "Fellow", "Experto"])
        with style_col:
            estilo = st.selectbox("Estilo", ["Conciso", "Académico", "Institucional", "Fellow MSK"])

        if st.button("🪄 Generar Reporte Estructurado"):
            with st.spinner("Procesando con IA Radiológica..."):
                prompt = f"""
                Actúa como un Radiólogo {complejidad} con subespecialidad en {subesp}.
                Genera un informe estructurado para {modalidad} en estilo {estilo}.
                
                Instrucciones específicas:
                1. Corrige gramática médica.
                2. Genera una descripción detallada.
                3. Incluye una conclusión automática inteligente.
                4. Si aplica, sugiere diagnósticos diferenciales.
                
                Información proporcionada: {hallazgos_dictado}
                """
                
                inputs = [prompt]
                if audio_file:
                    inputs.append({"mime_type": "audio/wav", "data": audio_file.getvalue()})
                
                response = model.generate_content(inputs)
                st.session_state.reporte_final = response.text

    with panel_der:
        st.subheader("📄 Editor de Informe Generado")
        
        # Botones de acción rápida
        btn_col1, btn_col2, btn_col3 = st.columns(3)
        with btn_col1: st.button("📋 Copiar")
        with btn_col2: st.button("💾 Guardar")
        with btn_col3: st.button("🖨️ Exportar")
        
        # Área de edición rica (Editable por el médico)
        reporte_editable = st.text_area(
            "Visualización del Reporte (Editable):",
            value=st.session_state.reporte_final,
            height=500
        )
        
        st.caption("Atajos: Ctrl+S (Guardar) | Ctrl+C (Copiar)")

else:
    st.warning("⚠️ Ingresa tu API Key en el panel izquierdo para activar la estación de trabajo.")