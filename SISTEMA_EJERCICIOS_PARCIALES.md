# Sistema de Evaluación de Ejercicios Parciales

## 🎯 Problema Identificado

El sistema evalúa **CRITERIOS COMPLETOS**, pero los estudiantes pueden presentar **EJERCICIOS INDIVIDUALES** dentro de un criterio.

### Ejemplo:
**Criterio 2**: "Aplica modelos de regresión junto con las respectivas métricas"
- Puede incluir: Ejercicio 1 (regresión lineal), Ejercicio 2 (regresión polinomial), Ejercicio 3 (regresión ridge)
- Estudiante sube: `ejercicio_2.pdf` (solo regresión polinomial)
- **Problema**: El sistema evaluaba como si presentó TODO el Criterio 2

---

## ✅ Solución Implementada: Evaluación Proporcional con GPT

El sistema ahora **detecta automáticamente** si el estudiante presentó:
- ✅ **Criterio completo** → Evalúa con niveles normales (alto/medio/bajo)
- ⚠️ **Solo algunos ejercicios** → Asigna puntaje **PROPORCIONAL**

### Cómo Funciona:

**GPT ahora recibe instrucciones para**:
1. Identificar cuántos ejercicios presentó vs cuántos debía presentar
2. Asignar puntaje proporcional:
   - Si presentó **1 de 3 ejercicios** → Máximo 33% del puntaje (ejemplo: 17/50 puntos)
   - Si presentó **2 de 3 ejercicios** → Máximo 66% del puntaje (ejemplo: 33/50 puntos)
   - Si presentó **3 de 3 ejercicios** → 100% del puntaje (hasta 50/50 puntos)
3. Mencionar en el feedback cuántos ejercicios faltan

---

## 📊 Ejemplos de Evaluación

### Ejemplo 1: Solo Ejercicio 2 de Regresión

**Archivo**: `ejercicio_2.pdf`
**Contenido**: Regresión polinomial con métricas

**Evaluación del Criterio 2** (50 pts máx):
```
🟡 Criterio 2: Modelos de regresión - 17/50 pts (MEDIO)

Feedback:
"El estudiante presentó correctamente el ejercicio 2 (regresión polinomial)
con métricas apropiadas (MAE, MSE, RMSE, R²). Sin embargo, solo completó
1 de 3 ejercicios solicitados. Faltan: regresión lineal simple y regresión
ridge/lasso."

Aspectos cumplidos:
- Implementación correcta de regresión polinomial
- Cálculo adecuado de métricas de evaluación

Mejoras:
- Completar los ejercicios faltantes (regresión lineal y ridge)
- Presentar comparación entre los diferentes modelos
```

### Ejemplo 2: Todos los Ejercicios de Regresión

**Archivo**: `tarea_completa.pdf`
**Contenido**: Regresión lineal + polinomial + ridge con análisis comparativo

**Evaluación del Criterio 2** (50 pts máx):
```
🟢 Criterio 2: Modelos de regresión - 48/50 pts (ALTO)

Feedback:
"El estudiante completó todos los ejercicios solicitados (regresión lineal,
polinomial y ridge) con excelente implementación y análisis comparativo.
Las métricas están correctamente calculadas e interpretadas."

Aspectos cumplidos:
- Implementación de los 3 modelos de regresión solicitados
- Cálculo e interpretación de todas las métricas (MAE, MSE, RMSE, R²)
- Análisis comparativo entre modelos

Mejoras:
- Profundizar en la explicación de cuándo usar cada modelo
- Agregar visualizaciones de residuos
```

---

## 🚀 Cómo Usar el Sistema

### Para Estudiantes:

1. **Presentación parcial** (solo algunos ejercicios):
   - Nombrar archivo: `ejercicio_2.pdf`, `actividad_1.ipynb`, etc.
   - El sistema evaluará **solo lo presentado** con puntaje proporcional
   - Recibirás feedback indicando qué falta

2. **Presentación completa** (todos los ejercicios):
   - Nombrar archivo: `trabajo_completo.pdf`, `fase_2.ipynb`, etc.
   - El sistema evaluará TODO con puntaje completo (0-100%)

### Para Profesores:

El sistema ahora es **más justo**:
- ✅ No penaliza con 0 puntos si presentó algo (antes lo hacía)
- ✅ Asigna puntaje proporcional automáticamente
- ✅ Indica claramente en el feedback qué falta

---

## ⚙️ Configuración Actual

**Keywords flexibles**:
- Solo requiere **1 grupo de keywords** para detectar presencia
- No usa exclusiones automáticas (permite trabajos completos)

**Validación GPT**:
- Modo **JUSTO** (no extremadamente estricto)
- Da beneficio de la duda al estudiante
- Acepta confianza baja si hay pista de archivo

**Puntaje proporcional**:
- GPT calcula automáticamente según completitud
- Ejemplo: 1 de 3 ejercicios = máximo 33% del puntaje del criterio

---

## 🔧 Limitaciones Actuales

1. **No hay sub-rúbrica por ejercicio**: GPT estima la proporción, no hay puntajes exactos por ejercicio
2. **Depende de GPT**: Si GPT no identifica bien cuántos ejercicios hay, el puntaje puede variar
3. **Nombres de archivo**: Son pistas, no absolutos (permite flexibilidad)

---

## 💡 Recomendación para Mejorar

Si necesitas **evaluación precisa por ejercicio**, deberías crear una rúbrica con:

```json
{
  "criterio_2_ejercicio_1": {
    "nombre": "Regresión Lineal Simple",
    "puntaje_maximo": 17
  },
  "criterio_2_ejercicio_2": {
    "nombre": "Regresión Polinomial",
    "puntaje_maximo": 17
  },
  "criterio_2_ejercicio_3": {
    "nombre": "Regresión Ridge/Lasso",
    "puntaje_maximo": 16
  }
}
```

¿Quieres que implemente esta estructura detallada?

---

🎉 **Sistema actualizado y funcional para evaluación proporcional!**
