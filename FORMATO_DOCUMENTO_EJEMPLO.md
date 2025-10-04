# Formato Correcto de Documentos para Evaluación

## 🎯 Cómo Estructurar tu Documento

Para que el sistema detecte correctamente qué ejercicios presentaste, tu documento debe incluir **literalmente** las palabras clave que el sistema busca.

---

## ✅ Ejemplo CORRECTO - Detectará los ejercicios

```markdown
# Tarea de Machine Learning - Regresión

## Ejercicio 1: Regresión Lineal Simple

Implementación de regresión lineal...

[tu código aquí]

Resultados:
- MAE: 0.25
- MSE: 0.15
- RMSE: 0.38
- R²: 0.85

## Ejercicio 2: Regresión Polinomial

Implementación de regresión polinomial de grado 3...

[tu código aquí]

Resultados:
- MAE: 0.18
- MSE: 0.09
- RMSE: 0.30
- R²: 0.92

## Ejercicio 3: Regresión Ridge

Implementación de regresión ridge con regularización...

[tu código aquí]

Resultados:
- MAE: 0.20
- MSE: 0.10
- RMSE: 0.32
- R²: 0.90
```

### Lo que detectará el sistema:
```
🔍 Ejercicios detectados: [1, 2, 3]
✅ Criterio 2: PRESENTE (presentó los 3 ejercicios)
📊 Evaluación: 45-50/50 pts (100% presentado, evaluación de calidad)
```

---

## ✅ Ejemplo CORRECTO - Solo algunos ejercicios

```markdown
# Tarea de Machine Learning

## Ejercicio 2

Implementación de regresión polinomial...

[tu código aquí]
```

### Lo que detectará el sistema:
```
🔍 Ejercicios detectados: [2]
✅ Criterio 2: PRESENTE (presentó 1 de 3 ejercicios)
📊 Evaluación: 15-17/50 pts (33% presentado)
Feedback: "El estudiante presentó solo el Ejercicio 2. Faltan: Ejercicio 1 y 3."
```

---

## ❌ Ejemplo INCORRECTO - NO detectará ejercicios

```markdown
# Tarea de Regresión

## Implementación de Modelos

Aquí implementé varios modelos de regresión...

### Modelo 1: Lineal
[código...]

### Modelo 2: Polinomial
[código...]
```

### Problema:
```
⚠️ NO dice "Ejercicio 1", "Ejercicio 2", etc.
❌ El sistema NO detectará ejercicios específicos
🤷 Evaluará con keywords genéricas (menos preciso)
```

---

## 📋 Palabras Clave que el Sistema Busca

El sistema busca **literalmente** estas palabras (no case-sensitive):

### Español:
- ✅ `Ejercicio 1`, `Ejercicio 2`, `Ejercicio 3`
- ✅ `ejercicio 1`, `EJERCICIO 1`
- ✅ `Actividad 1`, `Actividad 2`
- ✅ `Punto 1`, `Punto 2`
- ✅ `Tarea 1`, `Tarea 2`
- ✅ `Ítem 1`, `Ítem 2`

### Inglés:
- ✅ `Exercise 1`, `Exercise 2`, `Exercise 3`
- ✅ `Activity 1`, `Activity 2`
- ✅ `Task 1`, `Task 2`
- ✅ `Item 1`, `Item 2`

---

## 📝 Plantilla Recomendada para Jupyter Notebook

```python
# %% [markdown]
# # Tarea de Machine Learning - Fase 2
#
# Estudiante: [Tu Nombre]
# Fecha: [Fecha]

# %% [markdown]
# ## Ejercicio 1: Carga y Análisis de Datos
#
# En este ejercicio cargo el dataset y realizo análisis exploratorio...

# %%
import pandas as pd
import numpy as np

# Cargar dataset
df = pd.read_csv('data.csv')
df.head()

# %% [markdown]
# ## Ejercicio 2: Modelos de Regresión
#
# Implementación de diferentes modelos de regresión...

# %%
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

# Implementación...

# %% [markdown]
# ## Ejercicio 3: Modelos de Clasificación
#
# Implementación de modelos de clasificación...

# %%
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score

# Implementación...
```

---

## 🚀 Nomenclatura de Archivos Recomendada

Para mejor detección, nombra tus archivos:

### Si presentas TODO:
- `trabajo_completo.pdf`
- `fase_2_completa.ipynb`
- `tarea_machine_learning.pdf`

### Si presentas PARCIAL:
- `ejercicio_1.pdf` (solo ejercicio 1)
- `ejercicio_2.ipynb` (solo ejercicio 2)
- `ejercicios_1_2.pdf` (ejercicios 1 y 2)

---

## ⚠️ Notas Importantes

1. **Las palabras deben aparecer literalmente** en tu documento
2. **No importa el formato** (PDF, .ipynb, imagen) - el sistema extrae el texto
3. **El número del ejercicio debe estar junto** a la palabra (ej: "Ejercicio 1", no "Ejercicio número 1")
4. **Puedes usar mayúsculas/minúsculas** - el sistema no distingue
5. **Los ejercicios pueden estar en cualquier orden** - el sistema los detecta todos

---

## ✅ Verificación Rápida

Antes de subir tu documento, verifica:

- [ ] ¿Incluiste "Ejercicio 1", "Ejercicio 2", etc. como títulos?
- [ ] ¿Cada ejercicio tiene su código/contenido debajo del título?
- [ ] ¿Incluiste las métricas/resultados requeridos?
- [ ] ¿El nombre del archivo describe lo que presentaste?

---

¡Con este formato, el sistema detectará correctamente tus ejercicios! 🎉
