# Tutor-IA

## Índice

1. [Introducción](#introducción)
2. [Arquitectura y Tecnologías](#arquitectura-y-tecnologías-utilizadas)
3. [Instalación y Ejecución](#-instalación-y-ejecución)
4. [Funcionamiento del sistema RAG](#funcionamiento-del-sistema-rag)
5. [Casos de uso recomendados](#casos-de-uso-recomendados)
6. [Checklist de contribución o desarrollo futuro](#checklist-de-contribución-o-desarrollo-futuro)
7. [API](#api-de-gestión-de-apuntes-y-tutoría)


# Introducción

**Tutor-IA** es una plataforma educativa potenciada por inteligencia artificial diseñada para facilitar el estudio a través del procesamiento y explicación personalizada de apuntes. Su objetivo principal es ayudar a estudiantes a comprender mejor sus materiales académicos, respondiendo a preguntas, generando resúmenes y ofreciendo explicaciones adaptadas al nivel y contexto del alumno.

Esta herramienta combina modelos de lenguaje avanzados con técnicas de recuperación de información para garantizar respuestas precisas basadas en los apuntes propios del estudiante, fomentando un aprendizaje eficiente y personalizado.

# Arquitectura y Tecnologías Utilizadas

Tutor-IA está construido sobre una arquitectura moderna que combina servicios backend robustos con una interfaz de usuario intuitiva. A continuación, se describen las principales tecnologías y componentes que conforman el proyecto:

- **FastAPI:** Framework para la creación de APIs RESTful rápidas y eficientes en Python. Se utiliza para gestionar las peticiones del frontend y ejecutar la lógica de negocio, incluyendo la integración con modelos de lenguaje y procesamiento de documentos.

- **Streamlit:** Biblioteca para construir interfaces web interactivas y fáciles de usar, orientada a aplicaciones de datos y machine learning. En Tutor-IA, Streamlit ofrece la UI donde los usuarios pueden interactuar con el tutor y gestionar sus apuntes.

- **Modelos de lenguaje (LLM):** Se emplean modelos como GPT-3.5 o Groq para generar respuestas y explicaciones basadas en el contexto proporcionado por los apuntes del usuario, utilizando técnicas de Recuperación Aumentada por Generación (RAG).

- **RAG (Retrieval-Augmented Generation):** Técnica que combina búsqueda de información en documentos relevantes con generación de texto para proporcionar respuestas más precisas y contextualizadas. Tutor-IA utiliza RAG para buscar fragmentos relevantes de los apuntes y enriquecer las respuestas del modelo.

- **FAISS (Facebook AI Similarity Search):** Motor de búsqueda eficiente para grandes colecciones de vectores que permite realizar búsquedas rápidas de fragmentos de texto similares. En Tutor-IA, FAISS almacena y consulta las representaciones vectoriales de los chunks de apuntes para facilitar la recuperación de información contextual.

- **Almacenamiento y Procesamiento de Apuntes:** Los documentos subidos por el usuario se procesan y segmentan en chunks para su posterior indexación y búsqueda contextual mediante FAISS.

Esta combinación tecnológica asegura un sistema escalable, eficiente y con una experiencia de usuario centrada en la personalización y calidad educativa.


# API de Gestión de Apuntes y Tutoría

Esta API ofrece un conjunto de endpoints diseñados para gestionar apuntes académicos, responder preguntas basadas en contenido vectorizado (RAG), evaluar desarrollos, generar explicaciones adaptadas y enriquecer apuntes. Está construida sobre FastAPI y usa tecnologías como FAISS para búsqueda vectorial y el modelo Groq para generación de lenguaje natural.

## ⚙️ Instalación y Ejecución

### 📋 Requisitos del Sistema

- Python 3.10 o superior
- Git instalado
- Recomendado: entorno virtual (venv, poetry o conda)
- Conexión a internet para instalación de dependencias y uso de Groq API y OpenAi API

---

### 🧪 Instrucciones Paso a Paso

#### 1. 🔄 Clonar el repositorio

```bash
git clone https://github.com/tuusuario/tutor-ia.git
cd tutor-ia
```

#### 2. 🧰 Crear el entorno virtual
```bash
python3 -m venv .venv
source .venv/bin/activate   # En Linux/macOS
.venv\Scripts\activate      # En Windows
```

#### 3. 📦 Instalar dependencias
```bash
pip install -r requirements.txt
```

#### 4. 🚀 Lanzar la API
```bash
uvicorn src.api.main:app --reload
```
La API estará disponible en http://localhost:8000
Puedes acceder a la documentación interactiva Swagger en http://localhost:8000/docs

Recuerda definir tu archivo .env con las claves necesarias, como GROQ_API_KEY, antes de lanzar la API.

#### 5. 🖥️ Lanzar la interfaz en Streamlit

```bash
streamlit run interfaz/main.py
```

# Endpoints Principales

## 1. /responder_pregunta (GET) (Deprecado)

Descripción:
Responde a una pregunta específica basada en la materia y tema indicados, usando un enfoque Retrieval-Augmented Generation (RAG) para aprovechar el contexto de los apuntes.

Parámetros:
	•	materia (string, requerido): Nombre de la materia.
	•	tema (string, requerido): Nombre del tema dentro de la materia.
	•	pregunta (string, requerido): La pregunta que desea responder el usuario.

Respuesta:

```json
{ "respuesta": "Texto con la respuesta generada basada en los apuntes." }
```

## 2. /explicar_ como_nino (GET)

Descripción:
Genera una explicación de un tema específico, adaptada para que un niño de 12 años pueda entenderla.

Parámetros:
	•	materia (string, requerido): Nombre de la materia.
	•	tema (string, requerido): Nombre del tema dentro de la materia.

Respuesta:

```json
{
	"explicacion": "Texto explicativo simplificado para niños."
}
```

## 3. /procesar_apunte (POST)

Descripción:
Procesa un nuevo archivo de apunte subido por el usuario, analiza su contenido, lo divide en chunks y actualiza el vectorstore correspondiente.

Parámetros:
	•	materia (form data, requerido): Nombre de la materia.
	•	tema (form data, requerido): Nombre del tema.
	•	archivo (file, requerido): Archivo de apunte en formato compatible.

```json
{
  "mensaje": "Mensaje indicando el resultado del procesamiento."
}
```

## 4. /evaluar_desarrollo (POST)

Descripción:
Evalúa un desarrollo escrito por el alumno comparándolo con los apuntes disponibles para la materia y tema indicados.

Parámetros (JSON body):
	•	materia (string): Nombre de la materia.
	•	tema (string): Nombre del tema.
	•	titulo_tema (string): Título del desarrollo.
	•	desarrollo (string): Texto del desarrollo a evaluar.

Respuesta:

```json
{
  "evaluacion": "Resultado cuantitativo o cualitativo de la evaluación."
}
```
## 5. /materias (GET)

Descripción:
Devuelve un listado de todas las materias disponibles (directorio de vectorstores).

Respuesta

```json
[
  "historia",
  "matematicas",
  "biologia"
]
```

## 6. /temas (GET)

Descripción:
Devuelve un listado de los temas disponibles para una materia concreta.

Parámetros:
	•	materia (string, requerido): Nombre de la materia.

Respuesta:

```json
[
  "Segunda guerra mundial",
  "Edad media",
  "Renacimiento"
]
```

## 7. /debug/vectorstores (GET)

Descripción:
Endpoint de depuración para listar todos los vectorstores existentes en el sistema.

Respuesta:

```json
[
  "historia__segunda_guerra_mundial",
  "matematicas__algebra",
  "biologia__celulas"
]
```

## 8. /enriquecer_apuntes (POST)

Descripción:
Permite enriquecer apuntes existentes con información adicional generada automáticamente, actualizando la base de datos de chunks y temas.

Parámetros:
	•	materia (string, requerido): Nombre de la materia.
	•	tema (string, requerido): Nombre del tema.

```json	
{
  "mensaje": {
    "chunks_creados": 10,
    "subtemas_agregados": ["subtema1", "subtema2"],
    "detalle": []
  },
  "ya_analizado": false
}
```

## 9. /generar_ clase_magistral (POST)

Descripción:
Genera una clase magistral completa para una materia y tema dados, combinando subtemas y almacenando el resultado en los apuntes.

Parámetros:
	•	materia (string, requerido): Nombre de la materia.
	•	tema (string, requerido): Nombre del tema.

Respuesta:

```json
{
  "mensaje": "Clase magistral generada correctamente."
}
```

## 10. /chat_ explica_simple (POST)

Descripción:
API para el chatbot que responde preguntas basándose en el contexto de apuntes, con manejo avanzado de preguntas fuera de contexto y fallback para respuestas genéricas.

Parámetros (JSON body):
	•	materia (string): Materia de referencia.
	•	tema (string): Tema de referencia.
	•	historial (lista de mensajes): Historial de la conversación.

Respuesta:

```json
{
  "respuesta": "Respuesta del tutor académico.",
  "historial": [
    {"role": "usuario", "content": "¿Quién fue Hitler?"},
    {"role": "tutor", "content": "Respuesta detallada basada en apuntes e IA."}
  ]
}
```

# 🏗️ Arquitectura del Proyecto

La arquitectura de `Tutor-IA` está organizada en una estructura modular y escalable, orientada a facilitar el desarrollo de funcionalidades educativas basadas en IA. A continuación se detalla la estructura principal del proyecto y la función de cada carpeta o archivo relevante:

### 📁 Estructura principal del proyecto

```plaintext
tutor-ia/
├── .devcontainer/              # Configuración para contenedores de desarrollo (opcional)
├── .env                        # Variables de entorno locales
├── .gitattributes              # Reglas de Git para atributos de archivos
├── .gitignore                  # Archivos y carpetas ignoradas por Git
├── audios/                     # Carpeta para audios generados (opcional)
├── data/                       # Carpeta para datos adicionales (p. ej., docs.json)
├── logs_chat.txt               # Registro de interacciones del chat
├── README.md                   # Documentación principal del proyecto
├── requirements.txt            # Dependencias del proyecto
├── runtime.txt                 # Requisito de entorno para despliegues (ej. Render)
├── streamlit_app.py            # Frontend visual del proyecto en Streamlit
├── tutor_ia_logo.png           # Logo del proyecto
├── uploads/                    # Apuntes PDF subidos por el usuario
├── src/                        # Código fuente principal
│   ├── api/
│   │   └── routes/             # Endpoints de FastAPI, incluyendo CLI y Chat
│   │       └── cli_routes.py   # Punto principal de la API
│   ├── apuntes/
│   │   ├── rag/                # Módulos de vectorización y búsqueda
│   │   │   └── vectorstores/   # FAISS Vectorstores generados por materia/tema
│   │   └── scripts/
│   │       └── agents/         # Agentes generativos (clase magistral, enriquecimiento, etc.)
│   │       └── agent_tools.py  # Herramientas de postprocesado
│   ├── services/               # Lógica de negocio para responder, evaluar, enriquecer, etc.
│   └── config.py               # Variables de entorno y claves API
└── main.py                     # Entry point para lanzar FastAPI
```

### 🧩 Módulos clave

- **`api/routes/cli_routes.py`**  
  Contiene todos los endpoints expuestos por FastAPI: subida de apuntes, generación de clases magistrales, chat educativo, enriquecimiento, etc.

- **`apuntes/rag/`**  
  Aquí se almacenan los vectorstores de FAISS que permiten búsquedas semánticas rápidas sobre los apuntes vectorizados.

- **`apuntes/scripts/agents/`**  
  Agentes que generan contenido automáticamente: clases magistrales, subtemas avanzados, validación de calidad, etc.

- **`services/`**  
  Funciones core que procesan peticiones, ejecutan lógica y devuelven respuestas. Es la capa intermedia entre los endpoints y los modelos o herramientas externas.

- **`uploads/`**  
  Carpeta donde se almacenan temporalmente los archivos PDF subidos antes de ser procesados.

- **`config.py`**  
  Define variables como claves de API, rutas por defecto y configuraciones reutilizables.


## 🔄 Flujo de Trabajo: Subida de Apuntes → Vectorización → Consulta → Enriquecimiento

El flujo principal del proyecto **Tutor-IA** sigue una secuencia lógica que permite aprovechar al máximo los apuntes del estudiante mediante técnicas de procesamiento, búsqueda semántica y generación asistida por IA:

1. **📤 Subida del Apunte**  
   El usuario sube un archivo PDF a través del endpoint `/procesar_apunte`, indicando la `materia` y el `tema` correspondiente.

2. **🧹 Limpieza y Troceado**  
   El contenido del PDF se convierte en texto, se limpia (eliminando cabeceras, repeticiones, frases limitantes...) y se divide en fragmentos (chunks) coherentes desde el punto de vista semántico.

3. **📦 Vectorización e Indexación (FAISS)**  
   Los chunks son transformados en vectores mediante un modelo de embeddings. Estos vectores se almacenan en índices FAISS separados por `materia` y `tema`, permitiendo búsquedas eficientes por similitud semántica.

4. **🔍 Consulta del Usuario (RAG)**  
   Cuando el usuario realiza una pregunta, el sistema localiza los chunks más relevantes mediante búsqueda vectorial y construye un prompt contextualizado que se envía a un modelo LLM (Groq) para generar una respuesta fundamentada en los apuntes del alumno.

5. **🧠 Enriquecimiento Semiautomático**  
   A través del endpoint `/enriquecer_apuntes`, el sistema analiza los apuntes existentes, detecta lagunas de contenido, y sugiere subtemas adicionales. Luego genera desarrollos completos para cada subtema y los incorpora al vectorstore, ampliando así la base de conocimiento sin intervención manual.

Este flujo garantiza que el sistema evolucione con el tiempo, se mantenga centrado en los contenidos del estudiante, y mejore progresivamente su capacidad de respuesta mediante enriquecimiento continuo.

## 🧠 Funcionamiento del sistema RAG

### 🔍 ¿Qué es RAG (Retrieval-Augmented Generation)?

**RAG** es una técnica que combina dos enfoques en modelos de lenguaje:

- **Retrieval** (recuperación): busca información relevante en una base de datos o documentos antes de responder.
- **Augmented Generation** (generación aumentada): el modelo genera la respuesta basándose tanto en el contexto recuperado como en su conocimiento general.

Esto permite generar respuestas **más precisas y personalizadas**, incluso en dominios específicos como apuntes académicos.

---

### 🧾 ¿Cómo se usan FAISS y los apuntes vectorizados?

1. 📥 Cuando un estudiante sube un apunte en PDF, se analiza y se divide en fragmentos o *chunks* de texto.
2. 🧠 Cada fragmento se convierte en un vector numérico utilizando modelos de embeddings de Hugging Face.
3. 💾 Estos vectores se almacenan en un índice **FAISS**, organizado por materia y tema (`src/apuntes/rag/vectorstores`).
4. 🔎 Cuando se hace una pregunta, se transforma en vector y se compara con los fragmentos existentes en FAISS.
5. 📚 Los fragmentos más similares (contexto relevante) se pasan como input al modelo generativo para producir una respuesta fundamentada.

---

### 🤔 ¿Cuándo se considera una pregunta relevante?

El sistema utiliza la función `es_pregunta_relevante()` del módulo `rag_local.py`, que:

1. Convierte la pregunta en vector.
2. La compara con los vectores de los apuntes del tema correspondiente.
3. Si alguno supera un umbral de similitud determinado, se considera **relevante**.

---

### ⚖️ ¿Y si no es relevante?

- Si la pregunta no es considerada relevante, se comprueba si es una **pregunta genérica** (ej. "hazme un resumen").
- En ese caso, se fuerza una búsqueda contextual amplia usando todo el tema.
- Si no encaja en ninguna categoría, el sistema devuelve un mensaje indicando que no puede responder fuera de contexto.

---

> 🧠 Este enfoque permite un equilibrio entre precisión y flexibilidad, dando prioridad a la información contenida en los apuntes y evitando respuestas alucinadas.

## ✅ Casos de uso recomendados

Esta plataforma está diseñada para estudiantes y profesionales que deseen **aprovechar la inteligencia artificial para mejorar su aprendizaje**. A continuación, se describen los principales casos de uso:

---

### 📤 Subir apuntes y enriquecerlos automáticamente

- Los usuarios pueden subir apuntes en formato PDF clasificados por **materia** y **tema**.
- El sistema analiza el contenido, lo vectoriza y lo almacena de forma eficiente.
- Luego, se puede ejecutar un proceso de **enriquecimiento automático** que detecta lagunas de contenido y añade subtemas desarrollados por la IA, mejorando así la calidad del material de estudio.

---

### ❓ Formular preguntas sobre temas concretos

- El usuario puede hacer preguntas directamente sobre los temas que ha subido.
- El sistema utiliza RAG (Retrieval-Augmented Generation) para buscar información relevante en los apuntes y generar una respuesta coherente, confiable y adaptada.
- También se pueden hacer preguntas genéricas como “hazme un resumen” o “explica este tema”.

---

### 🧑‍🏫 Simular conversaciones educativas con IA

- Mediante el chat integrado, es posible mantener una conversación fluida con un **tutor académico virtual**.
- Se puede pedir explicaciones con distintos niveles de complejidad, incluyendo el modo **“explícalo como si tuviera 12 años”**.
- Ideal para repasar, resolver dudas o reforzar el aprendizaje de forma interactiva.

---

> 📚 La plataforma no solo responde, sino que también **evalúa desarrollos escritos**, genera clases magistrales completas y ofrece un sistema adaptable al progreso del estudiante.

## 🛠️ Checklist de contribución o desarrollo futuro

Este proyecto está en constante evolución. A continuación se presentan ideas, tareas pendientes y mejoras sugeridas para colaboradores o para el propio roadmap del proyecto.

---

> ✨ Si quieres contribuir, abre un Pull Request con una descripción clara de la mejora y asegúrate de mantener la coherencia con la arquitectura general del proyecto.



---

## 🛡️ Archivo `.env` requerido

Crea un archivo `.env` en la raíz del proyecto con al menos la siguiente clave:

```env
GROQ_API_KEY=tu_clave_groq_aqui
```


---

## 👥 Autores

Este proyecto ha sido desarrollado por Eugenio Barquín en el marco de la III Edicion del  Bootcamp Inteligencia Artificial Full Stack de KeepCoding 

## 📄 Licencia

Distribuido bajo la licencia MIT. Consulta el archivo LICENSE para más información.
