"""
Validador de Tipo de Documento
Detecta si el documento es una guia/instrucciones o una entrega real del estudiante
"""
from openai import OpenAI
import json
import os
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

class DocumentTypeValidator:
    """Valida que el documento sea una entrega real, no una guia de actividad"""

    def __init__(self):
        """Inicializa el validador con OpenAI"""
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=self.openai_api_key)
        self.model = "gpt-4o-mini"

    def validate_is_student_work(self, document_content: str) -> Dict:
        """
        Valida que el documento sea trabajo del estudiante, NO una guia

        Args:
            document_content: Contenido del documento a evaluar

        Returns:
            Dict con:
            - is_student_work: bool (True si es trabajo del estudiante)
            - confidence: str (alta/media/baja)
            - document_type: str (guia_actividad, entrega_estudiante, indeterminado)
            - evidence: list (evidencias que indican el tipo)
            - recommendation: str (mensaje para el usuario)
        """
        try:
            # Preparar prompt para deteccion
            prompt = f"""
Eres un detector academico experto. Tu tarea es determinar si un documento es:
A) Una GUIA/INSTRUCCIONES de actividad (documento que indica QUE DEBE HACER el estudiante)
B) Una ENTREGA REAL de un estudiante (documento con SOLUCION y trabajo desarrollado)

CONTENIDO DEL DOCUMENTO (primeros 4000 caracteres):
{document_content[:4000]}

INDICADORES DE GUIA/INSTRUCCIONES:
- Frases como: "El estudiante debe", "Usted debe", "Se requiere que"
- Instrucciones imperativas: "Realice", "Desarrolle", "Implemente", "Calcule"
- Descripciones de actividades a realizar
- Rubricas de evaluacion con puntajes
- Criterios de entrega
- Formato: "Ejercicio 1: [descripcion de lo que debe hacer]"
- Tablas con criterios de calificacion
- Frases como: "Esta actividad consiste en", "El objetivo es que el estudiante"
- Puntajes maximos y minimos por criterio
- Niveles de desempeno (alto, medio, bajo)

INDICADORES DE TRABAJO REAL DEL ESTUDIANTE:
- Codigo fuente ejecutable (import pandas, import sklearn, etc.)
- Resultados numericos especificos (ej: "RMSE: 2.34", "Accuracy: 0.85")
- Graficos y visualizaciones descritos o insertados
- Analisis y conclusiones en primera persona
- Datasets especificos cargados (ej: "liver-disorders.csv")
- Outputs de modelos (metricas reales, no teoricas)
- Interpretaciones personales del estudiante
- Evidencias de ejecucion de codigo

ANALISIS REQUERIDO:
1. Identifica el tipo de documento segun los indicadores
2. Busca evidencias claras de cada tipo
3. Determina la confianza de tu clasificacion

INSTRUCCIONES:
- Si el documento contiene PRINCIPALMENTE instrucciones → document_type: "guia_actividad"
- Si el documento contiene PRINCIPALMENTE trabajo desarrollado → document_type: "entrega_estudiante"
- Si no estas seguro → document_type: "indeterminado"

FORMATO DE RESPUESTA (JSON):
{{
  "document_type": "guia_actividad/entrega_estudiante/indeterminado",
  "confidence": "alta/media/baja",
  "evidence_guide": ["<evidencia 1 de que es guia>", "<evidencia 2>"],
  "evidence_student_work": ["<evidencia 1 de que es trabajo>", "<evidencia 2>"],
  "explanation": "<explicacion breve de la clasificacion>"
}}
"""

            # Llamar a GPT
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un detector academico preciso que distingue entre guias de actividad y entregas de estudiantes."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,  # Mas deterministico
                max_tokens=500,
                response_format={"type": "json_object"}
            )

            # Parsear respuesta
            result = json.loads(response.choices[0].message.content)

            document_type = result.get('document_type', 'indeterminado')
            confidence = result.get('confidence', 'baja')
            evidence_guide = result.get('evidence_guide', [])
            evidence_student = result.get('evidence_student_work', [])
            explanation = result.get('explanation', '')

            # Determinar si es trabajo del estudiante
            is_student_work = (document_type == 'entrega_estudiante')

            # Generar recomendacion
            if is_student_work:
                recommendation = "[OK] Este documento parece ser una entrega real del estudiante. Puede procederse con la evaluacion."
            else:
                if document_type == 'guia_actividad':
                    recommendation = "[ADVERTENCIA] Este documento parece ser una GUIA/INSTRUCCIONES de actividad, NO una entrega del estudiante. No debe ser calificado."
                else:
                    recommendation = "[ADVERTENCIA] No se pudo determinar con certeza el tipo de documento. Verifique que sea una entrega real del estudiante."

            return {
                'is_student_work': is_student_work,
                'confidence': confidence,
                'document_type': document_type,
                'evidence_guide': evidence_guide,
                'evidence_student_work': evidence_student,
                'explanation': explanation,
                'recommendation': recommendation
            }

        except Exception as e:
            print(f"[WARNING] Error validando tipo de documento: {e}")
            # En caso de error, PERMITIR (modo permisivo para no bloquear entregas validas)
            return {
                'is_student_work': True,  # Asumir que es trabajo del estudiante
                'confidence': 'baja',
                'document_type': 'indeterminado',
                'evidence_guide': [],
                'evidence_student_work': [],
                'explanation': f'Error en validacion: {str(e)}',
                'recommendation': '[WARNING] No se pudo validar el tipo de documento. Proceda con precaucion.'
            }


# Funcion de utilidad para uso rapido
def validate_document_quick(document_content: str) -> tuple:
    """
    Validacion rapida de tipo de documento

    Returns:
        (is_student_work: bool, message: str)
    """
    validator = DocumentTypeValidator()
    result = validator.validate_is_student_work(document_content)
    return result['is_student_work'], result['recommendation']


if __name__ == "__main__":
    # Test del validador
    print("=" * 80)
    print("TEST Document Type Validator")
    print("=" * 80)

    validator = DocumentTypeValidator()

    # Documento de ejemplo: GUIA DE ACTIVIDAD
    test_guia = """
    # Fase 3 - Componente Practico - Algoritmos No Supervisados

    ## Ejercicio 1: K-Means Clustering (60 puntos)

    El estudiante debe aplicar el algoritmo K-Means en dos escenarios:

    ### Escenario 1: Agrupacion con dos variables
    - Seleccione dos variables numericas consideradas mas relevantes
    - Determine cuantos clusters (k) serian adecuados
    - Establezca los criterios utilizados (metodo del codo, Silhouette Score)
    - Grafique un scatterplot identificando los clusters

    ### Escenario 2: Agrupacion con mas variables
    - Aplique K-Means incrementando el numero de variables
    - Verifique si mejora la agrupacion
    - Determine el perfil caracteristico de cada cluster

    ## Rubrica de Evaluacion

    | Nivel | Puntaje | Descripcion |
    |-------|---------|-------------|
    | Alto  | 51-60   | Aplica correctamente K-means, justifica numero de clusters |
    | Medio | 42-50   | Aplica K-means con dificultades menores |
    | Bajo  | 1-41    | Aplicacion incorrecta o confusa |

    ## Ejercicio 2: DBSCAN (60 puntos)

    El estudiante debe aplicar el algoritmo DBSCAN:
    - Seleccione tres variables numericas
    - Determine el valor de epsilon apropiado
    - Determine el valor de min_samples
    - Identifique el numero de clusters y puntos de ruido
    """

    # Documento de ejemplo: TRABAJO REAL DEL ESTUDIANTE
    test_trabajo = """
    # Machine Learning - Fase 3
    ## Estudiante: Juan Perez

    ## Ejercicio 1: K-Means Clustering

    ### Carga de datos
    ```python
    import pandas as pd
    from sklearn.cluster import KMeans
    import matplotlib.pyplot as plt

    df = pd.read_csv('customers.csv')
    print(df.head())
    ```

    ### Escenario 1: Clustering con 2 variables
    Seleccione las variables 'edad' e 'ingresos' porque muestran mayor correlacion.

    Aplicando el metodo del codo, determine que k=4 es optimo.
    El Silhouette Score obtenido es 0.72.

    ### Resultados
    - Cluster 0: 45 clientes - Jovenes de bajos ingresos
    - Cluster 1: 62 clientes - Adultos de ingresos medios
    - Cluster 2: 38 clientes - Adultos mayores de altos ingresos
    - Cluster 3: 55 clientes - Profesionales jovenes

    ### Escenario 2: Clustering con 5 variables
    Variables: edad, ingresos, gasto, educacion, hijos

    Metricas obtenidas:
    - Silhouette Score: 0.81 (mejora del 12.5% respecto al Escenario 1)
    - Inercia: 1250.34

    Conclusion: El Escenario 2 es mejor porque tiene mayor Silhouette Score.

    ## Ejercicio 2: DBSCAN

    Parametros seleccionados:
    - epsilon = 0.5
    - min_samples = 5

    Resultados:
    - 3 clusters identificados
    - 12 puntos de ruido (outliers)

    Perfiles:
    - Cluster 0: Grupo homogeneo de ingresos medios (85 clientes)
    - Cluster 1: Profesionales de altos ingresos (42 clientes)
    - Cluster 2: Adultos mayores pensionados (31 clientes)
    """

    print("\n" + "=" * 80)
    print("TEST 1: Documento que es GUIA DE ACTIVIDAD")
    print("=" * 80)

    result1 = validator.validate_is_student_work(test_guia)

    print(f"\nResultado:")
    print(f"  - is_student_work: {result1['is_student_work']}")
    print(f"  - document_type: {result1['document_type']}")
    print(f"  - confidence: {result1['confidence']}")
    print(f"  - recommendation: {result1['recommendation']}")
    print(f"\n  Evidencias de que es GUIA:")
    for ev in result1['evidence_guide'][:3]:
        print(f"    - {ev}")
    print(f"\n  Evidencias de que es TRABAJO:")
    for ev in result1['evidence_student_work'][:3]:
        print(f"    - {ev}")

    print("\n" + "=" * 80)
    print("TEST 2: Documento que es TRABAJO REAL DEL ESTUDIANTE")
    print("=" * 80)

    result2 = validator.validate_is_student_work(test_trabajo)

    print(f"\nResultado:")
    print(f"  - is_student_work: {result2['is_student_work']}")
    print(f"  - document_type: {result2['document_type']}")
    print(f"  - confidence: {result2['confidence']}")
    print(f"  - recommendation: {result2['recommendation']}")
    print(f"\n  Evidencias de que es GUIA:")
    for ev in result2['evidence_guide'][:3]:
        print(f"    - {ev}")
    print(f"\n  Evidencias de que es TRABAJO:")
    for ev in result2['evidence_student_work'][:3]:
        print(f"    - {ev}")

    print("\n" + "=" * 80)
    print("RESUMEN")
    print("=" * 80)

    test1_pass = (not result1['is_student_work'] and result1['document_type'] == 'guia_actividad')
    test2_pass = (result2['is_student_work'] and result2['document_type'] == 'entrega_estudiante')

    print(f"\nTEST 1 (Rechazar GUIA): {'[PASS]' if test1_pass else '[FAIL]'}")
    print(f"TEST 2 (Aceptar TRABAJO): {'[PASS]' if test2_pass else '[FAIL]'}")

    if test1_pass and test2_pass:
        print("\n[SUCCESS] Validador funciona correctamente")
    else:
        print("\n[WARNING] Revisar validador")
