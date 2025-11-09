# Sistema de Retroalimentación Académica

Sistema automatizado para evaluar documentos académicos (PDF, imágenes, Jupyter Notebooks) con feedback personalizado usando IA.

## Proyectos incluidos

### 1. Sistema de Retroalimentación Académica
Sistema principal de evaluación de documentos académicos con IA.

### 2. [Medidor de Velocidad de Mano](./speed-measurement/)
Aplicación web que utiliza IA para medir la velocidad con la que bajas tu mano usando la cámara.
- Detección de manos en tiempo real con MediaPipe
- Cálculo de velocidad, distancia y tiempo
- Interfaz moderna y responsive
- [Ver demo](https://jorgeQuintero87.github.io/retroalimentacion-academica-ia/speed-measurement/)

## Características

- ✅ Soporta PDFs con texto y con imágenes (OCR)
- ✅ Lee archivos .ipynb, .png, .jpg
- ✅ Detecta ejercicios específicos presentados
- ✅ Genera feedback personalizado y motivador
- ✅ Evaluación basada en rúbricas estructuradas
- ✅ Usa Pinecone (búsqueda semántica) + GPT-4o-mini

## Deployment en Streamlit Cloud

### Paso 1: Subir a GitHub

```bash
git init
git add .
git commit -m "Sistema de retroalimentación académica"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/retroalimentacion-academica.git
git push -u origin main
```

### Paso 2: Configurar Streamlit Cloud

1. Ir a https://share.streamlit.io
2. Iniciar sesión con GitHub
3. Clic en "New app"
4. Seleccionar tu repositorio
5. Main file: `app.py`

### Paso 3: Configurar Secrets

En la configuración del app, agregar:

```toml
PINECONE_API_KEY = "tu_api_key_aqui"
OPENAI_API_KEY = "tu_api_key_aqui"
INDEX_NAME = "rubricamachine"
NAMESPACE = "solomachine"
```

### Paso 4: Deploy

Streamlit Cloud instalará automáticamente:
- Dependencias de `requirements.txt`
- Paquetes del sistema de `packages.txt`

## Estructura del Proyecto

```
proyecto_retroalimentacion/
├── app.py                          # Interfaz Streamlit
├── processors/
│   └── pdf_processor.py           # Procesamiento PDFs con OCR
├── vector_store/
│   └── pinecone_manager.py        # Gestión de Pinecone
├── feedback/
│   └── gpt_feedback.py            # Generación de feedback con GPT
├── courses/
│   ├── machine_learning/
│   │   └── rubrica_estructurada.json
│   └── big_data_integration/
│       └── rubrica_estructurada.json
├── requirements.txt               # Dependencias Python
└── packages.txt                   # Paquetes del sistema (Tesseract, Poppler)
```

## Uso Local

1. Instalar dependencias:
```bash
pip install -r requirements.txt
```

2. Configurar variables de entorno (.env):
```
PINECONE_API_KEY=...
OPENAI_API_KEY=...
INDEX_NAME=rubricamachine
NAMESPACE=solomachine
```

3. Ejecutar:
```bash
streamlit run app.py
```

## Tecnologías

- **Streamlit**: Interfaz web
- **OpenAI GPT-4o-mini**: Generación de feedback
- **Pinecone**: Base de datos vectorial
- **Tesseract OCR**: Extracción de texto de imágenes
- **Poppler**: Conversión PDF a imágenes
- **pdfplumber**: Procesamiento de PDFs

## Autor

Proyecto desarrollado para retroalimentación académica automatizada.
