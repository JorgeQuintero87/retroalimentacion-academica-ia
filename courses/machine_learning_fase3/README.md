# Machine Learning - Fase 3
## Componente Práctico - Algoritmos No Supervisados de Agrupamiento

### 📋 Descripción General

Esta carpeta contiene la configuración y rúbrica de evaluación para la **Fase 3** del curso de Machine Learning, enfocada en la aplicación práctica de **algoritmos no supervisados de clustering**.

---

### 📁 Archivos en esta carpeta

1. **`rubrica_estructurada.json`**
   - Rúbrica de evaluación completa con 5 criterios
   - Puntaje total: 200 puntos
   - Niveles: Alto, Medio, Bajo, No Presentado
   - Calificación flexible (no estricta)

2. **`condiciones.json`**
   - Descripción detallada de las actividades a realizar
   - 4 ejercicios obligatorios
   - Requisitos de entrega
   - Recomendaciones para estudiantes

3. **`README.md`** (este archivo)
   - Documentación de la estructura de la carpeta

---

### 🎯 Resultado de Aprendizaje

**Aplicar algoritmos no supervisados de agrupamiento para encontrar patrones y estructuras de los datos**

---

### 📊 Criterios de Evaluación (200 puntos total)

| # | Criterio | Puntaje |
|---|----------|---------|
| 1 | K-Means Clustering (2 escenarios) | 60 pts |
| 2 | DBSCAN | 60 pts |
| 3 | Agglomerative Clustering | 60 pts |
| 4 | Participación en foro y feedback | 10 pts |
| 5 | Entrega según indicaciones | 10 pts |

---

### 🔬 Ejercicios Obligatorios

#### **Ejercicio 1: K-Means Clustering** (60 pts)
- **Escenario 1:** Clustering con 2 variables
  - Scatterplot con clusters
  - Método del codo
  - Silhouette Score

- **Escenario 2:** Clustering con más variables
  - Comparación con Escenario 1
  - Determinar cuál escenario es mejor
  - Describir perfiles de clusters del mejor modelo

#### **Ejercicio 2: DBSCAN** (60 pts)
- Usar **3 variables numéricas**
- Determinar parámetros:
  - Epsilon (ϵ)
  - min_samples
- Identificar clusters y puntos de ruido
- Describir perfiles de cada cluster

#### **Ejercicio 3: Agglomerative Clustering** (60 pts)
- Usar **4 variables numéricas**
- Justificar selección de variables
- Generar y analizar **dendrograma**
- Determinar número óptimo de clusters
- Describir perfiles de cada cluster

#### **Ejercicio 4: Feedback a Compañero** (10 pts)
- Seleccionar ejercicio de un compañero
- Retroalimentación constructiva
- Adjuntar screenshot

---

### 📦 Formato de Entrega

#### **1. Publicación en Foro**
- **Formato:** PDF o JPG
- **Contenido:** Los 3 ejercicios de clustering

#### **2. Entrega en Evaluación**
- **Formato:** `.ipynb` (Jupyter Notebook)
- **Nombre:** `G#_(nombre_apellido)_Fase3.ipynb`
- **Ejemplo:** `G15_Rafael_Gaitan_Fase3.ipynb`
- **Contenido:**
  - Código ejecutable
  - Gráficos y visualizaciones
  - Análisis y descripciones detalladas
  - Screenshot de feedback

---

### 🛠️ Herramientas Requeridas

- Python (local o Google Colab)
- Jupyter Notebook
- Librerías:
  - `scikit-learn`
  - `pandas`
  - `numpy`
  - `matplotlib`
  - `seaborn`
  - `scipy` (para dendrogramas)

---

### ⚠️ Notas Importantes

1. **Calificación flexible:** Se valora el esfuerzo y comprensión del estudiante
2. **Datasets:** Usar los mismos de la Fase 2
3. **Descripción de perfiles:** Debe ser detallada y con propias palabras
4. **Métricas obligatorias:**
   - K-Means: Método del codo + Silhouette Score
   - DBSCAN: Justificación de ϵ y min_samples
   - Agglomerative: Dendrograma
5. **Feedback:** Debe ser constructivo, respetuoso y específico

---

### 📌 Puntos Clave para Evaluación

✅ Correcta implementación de los 3 algoritmos
✅ Justificación técnica de parámetros
✅ Uso apropiado de métricas
✅ Descripciones detalladas de perfiles
✅ Gráficos claros y bien etiquetados
✅ Comparación entre escenarios (K-Means)
✅ Participación en foro
✅ Cumplimiento de formato de entrega

---

### 💡 Recomendaciones

- Explorar los datos antes de aplicar algoritmos
- Normalizar/estandarizar variables cuando sea apropiado
- Experimentar con diferentes valores de k
- Justificar todas las decisiones
- Incluir visualizaciones claras
- Describir perfiles de forma comprensible
- Realizar feedback constructivo

---

### 📞 Soporte

Para dudas o consultas sobre la rúbrica o las actividades, contactar al tutor del curso.

---

**Fecha de creación:** 2025
**Versión:** 1.0
**Curso:** Machine Learning - UNAD
