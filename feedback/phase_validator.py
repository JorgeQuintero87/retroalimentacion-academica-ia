"""
Validador de Fase para Evitar Evaluaciones Incorrectas
Verifica que el documento corresponda a la fase seleccionada
"""
from openai import OpenAI
import json
import os
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

class PhaseValidator:
    """Valida que un documento corresponda a la fase correcta antes de evaluar"""

    def __init__(self):
        """Inicializa el validador con OpenAI"""
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=self.openai_api_key)
        self.model = "gpt-4o-mini"

    def validate_document_phase(self, document_content: str, rubric_data: Dict) -> Dict:
        """
        Valida que el documento corresponda a la fase indicada en la rúbrica

        Args:
            document_content: Contenido del documento a evaluar
            rubric_data: Datos de la rúbrica (contiene nombre_curso, fase, criterios)

        Returns:
            Dict con:
            - is_valid: bool (True si corresponde a la fase)
            - confidence: str (alta/media/baja)
            - expected_topics: list (temas esperados)
            - found_topics: list (temas encontrados)
            - recommendation: str (mensaje para el usuario)
        """
        try:
            course_name = rubric_data.get('nombre_curso', 'Unknown')
            phase = rubric_data.get('fase', '')

            # Extraer temas clave de la rúbrica
            expected_topics = self._extract_expected_topics(rubric_data)

            # Preparar prompt para validación
            prompt = f"""
Eres un validador académico experto. Tu tarea es determinar si un documento corresponde a la fase correcta del curso.

CURSO: {course_name}
FASE ESPERADA: {phase}

TEMAS QUE DEBE CONTENER LA FASE:
{chr(10).join([f"- {topic}" for topic in expected_topics])}

CONTENIDO DEL DOCUMENTO (primeros 3000 caracteres):
{document_content[:3000]}

ANÁLISIS REQUERIDO:
1. Identifica los temas principales que trata el documento
2. Compara con los temas esperados de la fase
3. Determina si hay correspondencia clara

INSTRUCCIONES:
- Si el documento trata PRINCIPALMENTE los temas de la fase → is_valid: true
- Si el documento trata temas de OTRA fase → is_valid: false
- Si no estás seguro → confianza: "baja"

FORMATO DE RESPUESTA (JSON):
{{
  "is_valid": true/false,
  "confidence": "alta/media/baja",
  "expected_topics_found": ["<tema esperado 1>", "<tema esperado 2>"],
  "actual_topics_found": ["<tema real 1>", "<tema real 2>"],
  "phase_mismatch": "<nombre de la fase si es diferente, o null>",
  "explanation": "<explicación breve de por qué sí o no corresponde>"
}}
"""

            # Llamar a GPT
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un validador académico preciso que determina si un documento corresponde a la fase correcta de un curso."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,  # Más determinístico
                max_tokens=400,
                response_format={"type": "json_object"}
            )

            # Parsear respuesta
            result = json.loads(response.choices[0].message.content)

            is_valid = result.get('is_valid', False)
            confidence = result.get('confidence', 'baja')
            phase_mismatch = result.get('phase_mismatch')
            explanation = result.get('explanation', '')

            # Generar recomendación
            if is_valid:
                recommendation = f"[OK] El documento corresponde a {phase}. Puede procederse con la evaluacion."
            else:
                if phase_mismatch:
                    recommendation = f"[ADVERTENCIA] Este documento parece corresponder a '{phase_mismatch}', no a '{phase}'. Por favor, selecciona la fase correcta antes de evaluar."
                else:
                    recommendation = f"[ADVERTENCIA] Este documento NO corresponde claramente a '{phase}'. Verifica que hayas seleccionado la fase correcta."

            return {
                'is_valid': is_valid,
                'confidence': confidence,
                'expected_topics': expected_topics,
                'found_topics': result.get('actual_topics_found', []),
                'phase_mismatch': phase_mismatch,
                'explanation': explanation,
                'recommendation': recommendation
            }

        except Exception as e:
            print(f"[WARNING] Error validando fase del documento: {e}")
            # En caso de error, permitir evaluación (modo permisivo)
            return {
                'is_valid': True,
                'confidence': 'baja',
                'expected_topics': [],
                'found_topics': [],
                'phase_mismatch': None,
                'explanation': f'Error en validacion: {str(e)}',
                'recommendation': '[WARNING] No se pudo validar la fase. Proceda con precaucion.'
            }

    def _extract_expected_topics(self, rubric_data: Dict) -> list:
        """
        Extrae los temas clave esperados de la rúbrica

        Args:
            rubric_data: Datos de la rúbrica

        Returns:
            Lista de temas clave esperados
        """
        topics = []

        # Extraer de nombre del curso y fase
        course_name = rubric_data.get('nombre_curso', '')
        phase = rubric_data.get('fase', '')

        # Detectar temas específicos según el nombre
        if 'Fase 2' in course_name or 'Fase 2' in phase:
            topics.extend([
                'Modelos de regresión (Linear, Ridge, Lasso, Árbol)',
                'Modelos de clasificación (Regresión Logística, Árbol, KNN, Perceptrón)',
                'Métricas: MAE, MSE, RMSE, R² (regresión)',
                'Métricas: Accuracy, Precision, Recall, F1-score (clasificación)',
                'Matriz de confusión',
                'División de datos (train/test split)',
                'Comparación de modelos'
            ])
        elif 'Fase 3' in course_name or 'Fase 3' in phase:
            topics.extend([
                'Algoritmo K-Means Clustering',
                'Método del codo (elbow method)',
                'Silhouette Score',
                'Algoritmo DBSCAN',
                'Parámetro epsilon (ϵ)',
                'Parámetro min_samples',
                'Agglomerative Clustering',
                'Dendrogramas',
                'Perfiles de clusters',
                'Agrupamiento no supervisado',
                'Clustering'
            ])

        # Extraer de criterios de evaluación
        if 'criterios_evaluacion' in rubric_data:
            for criterion in rubric_data['criterios_evaluacion']:
                criterion_name = criterion.get('nombre', '')
                topics.append(criterion_name)

        # Limpiar duplicados y devolver
        return list(set(topics))


# Función de utilidad para uso rápido
def validate_phase_quick(document_content: str, rubric_data: Dict) -> tuple:
    """
    Validación rápida de fase

    Returns:
        (is_valid: bool, message: str)
    """
    validator = PhaseValidator()
    result = validator.validate_document_phase(document_content, rubric_data)
    return result['is_valid'], result['recommendation']


if __name__ == "__main__":
    # Test del validador
    print("=== Test Phase Validator ===\n")

    validator = PhaseValidator()

    # Documento de ejemplo (Fase 3 - Clustering)
    test_doc_fase3 = """
    # Ejercicio 1: K-Means Clustering

    ## Escenario 1: Agrupación con 2 variables
    Seleccioné las variables 'edad' y 'ingresos' como las más relevantes.
    Utilizando el método del codo, determiné que k=4 clusters es óptimo.
    El Silhouette Score es 0.72, lo cual indica buena separación.

    ## Escenario 2: Agrupación con más variables
    Apliqué K-Means con 5 variables: edad, ingresos, gasto, educación, hijos.
    El Silhouette Score mejoró a 0.81.

    # Ejercicio 2: DBSCAN
    Parámetros seleccionados:
    - epsilon (ϵ) = 0.5
    - min_samples = 5
    Se identificaron 3 clusters y 12 puntos de ruido.

    # Ejercicio 3: Agglomerative Clustering
    Variables seleccionadas: edad, ingresos, educación, gasto
    Según el dendrograma, el número óptimo es 4 clusters.
    """

    # Rúbrica de Fase 3
    rubric_fase3 = {
        "nombre_curso": "Machine Learning - Fase 3",
        "fase": "Fase 3 - Clustering",
        "criterios_evaluacion": [
            {"numero": 1, "nombre": "K-Means Clustering"},
            {"numero": 2, "nombre": "DBSCAN"},
            {"numero": 3, "nombre": "Agglomerative Clustering"}
        ]
    }

    result = validator.validate_document_phase(test_doc_fase3, rubric_fase3)

    print(f"Is Valid: {result['is_valid']}")
    print(f"Confidence: {result['confidence']}")
    print(f"Expected Topics: {result['expected_topics'][:3]}")
    print(f"Found Topics: {result['found_topics']}")
    print(f"Recommendation: {result['recommendation']}")
