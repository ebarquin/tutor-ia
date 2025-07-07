from streamlit_option_menu import option_menu
import streamlit as st
import requests
import time
import json
import os
st.cache_data.clear()

API_URL = os.environ.get("API_URL", "http://localhost:8000")

st.set_page_config(page_title="Tutor-IA", layout="centered")

# Personalización del sidebar
st.markdown("""
    <style>
    [data-testid="stSidebar"] {
        background-color: #ffffff;
    }
    </style>
""", unsafe_allow_html=True)

# Logo
st.sidebar.image("tutor_ia_logo.png", width=120)
st.sidebar.title("Tutor-IA")

# --- NUEVO MENÚ LATERAL: TODAS LAS OPCIONES VISIBLES ---
menu_options = [
    ("Portada", "house"),
    ("Gestión de apuntes", "folder"),
    ("  Subir apuntes", ""),    # Subopciones con dos espacios al principio
    ("  Enriquecer apuntes", ""),
    ("Evaluación", "check2-circle"),
    ("  Evaluar desarrollo", ""),
    ("Consultar", "search"),
    ("  Responder pregunta", ""),
    ("  Explicar como un niño", ""),
    ("Formación", "book"),
    ("  Clase magistral", ""),
    ("Administración", "gear"),
    ("  Borrar apuntes (admin)", ""),
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
                    st.error("Error: " + response.text)
        else:
            st.warning("Por favor, completa todos los campos y selecciona un archivo.")

elif selected.strip() == "Enriquecer apuntes":
    st.header("Enriquecer apuntes con IA")
    materia_enriq = st.selectbox("Materia", materias, key="materia_enriq")
    temas_enriq = cargar_temas(materia_enriq) if materia_enriq else []
    tema_enriq = st.selectbox("Tema", temas_enriq, key="tema_enriq")
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
                    st.error("Error: " + response.text)
        else:
            st.warning("Selecciona materia y tema.")

elif selected.strip() == "Evaluar desarrollo":
    st.header("Evaluar un desarrollo completo de tema")
    materia_eval = st.selectbox("Materia", materias, key="materia_eval")
    temas_eval = cargar_temas(materia_eval) if materia_eval else []
    tema_eval = st.selectbox("Tema", temas_eval, key="tema_eval")
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
                    st.error("Error: " + response.text)
        else:
            st.warning("Por favor, completa todos los campos antes de enviar.")

elif selected.strip() == "Responder pregunta":
    st.header("Haz una pregunta sobre tus apuntes")
    materia = st.selectbox("Materia", materias, key="materia_pregunta")
    temas = cargar_temas(materia) if materia else []
    tema = st.selectbox("Tema", temas, key="tema_pregunta")
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
                    st.error("Error: " + response.text)
        else:
            st.warning("Por favor, completa todos los campos.")

elif selected.strip() == "Explicar como un niño":
    st.header("Explica un tema como si tuvieras 12 años")
    materia_nino = st.selectbox("Materia", materias, key="materia_nino")
    temas_nino = cargar_temas(materia_nino) if materia_nino else []
    tema_nino = st.selectbox("Tema", temas_nino, key="tema_nino")

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
                    st.error("Error: " + response.text)
        else:
            st.warning("Por favor, completa ambos campos.")

elif selected.strip() == "Clase magistral":
    st.header("📚 Clase magistral generada por IA")
    materia_cm = st.selectbox("Materia", materias, key="materia_cm")
    temas_cm = cargar_temas(materia_cm) if materia_cm else []
    tema_cm = st.selectbox("Tema", temas_cm, key="tema_cm")

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
                            st.error("❌ Error al generar la clase magistral: " + response.text)
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
                        st.error("❌ Error al generar la clase magistral: " + response.text)
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
                st.error("❌ Error al borrar los apuntes: " + response.text)

# --- FOOTER ---
st.sidebar.markdown("""
    <div style='background-color: #e3f0fa; padding: 16px; border-radius: 8px; color: #1a3247; font-weight: 500;'>
        Plataforma Tutor-IA · v1.0<br>
        Un proyecto de aprendizaje con IA 🤖
    </div>
""", unsafe_allow_html=True)