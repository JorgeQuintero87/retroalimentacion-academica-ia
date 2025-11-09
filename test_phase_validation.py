"""
Test de Validación de Fase
Verifica que el PhaseValidator detecta correctamente documentos de fases incorrectas
"""
import json
from feedback.phase_validator import PhaseValidator

# Cargar rúbrica de Fase 3 (Clustering)
with open('courses/machine_learning_fase3/rubrica_estructurada.json', 'r', encoding='utf-8') as f:
    rubric_fase3 = json.load(f)

# Documento de FASE 2 (Regresión y Clasificación) - DEBE SER RECHAZADO
documento_fase2 = """
# Machine Learning - Fase 2

## Ejercicio 1: Carga y contextualización de datasets

He seleccionado el dataset de enfermedad hepática (liver-disorders ID:8).
Este dataset contiene 345 registros con variables médicas.

Variables objetivo: hepatomegalia
Variables predictoras: edad, género, enzimas hepáticas, consumo de alcohol

## Ejercicio 2: Modelos de Regresión

Implementé 4 modelos de regresión:
1. Regresión Lineal
2. Ridge Regression
3. Lasso Regression
4. Árbol de Decisión para Regresión

División de datos: 75% entrenamiento, 25% prueba

Métricas obtenidas:
- MAE (Error Absoluto Medio): 2.34
- MSE (Error Cuadrático Medio): 8.12
- RMSE (Raíz del Error Cuadrático Medio): 2.85
- R² (Coeficiente de Determinación): 0.78

Mejor modelo: Ridge Regression con R² = 0.82

## Ejercicio 3: Modelos de Clasificación

Implementé 4 modelos de clasificación:
1. Regresión Logística
2. Árbol de Decisión
3. K-Nearest Neighbors (KNN)
4. Perceptrón

División de datos: 70% entrenamiento, 30% prueba

Métricas obtenidas:
- Accuracy: 0.85
- Precision: 0.83
- Recall: 0.87
- F1-score: 0.85

Matriz de confusión:
[[45, 5],
 [8, 42]]

Mejor modelo: Árbol de Decisión con Accuracy = 0.87
"""

# Documento de FASE 3 (Clustering) - DEBE SER ACEPTADO
documento_fase3 = """
# Machine Learning - Fase 3: Clustering

## Ejercicio 1: K-Means Clustering

### Escenario 1: Agrupación con 2 variables
Seleccioné las variables 'edad' e 'ingresos' como las más relevantes.

Utilizando el método del codo, determiné que k=4 clusters es óptimo.
El Silhouette Score es 0.72, lo cual indica buena separación de clusters.

Scatterplot generado mostrando los 4 clusters claramente diferenciados.

### Escenario 2: Agrupación con más variables
Apliqué K-Means con 5 variables: edad, ingresos, gasto, educación, hijos.

El Silhouette Score mejoró a 0.81, indicando mejor separación.
El método del codo confirma k=4 como óptimo.

Perfiles de clusters del mejor modelo:
- Cluster 0: Jóvenes de bajos ingresos, sin hijos
- Cluster 1: Adultos de ingresos medios, 1-2 hijos
- Cluster 2: Adultos mayores de altos ingresos
- Cluster 3: Adultos jóvenes profesionales

## Ejercicio 2: DBSCAN

Variables seleccionadas: edad, ingresos, educación

Parámetros determinados:
- epsilon (ϵ) = 0.5
- min_samples = 5

Se identificaron 3 clusters y 12 puntos de ruido.

Perfiles de clusters:
- Cluster 0: Grupo homogéneo de ingresos medios
- Cluster 1: Profesionales de altos ingresos
- Cluster 2: Adultos mayores pensionados

## Ejercicio 3: Agglomerative Clustering

Variables seleccionadas: edad, ingresos, educación, gasto
Razón: Estas variables muestran alta correlación y permiten identificar patrones de consumo.

Dendrograma generado.
Según el dendrograma, el número óptimo es 4 clusters (punto de corte en distancia 15).

Perfiles de clusters:
- Cluster 0: Jóvenes estudiantes
- Cluster 1: Adultos trabajadores
- Cluster 2: Profesionales senior
- Cluster 3: Adultos mayores retirados
"""

def test_validation():
    """Prueba la validación de fase"""
    validator = PhaseValidator()

    print("=" * 80)
    print("TEST 1: Documento de FASE 2 contra Rúbrica de FASE 3")
    print("       RESULTADO ESPERADO: is_valid = False")
    print("=" * 80)

    result1 = validator.validate_document_phase(documento_fase2, rubric_fase3)

    print(f"\n[OK] Resultado:")
    print(f"  - is_valid: {result1['is_valid']}")
    print(f"  - confidence: {result1['confidence']}")
    print(f"  - phase_mismatch: {result1['phase_mismatch']}")
    print(f"  - recommendation: {result1['recommendation']}")
    print(f"\n  Temas esperados (Fase 3):")
    for topic in result1['expected_topics'][:5]:
        print(f"    - {topic}")
    print(f"\n  Temas encontrados en documento:")
    for topic in result1['found_topics']:
        print(f"    - {topic}")
    print(f"\n  Explicacion: {result1['explanation']}")

    print("\n" + "=" * 80)
    print("TEST 2: Documento de FASE 3 contra Rubrica de FASE 3")
    print("       RESULTADO ESPERADO: is_valid = True")
    print("=" * 80)

    result2 = validator.validate_document_phase(documento_fase3, rubric_fase3)

    print(f"\n[OK] Resultado:")
    print(f"  - is_valid: {result2['is_valid']}")
    print(f"  - confidence: {result2['confidence']}")
    print(f"  - phase_mismatch: {result2['phase_mismatch']}")
    print(f"  - recommendation: {result2['recommendation']}")
    print(f"\n  Temas esperados (Fase 3):")
    for topic in result2['expected_topics'][:5]:
        print(f"    - {topic}")
    print(f"\n  Temas encontrados en documento:")
    for topic in result2['found_topics']:
        print(f"    - {topic}")
    print(f"\n  Explicacion: {result2['explanation']}")

    print("\n" + "=" * 80)
    print("RESUMEN DE TESTS")
    print("=" * 80)

    test1_pass = not result1['is_valid']  # Debe ser False (rechazar)
    test2_pass = result2['is_valid']      # Debe ser True (aceptar)

    print(f"\n[OK] TEST 1 (Rechazar Fase 2): {'[PASS]' if test1_pass else '[FAIL]'}")
    print(f"[OK] TEST 2 (Aceptar Fase 3): {'[PASS]' if test2_pass else '[FAIL]'}")

    if test1_pass and test2_pass:
        print("\n[SUCCESS] TODOS LOS TESTS PASARON - El validador funciona correctamente")
    else:
        print("\n[WARNING] ALGUNOS TESTS FALLARON - Revisar configuracion del validador")

if __name__ == "__main__":
    test_validation()
