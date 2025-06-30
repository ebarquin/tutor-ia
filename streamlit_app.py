import streamlit as st
import requests
import time

API_URL = "https://tutor-ia-api.onrender.com"

st.set_page_config(page_title="Tutor-IA", layout="centered")
st.title("🎓 Tutor Inteligente de Apuntes")

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

# --- CARGAR MATERIAS UNA SOLA VEZ ---
materias = cargar_materias()

# --- TABS ---
tab1, tab2, tab3, tab4 = st.tabs([
    "🤖 Responder pregunta", 
    "🧒 Explicar como niño", 
    "📄 Subir apunte",
    "🧠 Evaluar desarrollo",
    "✨ Enriquecer apuntes"
])

# --- TAB 1: Responder pregunta ---
with tab1:
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

# --- TAB 2: Explicar como niño ---
with tab2:
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

# --- TAB 3: Subir apunte ---
with tab3:
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
                    # Espera 1.5 segundos para que el usuario vea el mensaje
                    time.sleep(1.5)
                    st.cache_data.clear()
                    st.rerun()
                else:
                    st.error("Error: " + response.text)
        else:
            st.warning("Por favor, completa todos los campos y selecciona un archivo.")

# --- TAB 4: Evaluar desarrollo ---
with tab4:
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

# --- TAB 5: Enriquecer apuntes ---
with tab5:
    st.header("Enriquecer apuntes con IA")
    materia_enriq = st.selectbox("Materia", materias, key="materia_enriq")
    temas_enriq = cargar_temas(materia_enriq) if materia_enriq else []
    tema_enriq = st.selectbox("Tema", temas_enriq, key="tema_enriq")
    if st.button("Enriquecer apuntes"):
        if materia_enriq and tema_enriq:
            with st.spinner("Enriqueciendo tus apuntes..."):
                response = requests.post(
                    f"{API_URL}/enriquecer_apuntes",
                    params={"materia": materia_enriq, "tema": tema_enriq}
                )
                if response.status_code == 200:
                    st.success(response.json().get("mensaje", "Apuntes enriquecidos correctamente."))
                else:
                    st.error("Error: " + response.text)
        else:
            st.warning("Selecciona materia y tema.")