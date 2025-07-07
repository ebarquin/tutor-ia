from streamlit_option_menu import option_menu
import streamlit as st
import requests
import time
import json
import os

st.cache_data.clear()

def seleccionar_materia_y_tema(materias, cargar_temas_func, key_materia, key_tema, label_materia="Materia", label_tema="Tema"):
    """
    Selector reutilizable de materia y tema para Streamlit.
    Devuelve (materia, tema)
    """
    materia = st.selectbox(label_materia, materias, key=key_materia)
    temas = cargar_temas_func(materia) if materia else []
    tema = st.selectbox(label_tema, temas, key=key_tema)
    return materia, tema

# --- Personalización visual global y del sidebar ---
st.markdown("""
    <style>
    /* FONDO GENERAL */
    body, .stApp {
        background-color: #f6f8fc !important;
        color: #14314f !important;
    }
    /* SIDEBAR fondo */
    [data-testid="stSidebar"] {
        background-color: #fff !important;
    }
    /* TITULOS Y TEXTOS PRINCIPALES */
    .stMarkdown h1, .stMarkdown h2, .stMarkdown h3, .stMarkdown h4,
    .stMarkdown h5, .stMarkdown h6,
    .stText, .stApp, .stMarkdown, .css-10trblm, .css-1v3fvcr {
        color: #14314f !important;
    }
    /* LABELS DE INPUTS */
    label, .stTextInput label, .stSelectbox label {
        color: #20567a !important;
        font-weight: 600 !important;
    }
    /* INPUTS Y SELECTBOXES MÁS CLAROS */
    .stTextInput>div>div>input, .stSelectbox>div>div>div>input, .stSelectbox>div>div {
        background-color: #d2eafb !important;
        color: #14314f !important;
        border-radius: 8px !important;
        border: 1.5px solid #1cd4d4 !important;
        font-weight: 600 !important;
    }
    /* Desplegables */
    .stSelectbox>div>div {
        min-height: 48px !important;
        border-radius: 8px !important;
        background-color: #d2eafb !important;
        color: #14314f !important;
        border: 1.5px solid #1cd4d4 !important;
        font-weight: 600 !important;
    }
    /* CURSOR DEL INPUT */
    input, textarea {
        caret-color: #14314f !important;
    }
    input::placeholder, textarea::placeholder {
        color: #b8d6e8 !important;
        opacity: 1 !important;
    }
    /* BOTONES */
    .stButton>button {
        background-color: #1cd4d4 !important;
        color: #fff !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.6em 1.5em !important;
    }
    .stButton>button:hover {
        background-color: #24b7b7 !important;
        color: #fff !important;
    }
    .stAlert, .stInfo {
        background-color: #d2f2fb !important;
        color: #14314f !important;
        font-weight: 700 !important;
        border-left: 5px solid #1cd4d4 !important;
    }
    .stAlert p, .stInfo p, .stAlert span, .stInfo span {
        color: #14314f !important;
    }
    .stWarning {
        background-color: #fff3cd !important;
        color: #664d03 !important;
        border-left: 5px solid #ffe066 !important;
    }
    .stSuccess {
        background-color: #d2fbe3 !important;
        color: #205732 !important;
        border-left: 5px solid #1cd485 !important;
    }
    .stError {
        background-color: #ffd9d9 !important;
        color: #ab1e1e !important;
        border-left: 5px solid #e76f51 !important;
    }
    /* CUADRO DE FILE UPLOADER: fondo azul claro, sin bordes internos, ni dobles líneas */
    .stFileUploader, .stFileUploader * {
        background: #d2eafb !important;
        color: #14314f !important;
        border-radius: 8px !important;
        border: none !important;
        box-shadow: none !important;
    }
    .stFileUploader [data-testid="stFileDropzone"],
    .stFileUploader div[data-testid="stFileDropzone"] {
        background: #d2eafb !important;
        color: #20567a !important;
        border-radius: 8px !important;
        border: none !important;
        font-weight: 600 !important;
        box-shadow: none !important;
        outline: none !important;
    }
    /* Quitar cualquier borde interno de los elementos hijos */
    .stFileUploader * {
        border: none !important;
        box-shadow: none !important;
        outline: none !important;
    }
    /* Textos, iconos y botón */
    .stFileUploader span, 
    .stFileUploader p, 
    .stFileUploader label, 
    .stFileUploader div, 
    .stFileUploader button, 
    .stFileUploader svg {
        color: #20567a !important;
        font-weight: 600 !important;
        background: transparent !important;
        fill: #1cd4d4 !important;
        border: none !important;
        box-shadow: none !important;
    }
    .stFileUploader button {
        background-color: #1cd4d4 !important;
        color: #fff !important;
        border-radius: 6px !important;
        border: none !important;
        font-weight: bold !important;
    }
    .stFileUploader button:hover {
        background-color: #24b7b7 !important;
        color: #fff !important;
    }
    .stFileUploader svg {
        color: #1cd4d4 !important;
        fill: #1cd4d4 !important;
    }
    /* CAJA DE INFO DEL FOOTER SIDEBAR */
    .stSidebar .stMarkdown div {
        background-color: #e3f0fa !important;
        color: #20567a !important;
    }
    textarea, .stTextArea>div>textarea {
        background-color: #d2eafb !important;
        color: #14314f !important;
        border-radius: 8px !important;
        border: 1.5px solid #1cd4d4 !important;
        font-weight: 600 !important;
    }
    </style>
""", unsafe_allow_html=True)

API_URL = os.environ.get("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Tutor-IA", layout="centered")



# Logo
st.sidebar.image("tutor_ia_logo.png", width=120)
st.sidebar.title("Tutor-IA")

# --- NUEVO MENÚ LATERAL: TODAS LAS OPCIONES VISIBLES ---
menu_options = [
    ("Portada", "house"),
    ("Gestión de apuntes", "folder"),
    ("    Subir apuntes", ""),
    ("    Enriquecer apuntes", ""),
    ("Evaluación", "check2-circle"),
    ("    Evaluar desarrollo", ""),
    ("Consultar", "search"),
    ("    Responder pregunta", ""),
    ("    Explicar como un niño", ""),
    ("Formación", "book"),
    ("    Clase magistral", ""),
    ("Administración", "gear"),
    ("    Borrar apuntes (admin)", ""),
]
labels, icons = zip(*menu_options)

with st.sidebar:
    selected = option_menu(
        menu_title=None,
        options=labels,
        icons=icons,
        menu_icon="cast",
        default_index=0,
        orientation="vertical",
        styles={
            "container": {"background-color": "#fff", "padding": "12px"},
            "icon": {"color": "#E76F51", "font-size": "18px"},
            "nav-link": {
                "font-size": "17px",
                "text-align": "left",
                "margin":"0px",
                "color": "#1a3247",
                "font-weight": "normal"
            },
            "nav-link-selected": {
                "background-color": "#e3e3e3",
                "color": "#222",
                "font-weight": "bold"
            },
        }
    )

# --- Control para que los títulos no tengan acción ---
# Las subopciones empiezan con dos espacios
subopciones_validas = [opt for opt in labels if opt.startswith("  ")]
# Opciones principales (títulos de sección, sin espacios al principio, excepto Portada)
secciones = {"Gestión de apuntes", "Evaluación", "Consultar", "Formación", "Administración"}

# Guardamos la última subopción elegida
if "last_valid_option" not in st.session_state:
    st.session_state["last_valid_option"] = "Portada"

if selected in secciones:
    # Si el usuario pulsa una sección, restauramos la última subopción o Portada
    selected = st.session_state["last_valid_option"]
elif selected in subopciones_validas or selected == "Portada":
    st.session_state["last_valid_option"] = selected

# --- FUNCIONES DE CARGA ---
@st.cache_data
def cargar_materias():
    try:
        response = requests.get(f"{API_URL}/materias")
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error al cargar materias: {e}")
        return []

@st.cache_data
def cargar_temas(materia):
    try:
        response = requests.get(f"{API_URL}/temas", params={"materia": materia})
        response.raise_for_status()
        return response.json()
    except Exception as e:
        st.error(f"Error al cargar temas: {e}")
        return []

materias = cargar_materias()

if selected == "Portada":
    st.title("🎓 Tutor Inteligente de Apuntes")
    st.markdown("""
    ¡Bienvenido a **Tutor-IA**!  
    Plataforma para crear, enriquecer y consultar tus apuntes con inteligencia artificial.  
    Selecciona una sección en el menú lateral para comenzar.
    """)
    st.info("¿Tienes dudas, feedback o sugerencias? Contacta con el equipo Tutor-IA.")

elif selected.strip() == "Subir apuntes":
    st.header("Subir y procesar nuevo apunte")
    materia_subir = st.text_input("Materia", key="materia_subir")
    tema_subir = st.text_input("Tema", key="tema_subir")
    archivo = st.file_uploader("Selecciona un archivo PDF", type=["pdf"])

    if st.button("Procesar apunte"):
        if materia_subir and tema_subir and archivo:
            files = {"archivo": (archivo.name, archivo, "application/pdf")}
            data = {"materia": materia_subir, "tema": tema_subir}
            with st.spinner("Procesando apunte..."):
                response = requests.post(
                    f"{API_URL}/procesar_apunte",
                    data=data,
                    files=files
                )
                if response.status_code == 200:
                    st.success(response.json()["mensaje"])
                    time.sleep(1.5)
                    st.cache_data.clear()
                    st.experimental_rerun()
                else:
                    try:
                        detail = response.json().get("detail", "Se produjo un error inesperado.")
                    except Exception:
                        detail = "Se produjo un error inesperado."
                    st.error(f"❌ {detail}")
        else:
            st.warning("Por favor, completa todos los campos y selecciona un archivo.")

elif selected.strip() == "Enriquecer apuntes":
    st.header("Enriquecer apuntes con IA")
    materia_enriq, tema_enriq = seleccionar_materia_y_tema(materias, cargar_temas, "materia_enriq", "tema_enriq")
    if st.button("Enriquecer apuntes"):
        if materia_enriq and tema_enriq:
            with st.spinner("Enriqueciendo tus apuntes... Este proceso puede tardar varios segundos. No cierres la ventana."):
                response = requests.post(
                    f"{API_URL}/enriquecer_apuntes",
                    params={"materia": materia_enriq, "tema": tema_enriq}
                )
                if response.status_code == 200:
                    data = response.json().get("mensaje", {})
                    st.balloons()
                    st.success("🎉 ¡Apuntes enriquecidos correctamente! 🎉")
                    chunks_creados = data.get("chunks_creados", "?")
                    st.info(f"Número de nuevos chunks añadidos: **{chunks_creados}**. ¡Sigue así, tu aprendizaje mejora cada día!")
                    subtemas = data.get("subtemas_agregados", [])
                    detalle = data.get("detalle", [])
                    
                    if subtemas:
                        st.markdown("**Subtemas añadidos:**")
                        for sub in subtemas:
                            st.markdown(f"- ✅ {sub}")

                    if detalle:
                        st.markdown("---\n**Detalles de los nuevos chunks:**")
                        for chunk in detalle:
                            with st.expander(chunk["titulo"]):
                                st.write(chunk["resumen"])
                else:
                    try:
                        detail = response.json().get("detail", "Se produjo un error inesperado.")
                    except Exception:
                        detail = "Se produjo un error inesperado."
                    st.error(f"❌ {detail}")
        else:
            st.warning("Selecciona materia y tema.")

elif selected.strip() == "Evaluar desarrollo":
    for key in ["materia_pregunta", "tema_pregunta", "materia_nino", "tema_nino", "materia_cm", "tema_cm", "materia_eval", "tema_eval", "titulo_eval"]:
        st.session_state.pop(key, None)
    st.header("Evaluar un desarrollo completo de tema")
    materia_eval, tema_eval = seleccionar_materia_y_tema(materias, cargar_temas, "materia_eval", "tema_eval")
    titulo_eval = st.text_input("Título del desarrollo", key="titulo_eval")
    desarrollo = st.text_area("Desarrollo del tema", height=300)

    if st.button("Enviar desarrollo para evaluación"):
        if materia_eval and tema_eval and titulo_eval and desarrollo:
            with st.spinner("Evaluando tu desarrollo..."):
                payload = {
                    "materia": materia_eval,
                    "tema": tema_eval,
                    "titulo_tema": titulo_eval,
                    "desarrollo": desarrollo
                }
                response = requests.post(f"{API_URL}/evaluar_desarrollo", json=payload)
                if response.status_code == 200:
                    st.markdown("### 📝 Evaluación")
                    st.success(response.json()["evaluacion"])
                else:
                    try:
                        detail = response.json().get("detail", "Se produjo un error inesperado.")
                    except Exception:
                        detail = "Se produjo un error inesperado."
                    st.error(f"❌ {detail}")
        else:
            st.warning("Por favor, completa todos los campos antes de enviar.")

elif selected.strip() == "Responder pregunta":
    for key in ["materia_pregunta", "tema_pregunta", "materia_nino", "tema_nino", "materia_cm", "tema_cm", "materia_eval", "tema_eval", "titulo_eval"]:
        st.session_state.pop(key, None)
    st.header("Haz una pregunta sobre tus apuntes")
    materia, tema = seleccionar_materia_y_tema(materias, cargar_temas, "materia_pregunta", "tema_pregunta")
    pregunta = st.text_area("Pregunta")

    if st.button("Enviar pregunta"):
        if materia and tema and pregunta:
            with st.spinner("Obteniendo respuesta..."):
                response = requests.get(
                    f"{API_URL}/responder_pregunta",
                    params={"materia": materia, "tema": tema, "pregunta": pregunta}
                )
                if response.status_code == 200:
                    st.success(response.json()["respuesta"])
                else:
                    try:
                        detail = response.json().get("detail", "Se produjo un error inesperado.")
                    except Exception:
                        detail = "Se produjo un error inesperado."
                    st.error(f"❌ {detail}")
        else:
            st.warning("Por favor, completa todos los campos.")

elif selected.strip() == "Explicar como un niño":
    for key in ["materia_pregunta", "tema_pregunta", "materia_nino", "tema_nino", "materia_cm", "tema_cm", "materia_eval", "tema_eval", "titulo_eval"]:
        st.session_state.pop(key, None)
    st.header("Explica un tema como si tuvieras 12 años")
    materia_nino, tema_nino = seleccionar_materia_y_tema(materias, cargar_temas, "materia_nino", "tema_nino")

    if st.button("Explicar"):
        if materia_nino and tema_nino:
            with st.spinner("Generando explicación..."):
                response = requests.get(
                    f"{API_URL}/explicar_como_nino",
                    params={"materia": materia_nino, "tema": tema_nino}
                )
                if response.status_code == 200:
                    st.success(response.json()["explicacion"])
                else:
                    try:
                        detail = response.json().get("detail", "Se produjo un error inesperado.")
                    except Exception:
                        detail = "Se produjo un error inesperado."
                    st.error(f"❌ {detail}")
        else:
            st.warning("Por favor, completa ambos campos.")

elif selected.strip() == "Clase magistral":
    for key in ["materia_pregunta", "tema_pregunta", "materia_nino", "tema_nino", "materia_cm", "tema_cm", "materia_eval", "tema_eval", "titulo_eval"]:
        st.session_state.pop(key, None)
    st.header("📚 Clase magistral generada por IA")
    materia_cm, tema_cm = seleccionar_materia_y_tema(materias, cargar_temas, "materia_cm", "tema_cm")

    if materia_cm and tema_cm:
        try:
            tema_slug = tema_cm.lower().replace(" ", "_")
            ruta_json = f"src/apuntes/rag/chunks/{materia_cm}__{tema_slug}.json"
            st.write(f"📁 Buscando archivo en: `{ruta_json}`")

            with open(ruta_json, "r", encoding="utf-8") as f:
                chunks = json.load(f)

            clase = next(
                (c for c in chunks if c.get("metadata", {}).get("tipo", "").replace(" ", "_").lower() == "clase_magistral_completa"),
                None
            )

            if clase:
                st.success("✅ Clase magistral encontrada")
                st.markdown(clase["page_content"])
            else:
                st.info("ℹ️ Aún no existe una clase magistral generada para este tema. Pulsa el botón para crearla con IA.")
                generar = st.button("🚀 Generar clase magistral ahora", key="generar_clase_magistral_btn")
                if generar:
                    with st.spinner("Generando clase magistral..."):
                        response = requests.post(
                            f"{API_URL}/generar_clase_magistral",
                            params={"materia": materia_cm, "tema": tema_cm}
                        )
                        if response.status_code == 200:
                            st.success("✅ Clase magistral generada. Recarga para visualizarla.")
                            st.cache_data.clear()
                            st.experimental_rerun()
                        else:
                            try:
                                detail = response.json().get("detail", "Se produjo un error inesperado.")
                            except Exception:
                                detail = "Se produjo un error inesperado."
                            st.error(f"❌ {detail}")
        except FileNotFoundError:
            st.info("ℹ️ No existe ningún apunte para este tema. Por favor, sube apuntes antes de generar la clase magistral.")
            generar = st.button("🚀 Generar clase magistral ahora", key="generar_clase_magistral_btn_2")
            if generar:
                with st.spinner("Generando clase magistral..."):
                    response = requests.post(
                        f"{API_URL}/generar_clase_magistral",
                        params={"materia": materia_cm, "tema": tema_cm}
                    )
                    if response.status_code == 200:
                        st.success("✅ Clase magistral generada. Recarga para visualizarla.")
                        st.cache_data.clear()
                        st.experimental_rerun()
                    else:
                        try:
                            detail = response.json().get("detail", "Se produjo un error inesperado.")
                        except Exception:
                            detail = "Se produjo un error inesperado."
                        st.error(f"❌ {detail}")
        except Exception as e:
            st.error(f"Error leyendo el JSON: {e}")

elif selected.strip() == "Borrar apuntes (admin)":
    st.header("🧹 Borrar todos los apuntes del sistema")
    if st.button("🧹 Borrar todos los apuntes", key="borrar_todos_apuntes_btn"):
        with st.spinner("Borrando todos los apuntes..."):
            response = requests.post(f"{API_URL}/borrar_apuntes_todos")
            if response.status_code == 200:
                st.success("✅ Todos los apuntes borrados correctamente.")
                st.cache_data.clear()
                st.experimental_rerun()
            else:
                try:
                    detail = response.json().get("detail", "Se produjo un error inesperado.")
                except Exception:
                    detail = "Se produjo un error inesperado."
                st.error(f"❌ {detail}")

# --- FOOTER ---
st.sidebar.markdown("""
    <div style='background-color: #e3f0fa; padding: 16px; border-radius: 8px; color: #1a3247; font-weight: 500;'>
        Plataforma Tutor-IA · v1.0<br>
        Un proyecto de aprendizaje con IA 🤖
    </div>
""", unsafe_allow_html=True)