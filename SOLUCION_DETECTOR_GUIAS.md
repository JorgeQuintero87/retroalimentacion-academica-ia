# Solucion Implementada: Detector de Guias/Instrucciones

## Problema Identificado

El usuario identifico otro problema critico:

> "como es posible que yo le suba el documento de la actividad y me califique bien, sabiendo que es la guia del estudiante as no la solucion"

**Problema**: El sistema calificaba bien la **GUIA/INSTRUCCIONES** de la actividad (documento que indica QUE debe hacer el estudiante) en lugar de rechazarla, porque NO es la solucion/entrega real del estudiante.

---

## Solucion Implementada

### 1. Creacion de `document_type_validator.py`

**Ubicacion**: `C:\Users\DELL\Downloads\Gemini Agent\proyecto_retroalimentacion\feedback\document_type_validator.py`

**Funcionamiento**:
- Usa GPT-4o-mini para analizar el contenido del documento
- Detecta si es una GUIA/INSTRUCCIONES o una ENTREGA REAL del estudiante
- Identifica indicadores especificos de cada tipo

**Clase Principal**: `DocumentTypeValidator`

**Metodo Principal**: `validate_is_student_work(document_content)`

**Retorna**:
```python
{
    'is_student_work': bool,          # True si es trabajo del estudiante
    'confidence': str,                # 'alta', 'media', 'baja'
    'document_type': str,             # 'guia_actividad', 'entrega_estudiante', 'indeterminado'
    'evidence_guide': list,           # Evidencias de que es guia
    'evidence_student_work': list,    # Evidencias de que es trabajo
    'explanation': str,               # Explicacion detallada
    'recommendation': str             # Mensaje para el usuario
}
```

---

### 2. Indicadores que Detecta

#### INDICADORES DE GUIA/INSTRUCCIONES:

1. **Frases imperativas**:
   - "El estudiante debe", "Usted debe", "Se requiere que"
   - "Realice", "Desarrolle", "Implemente", "Calcule"

2. **Estructura de guia**:
   - "Ejercicio 1: [descripcion de lo que debe hacer]"
   - "Esta actividad consiste en..."
   - "El objetivo es que el estudiante..."

3. **Rubricas de evaluacion**:
   - Tablas con criterios de calificacion
   - Puntajes maximos y minimos por criterio
   - Niveles de desempeno (alto, medio, bajo)
   - Descripciones de criterios de evaluacion

4. **Criterios de entrega**:
   - Formatos requeridos
   - Fechas de entrega
   - Requisitos de formato

#### INDICADORES DE TRABAJO REAL DEL ESTUDIANTE:

1. **Codigo ejecutable**:
   - `import pandas`, `import sklearn`, `import matplotlib`
   - Codigo real ejecutado (no ejemplos teoricos)

2. **Resultados especificos**:
   - "RMSE: 2.34" (numeros reales, no placeholders)
   - "Accuracy: 0.85"
   - "Silhouette Score: 0.72"
   - "epsilon = 0.5, min_samples = 5"

3. **Datasets cargados**:
   - "df = pd.read_csv('liver-disorders.csv')"
   - Nombres especificos de archivos

4. **Analisis personal**:
   - Primera persona: "Seleccione las variables...", "Determine que..."
   - Interpretaciones personales
   - Conclusiones propias

5. **Graficos y visualizaciones**:
   - Descripciones de graficos generados
   - Imagenes insertadas
   - Outputs de codigo

---

### 3. Integracion en `app.py`

**Ubicacion de cambios**: `app.py` lineas 385-428

**Flujo de Validacion**:

```
1. Usuario sube documento
2. Sistema extrae contenido
3. VALIDACION 1: Tipo de Documento (NUEVA)
   ├─ Si es GUIA → BLOQUEAR con confianza alta/media
   ├─ Si es TRABAJO → Continuar
   └─ Si es INDETERMINADO → Advertencia y continuar
4. VALIDACION 2: Fase correcta
   └─ (validacion existente)
5. Evaluacion del documento
```

**Codigo de Integracion**:
```python
# VALIDACION 1: Tipo de Documento
type_validator = DocumentTypeValidator()
type_result = type_validator.validate_is_student_work(content)

if type_result['is_student_work']:
    st.success("Documento validado: Es una entrega de estudiante")
else:
    if confidence in ['alta', 'media']:
        st.error("Este documento parece ser una GUIA, NO una entrega")
        # Mostrar evidencias
        st.stop()  # BLOQUEAR evaluacion
```

---

### 4. Tests Implementados

**Archivo**: `feedback/document_type_validator.py` (incluye tests)

**Test 1**: Documento que es GUIA DE ACTIVIDAD
- Contiene: "El estudiante debe", rubricas, puntajes, criterios
- **Resultado Esperado**: RECHAZADO
- **Resultado Real**: ✓ RECHAZADO (document_type: guia_actividad, confidence: alta)
- **Evidencias detectadas**:
  - "Frases como 'El estudiante debe aplicar el algoritmo K-Means'"
  - "Rubrica de evaluacion con criterios de calificacion y puntajes"
  - "Formato de 'Ejercicio 1' describe lo que debe hacer"

**Test 2**: Documento que es TRABAJO REAL DEL ESTUDIANTE
- Contiene: Codigo Python, metricas reales, analisis personal
- **Resultado Esperado**: ACEPTADO
- **Resultado Real**: ✓ ACEPTADO (document_type: entrega_estudiante, confidence: alta)
- **Evidencias detectadas**:
  - "Codigo fuente ejecutable con importaciones y carga de datos"
  - "Resultados numericos especificos (Silhouette Score, inercia)"
  - "Analisis y conclusiones en primera persona"

**Conclusion**: Todos los tests PASARON correctamente.

---

## Como Funciona en la Practica

### Escenario 1: Usuario sube GUIA de actividad (instrucciones)

**Documento contiene**:
```
# Fase 3 - Componente Practico

## Ejercicio 1: K-Means Clustering (60 puntos)

El estudiante debe aplicar el algoritmo K-Means en dos escenarios:

### Escenario 1: Agrupacion con dos variables
- Seleccione dos variables numericas
- Determine cuantos clusters (k) serian adecuados
- Grafique un scatterplot

## Rubrica de Evaluacion

| Nivel | Puntaje | Descripcion |
|-------|---------|-------------|
| Alto  | 51-60   | Aplica correctamente K-means |
| Medio | 42-50   | Aplica con dificultades |
```

**Proceso**:
1. Sistema procesa el documento
2. **DocumentTypeValidator analiza**:
   - Encuentra: "El estudiante debe", rubricas, puntajes, criterios
   - NO encuentra: codigo ejecutable, metricas reales, analisis personal
3. **Resultado**:
   ```
   [ADVERTENCIA] Este documento parece ser una GUIA/INSTRUCCIONES
   de actividad, NO una entrega del estudiante. No debe ser calificado.

   Tipo detectado: guia_actividad
   Confianza: alta
   ```

4. **Accion**: Sistema **BLOQUEA** la evaluacion y muestra:
   - Error en rojo
   - Evidencias de que es guia
   - Falta de evidencias de trabajo real
   - Mensaje: "Suba el trabajo desarrollado por el estudiante"

5. Usuario **NO puede continuar** hasta subir el trabajo real

---

### Escenario 2: Usuario sube TRABAJO REAL del estudiante

**Documento contiene**:
```python
# Machine Learning - Fase 3
## Estudiante: Juan Perez

## Ejercicio 1: K-Means Clustering

import pandas as pd
from sklearn.cluster import KMeans

df = pd.read_csv('customers.csv')

# Escenario 1: 2 variables
kmeans = KMeans(n_clusters=4)
kmeans.fit(df[['edad', 'ingresos']])

Silhouette Score obtenido: 0.72

Resultados:
- Cluster 0: 45 clientes - Jovenes de bajos ingresos
- Cluster 1: 62 clientes - Adultos de ingresos medios

Conclusion: El Escenario 2 es mejor (Silhouette Score: 0.81)
```

**Proceso**:
1. Sistema procesa el documento
2. **DocumentTypeValidator analiza**:
   - Encuentra: codigo Python, metricas reales (0.72, 0.81), analisis personal
   - NO encuentra: frases imperativas, rubricas, puntajes
3. **Resultado**:
   ```
   [OK] Este documento parece ser una entrega real del estudiante.
   Puede procederse con la evaluacion.

   Tipo detectado: entrega_estudiante
   Confianza: alta
   ```

4. **Accion**: Sistema **PERMITE** continuar con la validacion de fase y evaluacion

---

## Ventajas de la Solucion

1. **Previene calificar guias**: No permite evaluar documentos de instrucciones
2. **Inteligente**: Usa GPT para detectar el tipo de documento, no solo palabras clave
3. **Informativo**: Muestra evidencias especificas de por que es guia o trabajo
4. **Doble capa de seguridad**:
   - VALIDACION 1: Tipo de documento (guia vs trabajo)
   - VALIDACION 2: Fase correcta (Fase 2 vs Fase 3)
5. **Flexible**: Con confianza baja, permite continuar con advertencia
6. **Ejecuta ANTES**: Se ejecuta antes de cualquier evaluacion, ahorrando tiempo

---

## Comparacion: Sistema Anterior vs Nuevo

### ANTES:
```
Usuario sube GUIA → Sistema evalua → Califica BIEN (ERROR!)
```

### AHORA:
```
Usuario sube GUIA → Detector identifica tipo → BLOQUEA evaluacion
                                             → Muestra error
                                             → No permite continuar
```

---

## Archivos Modificados/Creados

### Archivos Creados:
1. `feedback/document_type_validator.py` - Detector de tipo de documento (NUEVO)
2. `SOLUCION_DETECTOR_GUIAS.md` - Este documento (NUEVO)

### Archivos Modificados:
1. `app.py` (lineas 17, 385-428) - Integracion del detector

---

## Flujo Completo de Validaciones

```
USUARIO SUBE DOCUMENTO
        |
        v
1. PROCESAMIENTO
   - Extrae texto (PDF/imagen/notebook)
        |
        v
2. VALIDACION TIPO DE DOCUMENTO (NUEVA)
   - ¿Es guia o trabajo?
   - Si es GUIA → BLOQUEAR
   - Si es TRABAJO → Continuar
        |
        v
3. VALIDACION DE FASE (EXISTENTE)
   - ¿Corresponde a la fase?
   - Si NO corresponde → BLOQUEAR
   - Si corresponde → Continuar
        |
        v
4. EVALUACION CON GPT
   - Califica segun rubrica
   - Genera feedback
        |
        v
5. MUESTRA RESULTADOS
```

---

## Como Ejecutar Tests

### Test del Detector de Tipo de Documento:
```bash
cd "C:\Users\DELL\Downloads\Gemini Agent\proyecto_retroalimentacion"
python feedback/document_type_validator.py
```

**Salida esperada**:
```
TEST 1 (Rechazar GUIA): [PASS]
TEST 2 (Aceptar TRABAJO): [PASS]
[SUCCESS] Validador funciona correctamente
```

---

## Ejemplos de Deteccion

### Ejemplo 1: GUIA detectada correctamente

**Input**: Documento con texto
```
El estudiante debe aplicar K-Means...
Rubrica de Evaluacion:
| Alto | 51-60 puntos | Aplica correctamente |
```

**Output**:
```json
{
  "is_student_work": false,
  "document_type": "guia_actividad",
  "confidence": "alta",
  "evidence_guide": [
    "Frases como 'El estudiante debe'",
    "Rubrica de evaluacion con puntajes",
    "Formato de ejercicio describe tareas"
  ],
  "recommendation": "[ADVERTENCIA] Este documento parece ser una GUIA..."
}
```

### Ejemplo 2: TRABAJO detectado correctamente

**Input**: Documento con codigo
```python
import pandas as pd
df = pd.read_csv('data.csv')
Silhouette Score: 0.72
Cluster 0: Jovenes de bajos ingresos
```

**Output**:
```json
{
  "is_student_work": true,
  "document_type": "entrega_estudiante",
  "confidence": "alta",
  "evidence_student_work": [
    "Codigo ejecutable con importaciones",
    "Resultados numericos especificos (0.72)",
    "Analisis personal de clusters"
  ],
  "recommendation": "[OK] Este documento parece ser una entrega real..."
}
```

---

## Resumen

**Problema**: Sistema calificaba GUIAS/INSTRUCCIONES como si fueran entregas del estudiante

**Solucion**: Detector inteligente que identifica tipo de documento ANTES de evaluar

**Resultado**: Sistema ahora RECHAZA guias y solo evalua trabajos reales

**Estado**: ✓ IMPLEMENTADO Y TESTEADO EXITOSAMENTE

---

**Desarrollado por**: Ing. Jorge Quintero (lucho19q@gmail.com)
**Asistencia**: Claude AI (Anthropic)
**Fecha**: 2025
