# Tutor-IA 📘

Asistente educativo basado en inteligencia artificial. Permite a estudiantes y docentes interactuar con apuntes en PDF mediante preguntas, explicaciones accesibles, clases magistrales generadas por IA y evaluaciones automáticas.

---

## 🚀 Instalación y ejecución

```bash
git clone https://github.com/usuario/tutor-ia.git
cd tutor-ia
pip install -r requirements.txt

# Ejecutar API
uvicorn main:app --reload

# Ejecutar interfaz de usuario
streamlit run streamlit_app.py
```

---

## 🧭 Flujo principal del usuario

1. Subes apuntes en PDF.
2. El sistema los analiza, trocea y los almacena clasificados por **materia** y **tema**.
3. Puedes:
   - ❓ Hacer preguntas sobre tus apuntes.
   - 👩‍🎓 Obtener explicaciones como si tuvieras 12 años.
   - 📚 Generar clases magistrales completas.
   - 🎓 Evaluar tus propios desarrollos.
   - ✨ Enriquecer los apuntes con subtemas automáticos.

---

## 📡 Endpoints de la API

La API está documentada en `/docs` mediante Swagger (FastAPI).

| Método | Endpoint                    | Descripción                                                                 |
|--------|-----------------------------|-----------------------------------------------------------------------------|
| GET    | `/materias`                | Devuelve listado de materias                                               |
| GET    | `/temas`                   | Devuelve listado de temas por materia (`?materia=Nombre`)                 |
| GET    | `/responder_pregunta`     | Responde una pregunta basada en apuntes                                   |
| GET    | `/explicar_como_nino`     | Explica un tema con lenguaje accesible para niños                          |
| GET    | `/debug/vectorstores`     | Lista todas las carpetas vectorstore existentes (depuración)              |
| POST   | `/procesar_apunte`        | Procesa un PDF subido y lo añade al vectorstore                           |
| POST   | `/evaluar_desarrollo`     | Evalúa un texto redactado por el alumno                                  |
| POST   | `/enriquecer_apuntes`     | Añade subtemas enriquecidos a un tema                                     |
| POST   | `/generar_clase_magistral`| Genera una clase magistral para un tema                                    |
| POST   | `/borrar_apuntes_todos`   | Borra todos los apuntes, chunks y vectorstores                             |

---

## ⚙️ Variables de entorno

Crea un archivo `.env` en la raíz del proyecto a partir de la plantilla `.env.example`.

| Variable             | Obligatoria | Descripción                           | Por defecto         |
|----------------------|-------------|---------------------------------------|---------------------|
| `GROQ_API_KEY`       | Sí          | Clave API de Groq                     | -                   |
| `OPENAI_API_KEY`     | Sí          | Clave API de OpenAI                   | -                   |
| `BASE_VECTORSTORE_PATH` | No      | Ruta base para almacenamiento vectorial | `./data/vectorstores` |
| `DEFAULT_MODEL`      | No          | Modelo usado por defecto              | `gpt-3.5-turbo`     |
| `DEBUG`              | No          | Activa modo depuración                | `false`             |

---

## 📚 Estructura del proyecto (resumen)

```
src/
├── api/               # Rutas de FastAPI
├── apuntes/           # Scripts para manipular apuntes y chunks
├── rag/               # Vectorstores y chunks JSON
├── services/          # Lógica central de negocio
├── config.py          # Variables de entorno centralizadas
```

---

## ✅ Estado del proyecto

- [x] Subida y procesamiento de apuntes
- [x] Interfaz de usuario con Streamlit
- [x] Generación de clase magistral
- [x] Evaluación de desarrollos
- [x] Documentación de API
- [ ] Generación de audio (pendiente)

---

Este README es un primer enfoque. Aún faltan detalles importantes como:
- Arquitectura completa del sistema
- Esquemas de flujo de datos
- Tests y cobertura
- Guías para contribuciones o despliegue

Pero sirve como base para seguir iterando 🚀
