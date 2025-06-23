import streamlit as st
import requests

API_URL = "https://tutor-ia-api.onrender.com"

st.set_page_config(page_title="Tutor-IA", layout="centered")
st.title("🎓 Tutor Inteligente de Apuntes")

tab1, tab2, tab3 = st.tabs([
    "🤖 Responder pregunta", 
    "🧒 Explicar como niño", 
    "📄 Subir apunte"
])

# --- TAB 1: Responder pregunta ---
with tab1:
    st.header("Haz una pregunta sobre tus apuntes")
    materia = st.text_input("Materia", key="materia_pregunta")
    tema = st.text_input("Tema", key="tema_pregunta")
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
    materia_nino = st.text_input("Materia", key="materia_nino")
    tema_nino = st.text_input("Tema", key="tema_nino")

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
            with st.spinner("Procesando apunte..."):
                response = requests.post(
                    f"{API_URL}/procesar_apunte",
                    params={"materia": materia_subir, "tema": tema_subir},
                    files=files
                )
                if response.status_code == 200:
                    st.success(response.json()["mensaje"])
                else:
                    st.error("Error: " + response.text)
        else:
            st.warning("Por favor, completa todos los campos y selecciona un archivo.")