# Instrucciones de Prueba - Sistema de Retroalimentación

## ✅ Cambios Implementados

El sistema ahora **detecta automáticamente qué criterios están presentes** en el documento del estudiante.

### Funcionalidad:
- **Criterios 1, 2, 3**: Se evalúan SOLO si se encuentra evidencia (keywords: datasets, regresión, clasificación)
- **Criterios 4, 5**: Siempre se evalúan (participación y formato)
- **Criterios no presentados**: Aparecen como "⚫ NO PRESENTADO" con 0 puntos

---

## 🚀 Cómo Probar

### 1. Iniciar la aplicación:
```bash
cd C:\Users\DELL\Downloads\Gemini Agent\proyecto_retroalimentacion
python -m streamlit run app.py
```

### 2. En la interfaz web:
- Seleccionar curso: **Machine Learning**
- Subir un documento que **solo contenga evidencia del Criterio 4** (participación en foro)
- Hacer clic en **"🚀 Evaluar Documento"**

### 3. Resultados esperados:
```
📊 Evaluación: Machine Learning
Puntaje Final: X/150 (donde X es solo el puntaje del criterio 4)

📑 Evaluación por Criterio:

⚫ Criterio 1: Carga datasets - 0/30 pts (⚫ NO PRESENTADO)
⚫ Criterio 2: Modelos de regresión - 0/50 pts (⚫ NO PRESENTADO)
⚫ Criterio 3: Modelos de clasificación - 0/50 pts (⚫ NO PRESENTADO)
🟢 Criterio 4: Participación en foro - X/10 pts (🟢 ALTO/🟡 MEDIO/🔴 BAJO)
🟢 Criterio 5: Formato del documento - X/10 pts (🟢 ALTO/🟡 MEDIO/🔴 BAJO)
```

---

## 🔍 Palabras Clave por Criterio

El sistema busca estas palabras para determinar si un criterio está presente:

- **Criterio 1** (Datasets): dataset, datos, carga, csv, data, análisis, limpieza, contextualiza
- **Criterio 2** (Regresión): regresión, regression, MAE, MSE, RMSE, R², LinearRegression, modelo de regresión
- **Criterio 3** (Clasificación): clasificación, classification, accuracy, precision, recall, F1, matriz de confusión, RandomForest, LogisticRegression
- **Criterio 4** (Foro): Siempre se evalúa
- **Criterio 5** (Formato): Siempre se evalúa

---

## 📌 Notas Importantes

- Si un documento **no tiene** palabras clave de un criterio → **0 puntos automáticamente**
- Si tiene **1 keyword** → GPT confirma si realmente está presente
- Si tiene **2+ keywords** → Se evalúa normalmente
- El **puntaje total** solo suma los criterios presentados

---

## ✅ Verificación del Fix

Para verificar que el problema está resuelto:

1. Subir documento solo con Criterio 4 (foro)
2. Ver que Criterios 1, 2, 3 muestran "NO PRESENTADO"
3. Verificar que solo Criterio 4 tenga puntaje > 0
4. Confirmar que el puntaje total = suma de solo los criterios presentados

---

¡Sistema listo para usar! 🎉
