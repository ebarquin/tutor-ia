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
    /* BOTONES (fuera y dentro de formularios) */
    .stButton>button, form .stButton>button {
        background-color: #1cd4d4 !important;
        color: #fff !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.6em 1.5em !important;
    }
    .stButton>button:hover, form .stButton>button:hover {
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
    /* Forzar color oscuro en errores de excepción de Streamlit */
    .stException, .stException *, .stException pre, .stException code, .stException span, .stException div {
        color: #444444 !important;          /* Gris oscuro suave */
        background-color: #ffd9d9 !important;
        font-weight: bold !important;
        text-shadow: none !important;
        opacity: 1 !important;
    }
     /* Estilos para los botones en formularios (form_submit_button) */
    .stForm .stButton>button {
        background-color: #1cd4d4 !important;
        color: #fff !important;
        font-weight: bold !important;
        border-radius: 8px !important;
        border: none !important;
        padding: 0.6em 1.5em !important;
        margin: 0 8px 0 0 !important;
    }
    .stForm .stButton>button:hover {
        background-color: #24b7b7 !important;
        color: #fff !important;
    }
    </style>
""", unsafe_allow_html=True)

API_URL = os.environ.get("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Tutor-IA", layout="centered")



# Logo
st.sidebar.image("tutor_ia_logo.png", width=120)
st.sidebar.title("Tutor-IA")

#
# --- NUEVO MENÚ LATERAL: TODAS LAS OPCIONES VISIBLES ---
# Añadimos "💬 Chat explicativo" justo antes de "Formación"
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
    ("💬 Chat explicativo", "chat-dots"),
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

    if st.button("Procesar documento"):
        if materia_subir and tema_subir and archivo:
            files = {"archivo": (archivo.name, archivo, "application/pdf")}
            data = {"materia": materia_subir, "tema": tema_subir}
            with st.spinner("Procesando documento..."):
                response = requests.post(
                    f"{API_URL}/procesar_apunte",
                    data=data,
                    files=files
                )
                if response.status_code == 200:
                    st.success(response.json()["mensaje"])
                    time.sleep(1.5)
                    st.cache_data.clear()
                    st.rerun()
                else:
                    try:
                        detail = response.json().get("detail", "Se produjo un error inesperado.")
                    except Exception:
                        detail = "Se produjo un error inesperado."
                    st.error(f"❌ {detail}")
        else:
            st.warning("Por favor, completa todos los campos y selecciona un archivo.")

elif selected.strip() == "Enriquecer apuntes":
    import traceback
    st.header("Enriquecer apuntes con IA")
    materia_enriq, tema_enriq = seleccionar_materia_y_tema(materias, cargar_temas, "materia_enriq", "tema_enriq")
    if st.button("Enriquecer apuntes"):
        try:
            if materia_enriq and tema_enriq:
                with st.spinner("Enriqueciendo tus apuntes... Este proceso puede tardar varios segundos. No cierres la ventana."):
                    response = requests.post(
                        f"{API_URL}/enriquecer_apuntes",
                        params={"materia": materia_enriq, "tema": tema_enriq}
                    )
                    if response.status_code == 404:
                        try:
                            detail = response.json().get("detail", "No se encontraron apuntes para enriquecer.")
                        except Exception:
                            detail = "No se encontraron apuntes para enriquecer."
                        st.warning(f"⚠️ {detail}")
                    if response.status_code == 200:
                        data = response.json()
                        if data.get("ya_analizado"):
                            st.info("📌 Este tema ya fue enriquecido anteriormente. No se ha realizado un nuevo análisis.")
                        else:
                            mensaje = data.get("mensaje", {})
                            st.balloons()
                            st.success("🎉 ¡Apuntes enriquecidos correctamente! 🎉")
                            # Control robusto de tipos para mensaje
                            if isinstance(mensaje, dict):
                                chunks_creados = mensaje.get("chunks_creados", "?")
                                subtemas = mensaje.get("subtemas_agregados", [])
                                detalle = mensaje.get("detalle", [])
                            else:
                                chunks_creados = "?"
                                subtemas = []
                                detalle = []
                            st.info(f"Número de nuevos chunks añadidos: **{chunks_creados}**. ¡Sigue así, tu aprendizaje mejora cada día!")
                            if subtemas:
                                st.markdown("**Subtemas añadidos:**")
                                for sub in subtemas:
                                    st.markdown(f"- ✅ {sub}")
                            if detalle:
                                st.markdown("---\n**Detalles de los nuevos chunks:**")
                                for chunk in detalle:
                                    with st.expander(chunk.get("titulo", "Chunk sin título")):
                                        st.write(chunk.get("resumen", ""))
                    elif response.status_code != 404:
                        try:
                            detail = response.json().get("detail", "Se produjo un error inesperado.")
                        except Exception:
                            detail = "Se produjo un error inesperado."
                        st.error(f"❌ Error {response.status_code}: {detail}")
            else:
                st.warning("Selecciona materia y tema.")
        except Exception:
            st.error("❌ Ha ocurrido un error inesperado durante el enriquecimiento:")
            st.code(traceback.format_exc())

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

elif selected.strip() == "💬 Chat explicativo":
    # --- Título y descripción primero ---
    st.title("Chat explicativo Tutor-IA")
    st.markdown("Interactúa con el Tutor-IA para recibir explicaciones personalizadas sobre cualquier tema.")
    st.divider()

    # --- Selectores de materia y tema justo después del título ---
    materia_chat, tema_chat = seleccionar_materia_y_tema(
        materias,
        cargar_temas,
        "chat_materia",
        "chat_tema",
        label_materia="Materia",
        label_tema="Tema"
    )
    st.markdown(
        "<span style='font-size:0.92em; color:#20567a'>El historial de chat se borra automáticamente al cambiar de materia o tema.</span>",
        unsafe_allow_html=True
    )

    # --- Detectar cambio de materia/tema y resetear historial si corresponde ---
    chat_materia_last = st.session_state.get("chat_materia_last")
    chat_tema_last = st.session_state.get("chat_tema_last")
    if (materia_chat != chat_materia_last) or (tema_chat != chat_tema_last):
        st.session_state["chat_history"] = []
        st.session_state["chat_input_key"] = 0
    st.session_state["chat_materia_last"] = materia_chat
    st.session_state["chat_tema_last"] = tema_chat

    # --- Mostrar historial de mensajes (debajo de selectores) ---
    chat_history = st.session_state["chat_history"]
    if chat_history:
        for entry in chat_history:
            if entry["role"] == "user":
                st.markdown(
                    f"""
                    <div style="
                        background:#d2eafb;
                        border-radius: 12px 12px 0px 12px;
                        padding:10px 14px;
                        margin-bottom:4px;
                        max-width: 65%;
                        text-align: left;
                        margin-left: auto;
                        box-shadow: 1px 1px 8px #1cd4d414;
                        border-right: 3px solid #1cd4d4;
                    ">
                        <b>Tú:</b> {entry["content"]}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div style="
                        background:#e3f0fa;
                        border-radius: 12px 12px 12px 0px;
                        padding:10px 14px;
                        margin-bottom:8px;
                        max-width: 65%;
                        text-align: left;
                        margin-right: auto;
                        box-shadow: 1px 1px 8px #1cd4d414;
                    ">
                        <b>Tutor:</b> {entry["content"]}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
    else:
        st.info("El chat está vacío. ¡Haz tu primera pregunta!")

    # --- Campo de texto para nueva pregunta (debajo del historial) ---
    user_input_key = f"chat_input_{st.session_state['chat_input_key']}"
    user_input = st.text_input("Escribe tu pregunta", key=user_input_key)

    # --- SUGERENCIAS debajo del campo de texto, en horizontal, visual tipo globo pill ---
    if materia_chat and tema_chat:
        sugerencias = [
            "Explícame este tema como si tuviera 12 años.",
            "Dame un ejemplo sencillo sobre este tema.",
            "Cuéntame una historia sobre esto."
        ]
        # Espacio arriba
        st.markdown("<div style='height: 10px'></div>", unsafe_allow_html=True)
        # Nuevo CSS para globo pill con punta
        st.markdown("""
        <style>
        .sug-pills-container {
            display: flex;
            gap: 16px;
            margin: 16px 0 24px 0;
            justify-content: center;
        }
        .sug-pill-bubble {
            position: relative;
            background: #d2eafb;
            color: #14314f;
            padding: 8px 18px 8px 14px;
            border-radius: 32px 32px 32px 0px;
            font-size: 0.95em;
            font-weight: 600;
            box-shadow: 0 2px 12px #0002;
            cursor: pointer;
            border: none;
            outline: none;
            display: inline-block;
            transition: background 0.16s, box-shadow 0.16s;
            text-align: left;
            user-select: none;
        }
        .sug-pill-bubble:hover {
            background: #b8d6e8;
            box-shadow: 0 4px 18px #1cd4d444;
        }
        .sug-pill-bubble::after {
            content: "";
            position: absolute;
            left: 20px;
            bottom: -16px;
            width: 0;
            height: 0;
            border-top: 16px solid #d2eafb;
            border-left: 14px solid transparent;
        }
        .sug-pill-bubble:active {
            background: #98c8e6;
        }
        </style>
        """, unsafe_allow_html=True)
        import urllib.parse
        query_params = st.query_params
        sug_clicked = query_params.get("sug_pill", [None])[0]
        # Render pills como enlaces con globo pill
        pills_html = "<div class='sug-pills-container'>"
        for i, sugerencia in enumerate(sugerencias):
            encoded = urllib.parse.quote(sugerencia)
            pills_html += (
                f"<a href='?sug_pill={encoded}' class='sug-pill-bubble' "
                f"onclick=\"window.location.search='?sug_pill={encoded}';return false;\">{sugerencia}</a>"
            )
        pills_html += "</div>"
        st.markdown(pills_html, unsafe_allow_html=True)
        # Si pill clicada, copiar al input y limpiar el query param
        if sug_clicked:
            st.session_state[user_input_key] = sug_clicked
            # Limpiar query param (redirigir sin él)
            js = """
            <script>
            if (window.location.search.includes('sug_pill=')) {
                const url = new URL(window.location);
                url.searchParams.delete('sug_pill');
                window.history.replaceState(null, '', url);
            }
            </script>
            """
            st.markdown(js, unsafe_allow_html=True)
            # Forzar rerun para actualizar input
            st.rerun()
        # Espacio abajo
        st.markdown("<div style='height: 5px'></div>", unsafe_allow_html=True)

    # --- Botones "Enviar" y "Limpiar chat" juntos, debajo del input y sugerencias ---
    col1, col2 = st.columns([1, 1])
    enviar = col1.button("Enviar")
    limpiar = col2.button("Limpiar chat")

    # --- Acciones de los botones ---
    if limpiar:
        st.session_state["chat_history"] = []
        st.session_state["chat_input_key"] = 0
        st.rerun()

    if enviar and user_input.strip():
        # Añadir mensaje del usuario al historial
        st.session_state["chat_history"].append({"role": "user", "content": user_input.strip()})

        # --- Llamada real al endpoint de la API ---
        payload = {
            "materia": materia_chat,
            "tema": tema_chat,
            "nivel": "12_años",  # puedes adaptar esto con un selector si quieres más adelante
            "historial": st.session_state["chat_history"]
        }
        with st.spinner("Obteniendo respuesta del tutor..."):
            try:
                response = requests.post(f"{API_URL}/chat_explica_simple", json=payload, timeout=60)
                if response.status_code == 200:
                    data = response.json()
                    st.session_state["chat_history"] = data.get("historial", st.session_state["chat_history"])
                    st.session_state["chat_input_key"] += 1
                    st.rerun()
                else:
                    detail = response.json().get("detail", "Error desconocido al contactar con el backend.")
                    st.error(f"❌ {detail}")
            except Exception as e:
                st.error(f"❌ Error de conexión con la API: {e}")

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
                            st.rerun()
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
                        st.rerun()
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
                st.rerun()
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