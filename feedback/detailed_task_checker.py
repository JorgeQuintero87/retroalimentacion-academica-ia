"""
Verificador Detallado de Tareas
Compara PUNTO POR PUNTO lo que debe hacer el estudiante vs lo que presentó
"""
from openai import OpenAI
import json
import os
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

class DetailedTaskChecker:
    """Verifica que el estudiante haya cumplido CADA tarea específica"""

    def __init__(self):
        """Inicializa el verificador con OpenAI"""
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=self.openai_api_key)
        self.model = "gpt-4o-mini"

    def check_tasks_for_criterion(self, criterion_data: Dict, document_content: str,
                                   condiciones_data: Dict = None) -> Dict:
        """
        Verifica PUNTO POR PUNTO si el estudiante cumplió las tareas

        Args:
            criterion_data: Dict con info del criterio de la rúbrica
            document_content: Contenido del documento del estudiante
            condiciones_data: Dict con las tareas detalladas (opcional)

        Returns:
            Dict con:
            - tasks_found: list (tareas encontradas)
            - tasks_missing: list (tareas faltantes)
            - task_details: list (detalle de cada tarea)
            - completion_percentage: float (% de tareas cumplidas)
            - recommendation: str
        """
        try:
            criterion_num = criterion_data.get('numero', 0)
            criterion_name = criterion_data.get('nombre', '')

            # Buscar las tareas detalladas en condiciones.json
            detailed_tasks = []
            deliverables = []

            if condiciones_data and 'ejercicios' in condiciones_data:
                # Buscar el ejercicio correspondiente
                for ejercicio in condiciones_data['ejercicios']:
                    if ejercicio.get('numero') == criterion_num:
                        # Tareas del ejercicio
                        if 'tareas' in ejercicio:
                            detailed_tasks.extend(ejercicio['tareas'])

                        # Si tiene escenarios (como K-Means)
                        if 'escenarios' in ejercicio:
                            for escenario in ejercicio['escenarios']:
                                if 'tareas' in escenario:
                                    detailed_tasks.extend([
                                        f"[Escenario {escenario['escenario']}] {tarea}"
                                        for tarea in escenario['tareas']
                                    ])

                        # Entregables esperados
                        if 'entregables' in ejercicio:
                            deliverables = ejercicio['entregables']

                        break

            if not detailed_tasks:
                return {
                    'tasks_found': [],
                    'tasks_missing': [],
                    'task_details': [],
                    'completion_percentage': 0,
                    'recommendation': 'No se encontraron tareas detalladas para este criterio'
                }

            # Crear prompt para verificación PUNTO POR PUNTO
            tasks_text = "\n".join([f"{i+1}. {task}" for i, task in enumerate(detailed_tasks)])
            deliverables_text = "\n".join([f"- {d}" for d in deliverables])

            prompt = f"""
Eres un evaluador académico MUY DETALLADO. Tu tarea es verificar PUNTO POR PUNTO si el estudiante cumplió CADA tarea específica.

CRITERIO {criterion_num}: {criterion_name}

TAREAS QUE EL ESTUDIANTE DEBE REALIZAR:
{tasks_text}

ENTREGABLES ESPERADOS:
{deliverables_text}

CONTENIDO DEL DOCUMENTO DEL ESTUDIANTE:
{document_content[:5000]}

INSTRUCCIONES DE VERIFICACIÓN:

Para CADA tarea de la lista:
1. Busca evidencia ESPECÍFICA en el documento
2. Determina si la tarea fue CUMPLIDA, PARCIALMENTE CUMPLIDA o NO CUMPLIDA
3. Extrae la evidencia textual que lo demuestra

CRITERIOS DE VERIFICACIÓN:

**CUMPLIDA**: El estudiante realizó la tarea completa con evidencia clara
- Ejemplo: Si dice "Seleccionar dos variables" → debe mencionar cuáles variables seleccionó
- Ejemplo: Si dice "Calcular Silhouette Score" → debe mostrar el valor obtenido
- Ejemplo: Si dice "Graficar scatterplot" → debe mencionar que generó el gráfico

**PARCIALMENTE CUMPLIDA**: El estudiante mencionó la tarea pero sin completar
- Ejemplo: Menciona variables pero no justifica la selección
- Ejemplo: Menciona métricas pero no muestra valores

**NO CUMPLIDA**: No hay evidencia de que realizó la tarea
- No se menciona en el documento
- No hay código ni análisis relacionado

FORMATO DE RESPUESTA (JSON):
{{
  "task_checks": [
    {{
      "task_number": 1,
      "task_description": "<descripción de la tarea>",
      "status": "cumplida/parcial/no_cumplida",
      "evidence": "<evidencia textual del documento que lo demuestra>",
      "notes": "<notas adicionales>"
    }}
  ],
  "summary": {{
    "total_tasks": <número total>,
    "completed": <número cumplidas>,
    "partial": <número parciales>,
    "not_completed": <número no cumplidas>,
    "completion_percentage": <porcentaje>
  }},
  "recommendation": "<recomendación general>"
}}
"""

            # Llamar a GPT
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un evaluador académico extremadamente detallado que verifica PUNTO POR PUNTO el cumplimiento de tareas específicas."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.2,
                max_tokens=1500,
                response_format={"type": "json_object"}
            )

            # Parsear respuesta
            result = json.loads(response.choices[0].message.content)

            task_checks = result.get('task_checks', [])
            summary = result.get('summary', {})

            # Organizar resultados
            tasks_found = []
            tasks_missing = []
            tasks_partial = []

            for check in task_checks:
                status = check.get('status', 'no_cumplida')
                task_desc = check.get('task_description', '')

                if status == 'cumplida':
                    tasks_found.append(task_desc)
                elif status == 'parcial':
                    tasks_partial.append(task_desc)
                else:
                    tasks_missing.append(task_desc)

            completion_pct = summary.get('completion_percentage', 0)

            # Generar recomendación final
            if completion_pct >= 90:
                recommendation = f"Excelente trabajo. Cumplió {summary.get('completed', 0)}/{summary.get('total_tasks', 0)} tareas."
            elif completion_pct >= 70:
                recommendation = f"Buen trabajo. Cumplió {summary.get('completed', 0)}/{summary.get('total_tasks', 0)} tareas. Revisar tareas faltantes."
            elif completion_pct >= 50:
                recommendation = f"Trabajo incompleto. Solo cumplió {summary.get('completed', 0)}/{summary.get('total_tasks', 0)} tareas. Necesita completar las faltantes."
            else:
                recommendation = f"Trabajo muy incompleto. Cumplió {summary.get('completed', 0)}/{summary.get('total_tasks', 0)} tareas. Debe revisar los requisitos."

            return {
                'tasks_found': tasks_found,
                'tasks_partial': tasks_partial,
                'tasks_missing': tasks_missing,
                'task_details': task_checks,
                'completion_percentage': completion_pct,
                'recommendation': recommendation,
                'summary': summary
            }

        except Exception as e:
            print(f"[ERROR] Error verificando tareas: {e}")
            return {
                'tasks_found': [],
                'tasks_partial': [],
                'tasks_missing': [],
                'task_details': [],
                'completion_percentage': 0,
                'recommendation': f'Error en verificación: {str(e)}'
            }


if __name__ == "__main__":
    # Test del verificador
    print("=" * 80)
    print("TEST Detailed Task Checker")
    print("=" * 80)

    checker = DetailedTaskChecker()

    # Cargar condiciones de Fase 3
    with open('courses/machine_learning_fase3/condiciones.json', 'r', encoding='utf-8') as f:
        condiciones = json.load(f)

    # Documento de ejemplo: TRABAJO COMPLETO
    test_doc_completo = """
    # Ejercicio 1: K-Means Clustering

    ## Escenario 1: Agrupación con 2 variables

    Seleccioné las variables 'edad' e 'ingresos' porque muestran la mayor correlación.

    Determiné que k=4 clusters es adecuado utilizando el método del codo.
    También calculé el Silhouette Score que dio 0.72.

    Generé un scatterplot mostrando las dos variables con los 4 clusters identificados.

    ## Escenario 2: Agrupación con más variables

    Apliqué K-Means con 5 variables: edad, ingresos, gasto, educación, hijos.

    El método del codo confirma k=4 como óptimo.
    El Silhouette Score mejoró a 0.81 (mejora del 12.5%).

    El Escenario 2 es mejor porque tiene mayor Silhouette Score.

    Perfiles de clusters:
    - Cluster 0: Jóvenes de bajos ingresos, sin hijos
    - Cluster 1: Adultos de ingresos medios, 1-2 hijos
    - Cluster 2: Adultos mayores de altos ingresos
    - Cluster 3: Profesionales jóvenes
    """

    # Documento de ejemplo: TRABAJO INCOMPLETO
    test_doc_incompleto = """
    # Ejercicio 1: K-Means Clustering

    ## Escenario 1

    Seleccioné edad e ingresos.
    Usé k=4.

    ## Escenario 2

    Usé más variables.
    """

    # Criterio 1 (K-Means)
    criterion = {
        'numero': 1,
        'nombre': 'Aplica modelo no supervisado K-means',
        'puntaje_maximo': 60
    }

    print("\n" + "=" * 80)
    print("TEST 1: Documento COMPLETO")
    print("=" * 80)

    result1 = checker.check_tasks_for_criterion(criterion, test_doc_completo, condiciones)

    print(f"\nRESULTADO:")
    print(f"  Completion: {result1['completion_percentage']}%")
    print(f"  Tareas cumplidas: {len(result1['tasks_found'])}")
    print(f"  Tareas parciales: {len(result1['tasks_partial'])}")
    print(f"  Tareas faltantes: {len(result1['tasks_missing'])}")
    print(f"\n  Recomendacion: {result1['recommendation']}")

    print(f"\n  DETALLE:")
    for detail in result1['task_details'][:3]:
        print(f"\n    Tarea {detail['task_number']}: {detail['task_description'][:60]}...")
        print(f"      Status: {detail['status']}")
        print(f"      Evidencia: {detail['evidence'][:100]}...")

    print("\n" + "=" * 80)
    print("TEST 2: Documento INCOMPLETO")
    print("=" * 80)

    result2 = checker.check_tasks_for_criterion(criterion, test_doc_incompleto, condiciones)

    print(f"\nRESULTADO:")
    print(f"  Completion: {result2['completion_percentage']}%")
    print(f"  Tareas cumplidas: {len(result2['tasks_found'])}")
    print(f"  Tareas parciales: {len(result2['tasks_partial'])}")
    print(f"  Tareas faltantes: {len(result2['tasks_missing'])}")
    print(f"\n  Recomendacion: {result2['recommendation']}")

    print(f"\n  TAREAS FALTANTES:")
    for task in result2['tasks_missing'][:5]:
        print(f"    - {task}")
