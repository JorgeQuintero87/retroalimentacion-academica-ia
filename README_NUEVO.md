# 📚 Sistema de Retroalimentación Académica con Rúbricas PDF

Sistema inteligente que **lee automáticamente rúbricas desde PDFs**, evalúa trabajos académicos y genera retroalimentación por criterios usando **Pinecone** + **GPT-4**.

## 🎯 **NUEVO: Características Actualizadas**

- ✅ **Lee rúbricas automáticamente desde PDFs** (español e inglés)
- ✅ **Extrae criterios de evaluación** con niveles de desempeño
- ✅ **Retroalimentación por criterios**: "Criterio 1", "Criterio 2", etc.
- ✅ **Niveles de desempeño**: Alto, Medio, Bajo con rangos de puntaje
- ✅ **Múltiples formatos**: PDF, imágenes, Jupyter Notebooks
- ✅ **Búsqueda semántica**: Pinecone compara con rúbricas
- ✅ **Interfaz intuitiva**: Streamlit con visualización clara

---

## 📁 Estructura del Proyecto

```
proyecto_retroalimentacion/
├── app.py                           # Aplicación principal (Streamlit)
├── .env                             # API keys configuradas
├── test_sistema_completo.py         # Script de prueba
│
├── courses/                         # Rúbricas por curso
│   ├── machine_learning/
│   │   ├── Rúbrica de evaluación - Fase 2.pdf  ← Lee automáticamente
│   │   └── Guía de aprendizaje.pdf
│   └── big_data_integration/
│       ├── Evaluation Rubric - Stage 2.pdf     ← Lee automáticamente
│       └── Learning Guide.pdf
│
├── processors/                      # Procesadores de documentos
│   ├── pdf_processor.py
│   ├── rubric_processor.py          ← NUEVO: Extrae criterios de PDFs
│   ├── image_processor.py
│   └── notebook_processor.py
│
├── vector_store/
│   └── pinecone_manager.py          ← Actualizado para criterios
│
└── feedback/
    └── gpt_feedback.py              ← Genera feedback por criterio
```

---

## 🚀 **Instalación Rápida**

### 1. Instalar dependencias

```bash
cd "C:\Users\DELL\Downloads\Gemini Agent\proyecto_retroalimentacion"
pip install -r requirements.txt
```

### 2. Configurar Tesseract (OCR para imágenes)

**Windows:**
- Descargar: https://github.com/UB-Mannheim/tesseract/wiki
- Instalar y agregar a PATH

### 3. **Cargar rúbricas en Pinecone** (NUEVO)

```bash
python test_sistema_completo.py
```

Este script:
- ✅ Extrae criterios desde los PDFs de rúbricas
- ✅ Indexa en Pinecone automáticamente
- ✅ Verifica que todo funcione

### 4. Ejecutar la app

```bash
python -m streamlit run app.py
```

---

## 📖 **Uso del Sistema**

### **Flujo completo:**

1. **Seleccionar curso**: Machine Learning o Big Data Integration
2. **El sistema lee automáticamente** la rúbrica PDF del curso
3. **Subir documento** del estudiante (PDF, imagen o .ipynb)
4. **Click en "Evaluar"**
5. **Ver retroalimentación** por criterio:
   - **Criterio 1**: Carga y análisis de datasets (30 pts)
   - **Criterio 2**: Modelos de regresión (50 pts)
   - **Criterio 3**: Modelos de clasificación (50 pts)
   - etc.
6. **Descargar reporte** en JSON

---

## 📊 **Ejemplo de Salida**

```
📊 Evaluación: Machine Learning
Puntaje Final: 118/150 (78.7%) 🟢 Aprobado

📝 Retroalimentación General:
El estudiante demuestra un buen dominio de los conceptos de ML.
La implementación es funcional pero puede mejorar en documentación.

✓ Fortalezas:
- Correcto uso de scikit-learn y métricas apropiadas
- Buena exploración de datos con visualizaciones

⚠ Áreas de Mejora:
- Agregar validación cruzada en modelos
- Documentar decisiones de preprocesamiento

📑 Evaluación por Criterio:

🔍 Criterio 1: Carga, contextualiza y analiza datasets - 28/30 pts (🟢 ALTO)
   Aspectos cumplidos:
   - Carga correcta de datasets
   - Contextualización relevante

   Sugerencias:
   - Agregar más análisis de correlaciones

🔍 Criterio 2: Aplica modelos de regresión - 45/50 pts (🟢 ALTO)
   ...
```

---

## 🔧 **Cómo Funciona Internamente**

### **1. Extracción de Rúbricas (Nuevo)**

```python
# processors/rubric_processor.py
processor = RubricProcessor()
rubric = processor.extract_rubric_from_pdf(
    "Rúbrica.pdf",
    "Machine Learning"
)

# Resultado:
{
    "criterios_evaluacion": [
        {
            "numero": 1,
            "nombre": "Carga y analiza datasets",
            "puntaje_maximo": 30,
            "niveles": [
                {"nivel": "alto", "puntaje_minimo": 26, "puntaje_maximo": 30},
                {"nivel": "medio", "puntaje_minimo": 21, "puntaje_maximo": 25},
                {"nivel": "bajo", "puntaje_minimo": 1, "puntaje_maximo": 20}
            ]
        },
        ...
    ]
}
```

### **2. Indexación en Pinecone**

```python
# vector_store/pinecone_manager.py
manager = PineconeManager()
manager.load_all_rubrics(use_pdf=True)  # Lee PDFs automáticamente

# Crea embeddings de cada criterio:
# "Criterio 1: Carga datasets (30 pts) - Nivel alto: carga correcta..."
```

### **3. Evaluación con GPT**

```python
# feedback/gpt_feedback.py
feedback = generator.generate_criterion_feedback(
    criterion={
        "numero": 1,
        "nombre": "Carga y analiza datasets",
        "puntaje_maximo": 30,
        "niveles": [...]
    },
    document_content="contenido del estudiante...",
    course_name="Machine Learning"
)

# GPT retorna:
{
    "nivel_alcanzado": "alto",
    "puntaje": 28,
    "feedback": "El estudiante carga correctamente los datasets...",
    "aspectos_cumplidos": [...],
    "mejoras": [...]
}
```

---

## 🏫 **Agregar Nuevo Curso**

### **Opción 1: Desde PDF (Recomendado)**

1. Crear carpeta: `courses/nuevo_curso/`
2. Copiar PDF de rúbrica: `Rúbrica.pdf`
3. Actualizar `app.py` y `pinecone_manager.py`:

```python
course_configs = {
    'nuevo_curso': {
        'name': 'Nombre del Curso',
        'rubric_pdf': 'Rúbrica.pdf'
    }
}
```

4. Recargar rúbricas:
```bash
python test_sistema_completo.py
```

### **Opción 2: Crear JSON manualmente**

Ver README original para estructura JSON.

---

## 🧪 **Testing**

```bash
# Test completo
python test_sistema_completo.py

# Test solo procesador de rúbricas
python processors/rubric_processor.py

# Test Pinecone
python vector_store/pinecone_manager.py
```

---

## 📝 **Notas Importantes**

### **Costos**
- GPT-4o-mini: ~$0.02 USD por evaluación (5 criterios)
- text-embedding-3-large: ~$0.001 USD por rúbrica indexada
- Pinecone: Plan gratuito soporta 100K vectores

### **Formato de Rúbricas PDF Soportado**

✅ **Español:**
- Primer criterio de evaluación
- Segundo criterio de evaluación
- Nivel alto / medio / bajo

✅ **Inglés:**
- First evaluation criterion
- Second evaluation criterion
- High Level / Average Level / Low Level

### **Limitaciones Actuales**

- Solo soporta rúbricas con estructura: "Criterio X de evaluación"
- Máximo 7 criterios por rúbrica (expandible)
- Niveles fijos: alto, medio, bajo

---

## 🛠 **Solución de Problemas**

**Error: "No se encontraron criterios"**
- Verificar que el PDF tenga el formato: "Primer/First criterio de evaluación"
- Ver logs del procesador: `python processors/rubric_processor.py`

**Error: "Vector dimension mismatch"**
- El código ya usa `text-embedding-3-large` (3072 dim)
- Si tu índice usa otra dimensión, recrearlo o ajustar código

**Rúbrica mal extraída**
- El procesador usa regex para detectar criterios
- Si el formato es diferente, ajustar `rubric_processor.py` líneas 40-80

---

## 📧 **Soporte**

Para issues o mejoras, contactar al desarrollador.

---

**Desarrollado con:** Python 3.10+, Streamlit, Pinecone, OpenAI GPT-4, scikit-learn, pdfplumber
