import streamlit as st
import requests

API_URL = "https://tutor-ia-api.onrender.com"

st.set_page_config(page_title="Tutor-IA", layout="centered")
st.title("🎓 Tutor Inteligente de Apuntes")

st.header("Haz una pregunta sobre tus apuntes")
materia = st.text_input("Materia")
tema = st.text_input("Tema")
pregunta = st.text_area("Pregunta")

if st.button("Enviar pregunta"):
    with st.spinner("Obteniendo respuesta..."):
        response = requests.get(
            f"{API_URL}/responder_pregunta",
            params={"materia": materia, "tema": tema, "pregunta": pregunta}
        )
        if response.status_code == 200:
            st.success(response.json()["respuesta"])
        else:
            st.error("Error: " + response.text)