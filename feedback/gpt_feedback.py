"""
Sistema de Retroalimentación con GPT
Genera feedback automático comparando documentos con rúbricas
"""
from openai import OpenAI
import json
import os
from typing import Dict, List
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

class GPTFeedbackGenerator:
    """Genera retroalimentación académica usando GPT-4"""

    def __init__(self):
        """Inicializa el cliente de OpenAI"""
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.client = OpenAI(api_key=self.openai_api_key)
        self.model = "gpt-4o-mini"  # Opciones: gpt-4o-mini (barato), gpt-4o (mejor calidad)
        self.condiciones_cache = {}  # Cache para condiciones.json

    def generate_criterion_feedback(self, criterion: Dict, document_content: str,
                                    course_name: str, detected_criterion: int = None,
                                    exercises_in_document: list = None, condiciones: Dict = None) -> Dict:
        """
        Genera retroalimentación para un criterio específico (NUEVA ESTRUCTURA)
        ACTUALIZADO: Primero verifica si el criterio está presente en el documento

        Args:
            criterion: Dict con estructura del criterio (numero, nombre, niveles, etc.)
            document_content: Contenido del documento del estudiante
            course_name: Nombre del curso
            detected_criterion: Número del criterio detectado desde el nombre del archivo (opcional)
            exercises_in_document: Lista de ejercicios detectados en el documento (opcional)

        Returns:
            Dict con feedback, puntaje y nivel alcanzado (o no_presentado si no aplica)
        """
        try:
            # Extraer información del criterio
            criterion_number = criterion['numero']
            criterion_name = criterion['nombre']
            max_score = criterion['puntaje_maximo']
            levels = criterion.get('niveles', [])

            # Usar ejercicios pasados o detectarlos
            if exercises_in_document is None:
                exercises_in_doc = self._detect_exercises_in_document(document_content)
            else:
                exercises_in_doc = exercises_in_document

            print(f"  [EJERCICIOS] Evaluando con ejercicios detectados: {exercises_in_doc}")

            # NUEVA VALIDACIÓN: Verificar si el criterio está presente en el documento
            # El nombre del archivo es solo una PISTA, NO es definitivo
            is_present = self._is_criterion_present(
                criterion,
                document_content,
                detected_criterion  # Pasar como pista
            )

            if not is_present:
                return {
                    'success': True,
                    'criterion_number': criterion_number,
                    'criterion_name': criterion_name,
                    'max_score': max_score,
                    'score': 0,
                    'level_achieved': 'no_presentado',
                    'feedback': f'No se encontró evidencia de este criterio en el documento. El estudiante no presentó trabajo relacionado con: {criterion_name}.',
                    'aspects_met': [],
                    'improvements': [
                        f'Incluir evidencia clara de {criterion_name.lower()}',
                        'Asegurarse de cumplir con todos los requisitos de la rúbrica'
                    ]
                }

            # Construir texto de niveles
            levels_text = ""
            for level in levels:
                levels_text += f"\n{level['nivel'].upper()} ({level['puntaje_minimo']}-{level['puntaje_maximo']} pts): {level['descripcion'][:200]}"

            # Información de ejercicios detectados
            exercises_info = ""
            if len(exercises_in_doc) > 0:
                exercises_info = f"\n\n[WARN] EJERCICIOS DETECTADOS EN EL DOCUMENTO: {exercises_in_doc}\nEsto significa que el estudiante menciona explícitamente estos ejercicios."

            # NUEVO: Obtener tareas detalladas si existen condiciones
            detailed_tasks_info = ""
            if condiciones:
                task_details = self._get_detailed_tasks_for_criterion(criterion_number, condiciones)
                tasks = task_details.get('tasks', [])
                deliverables = task_details.get('deliverables', [])

                if tasks:
                    tasks_text = "\n".join([f"  {i+1}. {task}" for i, task in enumerate(tasks)])
                    detailed_tasks_info += f"\n\n📋 TAREAS ESPECÍFICAS QUE EL ESTUDIANTE DEBE REALIZAR:\n{tasks_text}"

                if deliverables:
                    deliverables_text = "\n".join([f"  - {d}" for d in deliverables])
                    detailed_tasks_info += f"\n\n📦 ENTREGABLES ESPERADOS:\n{deliverables_text}"

                if tasks or deliverables:
                    detailed_tasks_info += "\n\n[WARN] IMPORTANTE: Verifica PUNTO POR PUNTO si el estudiante cumplió CADA tarea y entregó CADA entregable."

            # Detectar el tipo de criterio para dar instrucciones específicas
            criterion_type_hint = ""
            if 'dbscan' in criterion_name.lower():
                criterion_type_hint = "\n\n**IMPORTANTE**: Este criterio evalúa DBSCAN (clustering basado en densidad), NO K-Means ni otros algoritmos. Busca específicamente: DBSCAN(), eps, min_samples, outliers, noise."
            elif 'k-mean' in criterion_name.lower() or 'kmean' in criterion_name.lower():
                criterion_type_hint = "\n\n**IMPORTANTE**: Este criterio evalúa K-Means, NO DBSCAN ni otros algoritmos. Busca específicamente: KMeans(), n_clusters, inertia, elbow, silhouette."
            elif 'agglomerative' in criterion_name.lower():
                criterion_type_hint = "\n\n**IMPORTANTE**: Este criterio evalúa Agglomerative Clustering (jerárquico), NO K-Means ni DBSCAN. Busca específicamente: AgglomerativeClustering(), dendrogram, linkage."

            # Construir prompt para GPT
            prompt = f"""
Eres un profesor experto y motivador en {course_name}. Evalúa el siguiente criterio de un trabajo estudiantil con un tono cercano, profesional y constructivo.

CRITERIO {criterion_number}: {criterion_name}
Puntaje máximo: {max_score} puntos
{criterion_type_hint}

NIVELES DE DESEMPEÑO:
{levels_text}
{detailed_tasks_info}

CONTENIDO DEL DOCUMENTO:
{document_content[:30000]}
{exercises_info}

INSTRUCCIONES PARA GENERAR FEEDBACK:

1. **Verificación PUNTO POR PUNTO (SI HAY TAREAS ESPECÍFICAS)**:
   - Revisa CADA tarea de la lista de "TAREAS ESPECÍFICAS"
   - Para CADA tarea, determina si fue CUMPLIDA, PARCIALMENTE CUMPLIDA o NO CUMPLIDA
   - Busca evidencia CONCRETA en el documento (código, métricas, gráficos, análisis)
   - Menciona EN EL FEEDBACK cuáles tareas cumplió y cuáles no
   - El puntaje debe reflejar el % de tareas cumplidas alineado con los NIVELES DE DESEMPEÑO

2. **Tono y Estilo**:
   - Usa un tono cercano y motivador (ej: "Excelente trabajo", "Tu implementación demuestra...", "Se observa que...")
   - Sé específico con los datasets, métricas y técnicas que usó el estudiante
   - Menciona IDs de datasets si los encuentras (ej: "liver-disorders (ID:8)")
   - Reconoce los logros primero, luego sugiere mejoras

3. **Detección de Ejercicios**:
   - Busca menciones literales: "Ejercicio 1", "Ejercicio 2", "Ejercicio 3", etc.
   - Si solo presentó ALGUNOS ejercicios -> Puntaje PROPORCIONAL
   - Menciona EXACTAMENTE cuáles ejercicios presentó

3. **Estructura del Feedback** (según el criterio - ADAPTABLE):

   Identifica qué tipo de criterio es basándote en su nombre/descripción:

   **Si el criterio menciona "carga", "datos", "dataset", "contextualización"**:
   - Menciona si explicó el propósito/contexto de los datasets
   - Verifica si identificó correctamente variables relevantes
   - Revisa si especificó características de los datos

   **Si el criterio menciona "regresión"**:
   - Menciona qué modelos implementó (Lineal, Ridge, Lasso, Árbol, etc.)
   - Verifica división de datos
   - Revisa cálculo de métricas (MAE, MSE, RMSE, R²)
   - Menciona si comparó modelos

   **Si el criterio menciona "clasificación"**:
   - Menciona qué modelos implementó (Regresión Logística, Árbol, KNN, Perceptrón, etc.)
   - Verifica división de datos
   - Revisa cálculo de métricas (Accuracy, Precision, Recall, F1-score)
   - Verifica matriz de confusión

   **Si el criterio menciona "K-Means" o "k-means"**:
   - Verifica aplicación en escenarios (2 variables y más variables)
   - Revisa método del codo y/o Silhouette Score
   - Evalúa gráficos (scatterplot)
   - Verifica descripción de perfiles de clusters
   - Revisa respuestas a interrogantes

   **Si el criterio menciona "DBSCAN" o "dbscan"**:
   - Verifica correcta aplicación con variables numéricas
   - Revisa justificación de parámetros epsilon (ϵ) y min_samples
   - Verifica identificación de clusters y puntos de ruido
   - Evalúa descripción de perfiles de clusters
   - Revisa respuestas a interrogantes

   **Si el criterio menciona "Agglomerative" o "jerárquico" o "hierarchical"**:
   - Verifica selección y justificación de variables
   - Revisa uso de dendrogramas
   - Evalúa determinación del número óptimo de clusters
   - Verifica descripción de perfiles de clusters

   **Si el criterio menciona "foro", "participación", "feedback", "retroalimentación"**:
   - Menciona si adjuntó screenshot del foro
   - Evalúa calidad del feedback (constructivo, respetuoso, argumentado)
   - Verifica publicación de ejercicios

   **Si el criterio menciona "formato", "entrega", "documento"**:
   - Evalúa estructura, organización, claridad
   - Verifica nombre de archivo correcto
   - Revisa cumplimiento de requisitos de entrega

4. **Ejemplos de Feedback Esperado**:
   - "Excelente trabajo en el Ejercicio X, cumples completamente con todos los requisitos solicitados..."
   - "Tu trabajo demuestra dominio técnico en la implementación de los cuatro modelos..."
   - "El estudiante evidenció su compromiso con la dinámica del Ejercicio 5..."

FORMATO DE RESPUESTA (JSON):
{{
  "nivel_alcanzado": "<alto/medio/bajo>",
  "puntaje": <número entre 0 y {max_score}>,
  "feedback": "<feedback detallado, motivador y específico (2-4 párrafos)>",
  "aspectos_cumplidos": ["<aspecto específico 1>", "<aspecto específico 2>", "<aspecto específico 3>"],
  "mejoras": ["<sugerencia constructiva 1>", "<sugerencia constructiva 2>"]
}}
"""

            # Llamar a GPT
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un profesor universitario experto, cercano y motivador. Proporcionas retroalimentación detallada, específica y constructiva que reconoce logros y guía mejoras."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=900,
                response_format={"type": "json_object"}
            )

            # Parsear respuesta
            feedback_data = json.loads(response.choices[0].message.content)

            return {
                'success': True,
                'criterion_number': criterion_number,
                'criterion_name': criterion_name,
                'max_score': max_score,
                'score': feedback_data.get('puntaje', 0),
                'level_achieved': feedback_data.get('nivel_alcanzado', 'medio'),
                'feedback': feedback_data.get('feedback', ''),
                'aspects_met': feedback_data.get('aspectos_cumplidos', []),
                'improvements': feedback_data.get('mejoras', [])
            }

        except Exception as e:
            print(f"[ERROR] Error generando feedback para criterio '{criterion_name}': {e}")
            return {
                'success': False,
                'criterion_number': criterion.get('numero', 0),
                'criterion_name': criterion.get('nombre', ''),
                'error': str(e)
            }

    def generate_overall_feedback_criteria(self, course_name: str, criteria_feedbacks: List[Dict],
                                          total_score: float, max_score: int) -> Dict:
        """
        Genera retroalimentación general usando NUEVA estructura de criterios

        Args:
            course_name: Nombre del curso
            criteria_feedbacks: Lista de feedbacks por criterio
            total_score: Puntaje total obtenido
            max_score: Puntaje máximo posible

        Returns:
            Dict con feedback general y recomendaciones
        """
        try:
            # Resumir resultados por criterio
            criteria_summary = []
            for fb in criteria_feedbacks:
                if fb.get('success'):
                    criteria_summary.append(
                        f"- Criterio {fb['criterion_number']}: {fb['score']}/{fb['max_score']} pts ({fb['level_achieved']})"
                    )

            summary_text = '\n'.join(criteria_summary)
            percentage = (total_score / max_score * 100) if max_score > 0 else 0

            prompt = f"""
Eres un profesor de {course_name}. Proporciona una retroalimentación GENERAL sobre un trabajo estudiantil.

PUNTAJE FINAL: {total_score}/{max_score} ({percentage:.1f}%)

RESULTADOS POR CRITERIO:
{summary_text}

INSTRUCCIONES:
1. Resume el desempeño general del estudiante (máximo 2 párrafos cortos)
2. Destaca 2-3 fortalezas principales
3. Indica 2-3 áreas de mejora prioritarias
4. Proporciona una conclusión motivadora

FORMATO DE RESPUESTA (JSON):
{{
  "resumen": "<resumen general>",
  "fortalezas": ["<fortaleza 1>", "<fortaleza 2>"],
  "areas_mejora": ["<área 1>", "<área 2>"],
  "conclusion": "<conclusión motivadora>"
}}
"""

            # Llamar a GPT
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un profesor universitario que proporciona retroalimentación motivadora y constructiva."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=600,
                response_format={"type": "json_object"}
            )

            # Parsear respuesta
            overall_data = json.loads(response.choices[0].message.content)

            return {
                'success': True,
                'total_score': total_score,
                'max_score': max_score,
                'percentage': round(percentage, 1),
                'summary': overall_data.get('resumen', ''),
                'strengths': overall_data.get('fortalezas', []),
                'improvement_areas': overall_data.get('areas_mejora', []),
                'conclusion': overall_data.get('conclusion', '')
            }

        except Exception as e:
            print(f"[ERROR] Error generando feedback general: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def generate_section_feedback(self, section_name: str, section_criteria: List[str],
                                  section_weight: int, document_content: str,
                                  course_name: str) -> Dict:
        """
        Genera retroalimentación para una sección específica

        Args:
            section_name: Nombre de la sección
            section_criteria: Lista de criterios de evaluación
            section_weight: Peso de la sección (%)
            document_content: Contenido del documento del estudiante
            course_name: Nombre del curso

        Returns:
            Dict con feedback, puntaje y recomendaciones
        """
        try:
            # Construir prompt para GPT
            criteria_text = '\n'.join([f"{i+1}. {c}" for i, c in enumerate(section_criteria)])

            prompt = f"""
Eres un profesor experto en {course_name}. Evalúa la sección "{section_name}" de un trabajo estudiantil.

CRITERIOS DE EVALUACIÓN (Peso: {section_weight}%):
{criteria_text}

CONTENIDO DEL DOCUMENTO:
{document_content[:3000]}

INSTRUCCIONES:
1. Evalúa qué criterios se cumplen y cuáles no
2. Asigna un puntaje de 0-100 para esta sección
3. Proporciona retroalimentación CONCISA (máximo 3 párrafos cortos)
4. Sugiere 2-3 mejoras específicas

FORMATO DE RESPUESTA (JSON):
{{
  "puntaje": <número 0-100>,
  "cumple_criterios": [<lista de criterios cumplidos>],
  "no_cumple_criterios": [<lista de criterios no cumplidos>],
  "feedback": "<retroalimentación concisa>",
  "mejoras": ["<mejora 1>", "<mejora 2>", "<mejora 3>"]
}}
"""

            # Llamar a GPT
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un profesor universitario experto que proporciona retroalimentación constructiva y concisa."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=800,
                response_format={"type": "json_object"}
            )

            # Parsear respuesta
            feedback_data = json.loads(response.choices[0].message.content)

            return {
                'success': True,
                'section': section_name,
                'weight': section_weight,
                'score': feedback_data.get('puntaje', 0),
                'criteria_met': feedback_data.get('cumple_criterios', []),
                'criteria_not_met': feedback_data.get('no_cumple_criterios', []),
                'feedback': feedback_data.get('feedback', ''),
                'improvements': feedback_data.get('mejoras', [])
            }

        except Exception as e:
            print(f"[ERROR] Error generando feedback para sección '{section_name}': {e}")
            return {
                'success': False,
                'section': section_name,
                'error': str(e)
            }

    def generate_overall_feedback(self, course_name: str, section_feedbacks: List[Dict],
                                  total_score: float) -> Dict:
        """
        Genera retroalimentación general del documento

        Args:
            course_name: Nombre del curso
            section_feedbacks: Lista de feedbacks por sección
            total_score: Puntaje total ponderado

        Returns:
            Dict con feedback general y recomendaciones
        """
        try:
            # Resumir resultados por sección
            sections_summary = []
            for fb in section_feedbacks:
                if fb.get('success'):
                    sections_summary.append(
                        f"- {fb['section']}: {fb['score']}/100 (Peso: {fb['weight']}%)"
                    )

            summary_text = '\n'.join(sections_summary)

            prompt = f"""
Eres un profesor de {course_name}. Proporciona una retroalimentación GENERAL sobre un trabajo estudiantil.

PUNTAJE FINAL: {total_score:.1f}/100

RESULTADOS POR SECCIÓN:
{summary_text}

INSTRUCCIONES:
1. Resume el desempeño general del estudiante (máximo 2 párrafos cortos)
2. Destaca 2-3 fortalezas principales
3. Indica 2-3 áreas de mejora prioritarias
4. Proporciona una conclusión motivadora

FORMATO DE RESPUESTA (JSON):
{{
  "resumen": "<resumen general>",
  "fortalezas": ["<fortaleza 1>", "<fortaleza 2>"],
  "areas_mejora": ["<área 1>", "<área 2>"],
  "conclusion": "<conclusión motivadora>"
}}
"""

            # Llamar a GPT
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un profesor universitario que proporciona retroalimentación motivadora y constructiva."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.4,
                max_tokens=600,
                response_format={"type": "json_object"}
            )

            # Parsear respuesta
            overall_data = json.loads(response.choices[0].message.content)

            return {
                'success': True,
                'total_score': total_score,
                'summary': overall_data.get('resumen', ''),
                'strengths': overall_data.get('fortalezas', []),
                'improvement_areas': overall_data.get('areas_mejora', []),
                'conclusion': overall_data.get('conclusion', '')
            }

        except Exception as e:
            print(f"[ERROR] Error generando feedback general: {e}")
            return {
                'success': False,
                'error': str(e)
            }

    def evaluate_document(self, document_content: str, rubric_data: Dict,
                         relevant_sections: List[Dict] = None, file_name: str = None) -> Dict:
        """
        Evalúa un documento completo contra una rúbrica
        SOPORTA NUEVA ESTRUCTURA: criterios_evaluacion

        Args:
            document_content: Contenido extraído del documento
            rubric_data: Datos de la rúbrica del curso
            relevant_sections: Secciones relevantes encontradas por Pinecone (opcional)
            file_name: Nombre del archivo subido (para detectar criterio) (opcional)

        Returns:
            Dict con evaluación completa
        """
        course_name = rubric_data['nombre_curso']

        # NUEVA ESTRUCTURA: criterios_evaluacion (desde PDF)
        if 'criterios_evaluacion' in rubric_data:
            return self._evaluate_with_criteria(document_content, rubric_data, relevant_sections, file_name)

        # ESTRUCTURA ANTIGUA: condiciones_entrega (compatibilidad)
        elif 'condiciones_entrega' in rubric_data:
            return self._evaluate_with_sections(document_content, rubric_data, relevant_sections)

        else:
            return {
                'success': False,
                'error': 'Estructura de rúbrica no reconocida'
            }

    def _evaluate_with_criteria(self, document_content: str, rubric_data: Dict,
                                relevant_sections: List[Dict] = None, file_name: str = None) -> Dict:
        """Evalúa documento usando NUEVA estructura de criterios"""
        course_name = rubric_data['nombre_curso']
        criteria_to_evaluate = rubric_data['criterios_evaluacion']

        print(f"\n[EVAL] Evaluando documento para: {course_name}")
        print(f"       Archivo: {file_name if file_name else 'Sin nombre'}")
        print(f"       Total criterios: {len(criteria_to_evaluate)}")

        # NUEVO: Cargar condiciones detalladas del curso
        course_folder = self._get_course_folder_from_name(course_name)
        condiciones = self._load_condiciones(course_folder) if course_folder else {}

        if condiciones:
            print(f"       [OK] Condiciones cargadas - Verificacion PUNTO POR PUNTO activada")
        else:
            print(f"       [INFO] Sin condiciones - Evaluacion estandar")

        # PRIMERO: Detectar ejercicios en el documento
        exercises_in_doc = self._detect_exercises_in_document(document_content)
        print(f"       [EJERCICIOS] Detectados en documento: {exercises_in_doc if exercises_in_doc else 'Ninguno'}")

        # Detectar criterio/ejercicio desde nombre del archivo
        detected_criterion = self._detect_criterion_from_filename(file_name) if file_name else None

        # También buscar "Ejercicio X" en el nombre del archivo
        # IGNORAR números entre paréntesis como (2), (1), etc.
        if file_name and not detected_criterion:
            import re
            # Buscar "ejercicio X", "tarea X", etc. pero NO números entre paréntesis
            # Primero eliminar números entre paréntesis del nombre
            clean_name = re.sub(r'\(\d+\)', '', file_name)  # Elimina (1), (2), etc.

            match = re.search(r'ejercicio\s*(\d+)', clean_name.lower())
            if match:
                detected_criterion = int(match.group(1))
                print(f"       [OK] Ejercicio detectado desde nombre archivo: {detected_criterion}")

        if detected_criterion:
            print(f"       [OK] Criterio/Ejercicio detectado desde nombre: {detected_criterion}")
            print(f"       [FILTRADO] Solo se evaluara el Criterio {detected_criterion}")

        # Evaluar cada criterio
        criteria_feedbacks = []
        total_score = 0
        total_max_score = rubric_data.get('puntaje_total', 150)

        for i, criterion in enumerate(criteria_to_evaluate, 1):
            criterion_num = criterion['numero']
            print(f"  [{i}/{len(criteria_to_evaluate)}] Evaluando Criterio {criterion_num}: {criterion['nombre']}...")

            # FILTRO: Si el nombre del archivo indica un criterio específico
            # Solo evaluar ese criterio (excepto 4 y 5 que siempre se evalúan)
            if detected_criterion is not None:
                if criterion_num not in [4, 5] and criterion_num != detected_criterion:
                    print(f"  [SKIP] Criterio {criterion_num}: SALTADO (archivo indica Criterio {detected_criterion})")
                    # Crear feedback de NO PRESENTADO
                    feedback = {
                        'success': True,
                        'criterion_number': criterion_num,
                        'criterion_name': criterion['nombre'],
                        'max_score': criterion['puntaje_maximo'],
                        'score': 0,
                        'level_achieved': 'no_presentado',
                        'feedback': f'El nombre del archivo indica que este documento corresponde al Criterio/Ejercicio {detected_criterion}, no al Criterio {criterion_num}.',
                        'aspects_met': [],
                        'improvements': [f'Subir documento específico para el Criterio {criterion_num}']
                    }
                    criteria_feedbacks.append(feedback)
                    continue

            # Generar feedback para este criterio
            feedback = self.generate_criterion_feedback(
                criterion=criterion,
                document_content=document_content,
                course_name=course_name,
                detected_criterion=detected_criterion,  # NUEVO
                exercises_in_document=exercises_in_doc,  # NUEVO
                condiciones=condiciones  # NUEVO: Pasar condiciones para verificación detallada
            )

            if feedback.get('success'):
                criteria_feedbacks.append(feedback)
                total_score += feedback['score']
            else:
                print(f"  [ERROR] Error en criterio: {criterion['nombre']}")

        # Generar retroalimentación general
        print(f"\n  [GENERAL] Generando feedback general...")
        overall_feedback = self.generate_overall_feedback_criteria(
            course_name=course_name,
            criteria_feedbacks=criteria_feedbacks,
            total_score=total_score,
            max_score=total_max_score
        )

        return {
            'success': True,
            'course': course_name,
            'total_score': round(total_score, 1),
            'max_score': total_max_score,
            'criteria_feedbacks': criteria_feedbacks,
            'overall_feedback': overall_feedback,
            'timestamp': self._get_timestamp()
        }

    def _evaluate_with_sections(self, document_content: str, rubric_data: Dict,
                               relevant_sections: List[Dict] = None) -> Dict:
        """Evalúa documento usando ESTRUCTURA ANTIGUA de secciones"""
        course_name = rubric_data['nombre_curso']
        sections_to_evaluate = rubric_data['condiciones_entrega']

        # Si hay secciones relevantes de Pinecone, priorizarlas
        if relevant_sections:
            print(f"[INFO] Priorizando {len(relevant_sections)} secciones relevantes")
            # Ordenar por relevancia
            relevant_sections.sort(key=lambda x: x['relevance_score'], reverse=True)

        print(f"\n[EVAL] Evaluando documento para: {course_name}")
        print(f"       Total secciones: {len(sections_to_evaluate)}")

        # Evaluar cada sección
        section_feedbacks = []
        total_weighted_score = 0

        for i, section in enumerate(sections_to_evaluate, 1):
            print(f"  [{i}/{len(sections_to_evaluate)}] Evaluando: {section['seccion']}...")

            feedback = self.generate_section_feedback(
                section_name=section['seccion'],
                section_criteria=section['criterios'],
                section_weight=section['peso'],
                document_content=document_content,
                course_name=course_name
            )

            if feedback.get('success'):
                section_feedbacks.append(feedback)
                # Calcular puntaje ponderado
                weighted_score = (feedback['score'] / 100) * section['peso']
                total_weighted_score += weighted_score
            else:
                print(f"  [ERROR] Error en seccion: {section['seccion']}")

        # Generar retroalimentación general
        print(f"\n  [GENERAL] Generando feedback general...")
        overall_feedback = self.generate_overall_feedback(
            course_name=course_name,
            section_feedbacks=section_feedbacks,
            total_score=total_weighted_score
        )

        return {
            'success': True,
            'course': course_name,
            'total_score': round(total_weighted_score, 1),
            'section_feedbacks': section_feedbacks,
            'overall_feedback': overall_feedback,
            'timestamp': self._get_timestamp()
        }

    def _detect_exercises_in_document(self, document_content: str) -> list:
        """
        Detecta qué ejercicios están presentes en el documento buscando literalmente
        "Ejercicio 1", "Ejercicio 2", etc.

        VERSIÓN MEJORADA: Maneja saltos de línea y espacios del OCR

        Returns:
            Lista de números de ejercicios encontrados (ej: [1, 2, 5])
        """
        import re

        doc_lower = document_content.lower()
        exercises_found = []

        # Patrones FLEXIBLES para buscar ejercicios (permiten saltos de línea y múltiples espacios)
        patterns = [
            r'ejercicio[\s\n\r]*(\d+)',      # Ejercicio 1, Ejercicio\n1, etc.
            r'exercise[\s\n\r]*(\d+)',
            r'actividad[\s\n\r]*(\d+)',
            r'activity[\s\n\r]*(\d+)',
            r'punto[\s\n\r]*(\d+)',
            r'item[\s\n\r]*(\d+)',
            r'tarea[\s\n\r]*(\d+)',
            r'task[\s\n\r]*(\d+)',
        ]

        for pattern in patterns:
            matches = re.finditer(pattern, doc_lower, re.MULTILINE)
            for match in matches:
                exercise_num = int(match.group(1))
                if exercise_num not in exercises_found and 1 <= exercise_num <= 10:
                    exercises_found.append(exercise_num)

        return sorted(exercises_found)

    def _is_criterion_present(self, criterion: Dict, document_content: str, detected_criterion: int = None) -> bool:
        """
        Verifica si un criterio específico está presente en el documento usando GPT
        VERSIÓN BALANCEADA: Usa keywords + GPT, con el nombre del archivo como PISTA

        Args:
            criterion: Dict con información del criterio
            document_content: Contenido del documento
            detected_criterion: Criterio detectado desde nombre archivo (PISTA, no absoluto)

        Returns:
            True si el criterio está presente, False si no
        """
        try:
            criterion_name = criterion['nombre']
            criterion_num = criterion.get('numero', 0)

            # PISTA POSITIVA: Si el nombre del archivo indica ESTE criterio -> Facilitar detección
            file_hint_matches = (detected_criterion is not None and detected_criterion == criterion_num)

            # Detectar ejercicios presentes en el documento
            exercises_in_doc = self._detect_exercises_in_document(document_content)

            print(f"\n  [DEBUG] Criterio {criterion_num}:")
            print(f"    - detected_criterion: {detected_criterion}")
            print(f"    - file_hint_matches: {file_hint_matches}")
            print(f"    - exercises_found: {exercises_in_doc}")

            if file_hint_matches:
                print(f"  [INFO] Criterio {criterion_num}: Nombre del archivo indica este criterio (PISTA POSITIVA)")

            # DETECCIÓN DIRECTA POR EJERCICIOS
            # Si encuentra "Ejercicio X" en el documento, asumir que el criterio está presente
            if len(exercises_in_doc) > 0:
                # Si este criterio está en la lista de ejercicios detectados, PRESENTE
                if criterion_num in exercises_in_doc:
                    print(f"  [OK] Criterio {criterion_num}: Encontró Ejercicio {criterion_num} en el documento -> PRESENTE")
                    return True
                else:
                    print(f"  [WARN] Criterio {criterion_num}: Ejercicios detectados {exercises_in_doc}, pero no incluye {criterion_num}")

            # Keywords DINÁMICAS basadas en el nombre del criterio
            # Detectar automáticamente si es Fase 2 (Regresión/Clasificación) o Fase 3 (Clustering)
            criterion_name_lower = criterion_name.lower()

            # FASE 3: Clustering (K-Means, DBSCAN, Agglomerative)
            if 'k-mean' in criterion_name_lower or 'kmean' in criterion_name_lower:
                required_keywords = {
                    criterion_num: [
                        ['kmeans', 'k-means', 'k_means', 'cluster', 'agrupamiento'],
                        ['elbow', 'codo', 'silhouette', 'inertia'],
                    ]
                }
            elif 'dbscan' in criterion_name_lower:
                required_keywords = {
                    criterion_num: [
                        ['dbscan', 'db-scan', 'db_scan', 'cluster', 'agrupamiento'],
                        ['epsilon', 'eps', 'min_samples', 'ruido', 'noise', 'outlier'],
                    ]
                }
            elif 'agglomerative' in criterion_name_lower or 'jerárquico' in criterion_name_lower or 'hierarchical' in criterion_name_lower:
                required_keywords = {
                    criterion_num: [
                        ['agglomerative', 'hierarchical', 'jerárquico', 'cluster', 'agrupamiento'],
                        ['dendrograma', 'dendrogram', 'linkage'],
                    ]
                }
            # FASE 2: Regresión y Clasificación
            elif 'regresión' in criterion_name_lower or 'regression' in criterion_name_lower:
                required_keywords = {
                    criterion_num: [
                        ['regresión', 'regression', 'regressor', 'predic'],
                        ['MAE', 'MSE', 'RMSE', 'R²', 'r2', 'error', 'métrica'],
                    ]
                }
            elif 'clasificación' in criterion_name_lower or 'classification' in criterion_name_lower:
                required_keywords = {
                    criterion_num: [
                        ['clasificación', 'classification', 'classifier', 'clase'],
                        ['accuracy', 'precision', 'recall', 'F1', 'score', 'exactitud'],
                    ]
                }
            # GENÉRICOS (Foro, Formato, Carga de datos)
            else:
                required_keywords = {
                    1: [
                        ['dataset', 'datos', 'data', 'csv', 'archivo'],
                        ['carga', 'load', 'read_csv', 'lectura'],
                    ],
                    4: [
                        ['foro', 'forum', 'participación', 'comentario'],
                    ],
                    5: [
                        ['documento', 'entrega', 'formato', 'archivo']
                    ]
                }

            # Keywords DE EXCLUSIÓN (si están presentes, DESCARTAR el criterio)
            exclusion_keywords = {
                1: ['regresión', 'regression', 'clasificación', 'classification', 'MAE', 'MSE', 'accuracy', 'precision', 'recall'],  # Si tiene modelos -> NO es solo Criterio 1
                2: ['clasificación', 'classification', 'accuracy', 'precision', 'recall', 'F1'],  # Si tiene clasificación -> NO es Criterio 2
                3: ['regresión', 'regression', 'MAE', 'MSE', 'RMSE']  # Si SOLO tiene regresión -> NO es Criterio 3
            }

            doc_lower = document_content.lower()

            # FASE 0: DESHABILITADA - No usar exclusiones automáticas
            # Permitir que GPT decida basado en el contenido completo
            # (Las exclusiones eran demasiado agresivas para trabajos completos)

            # FASE 1: Verificación rápida de keywords obligatorias
            required_groups = required_keywords.get(criterion_num, [])
            groups_matched = 0

            for group in required_groups:
                if any(kw.lower() in doc_lower for kw in group):
                    groups_matched += 1

            # DETECCIÓN ESPECIAL PARA DBSCAN: Si encuentra "DBSCAN" en el código, ACEPTAR INMEDIATAMENTE
            if 'dbscan' in criterion_name_lower and 'dbscan' in doc_lower:
                print(f"  [OK] Criterio {criterion_num}: Encontró 'DBSCAN' en el documento -> PRESENTE (detección directa)")
                return True

            # DETECCIÓN ESPECIAL PARA K-MEANS: Si encuentra "kmeans" en el código, ACEPTAR INMEDIATAMENTE
            if ('k-mean' in criterion_name_lower or 'kmean' in criterion_name_lower) and ('kmeans' in doc_lower or 'k-means' in doc_lower):
                print(f"  [OK] Criterio {criterion_num}: Encontró 'KMeans' en el documento -> PRESENTE (detección directa)")
                return True

            # DETECCIÓN ESPECIAL PARA AGGLOMERATIVE: Si encuentra "agglomerative" en el código, ACEPTAR INMEDIATAMENTE
            if 'agglomerative' in criterion_name_lower and 'agglomerative' in doc_lower:
                print(f"  [OK] Criterio {criterion_num}: Encontró 'Agglomerative' en el documento -> PRESENTE (detección directa)")
                return True

            # Ajustar requisitos según pista de archivo
            # AHORA MÁS FLEXIBLE: Solo necesita 1 grupo en general
            if file_hint_matches:
                min_groups = 1  # Con pista: 1 grupo
            else:
                # Sin pista: También 1 grupo (MUY FLEXIBLE para permitir trabajos completos)
                min_groups = 1

            if groups_matched < min_groups:
                print(f"  [ERROR] Criterio {criterion_num}: Solo {groups_matched}/{len(required_groups)} grupos obligatorios -> NO PRESENTADO")
                return False

            print(f"  [OK] Criterio {criterion_num}: Encontró {groups_matched}/{len(required_groups)} grupos de keywords (mínimo: {min_groups})")

            # FASE 2: Validación con GPT
            # Si NO hay criterio detectado desde archivo, ser MUY PERMISIVO (trabajo completo)
            if detected_criterion is None:
                strictness = "PERMISIVO: Da el beneficio de la duda. Si hay CUALQUIER evidencia mínima del criterio, marca como PRESENTE."
            else:
                strictness = "BALANCEADO: Busca evidencia razonable del criterio."

            prompt = f"""
Eres un evaluador académico {strictness}

Determina si el siguiente documento contiene evidencia del criterio:

CRITERIO {criterion_num}: "{criterion_name}"

DOCUMENTO COMPLETO:
{document_content[:30000]}

INSTRUCCIONES ADAPTABLES según el nombre del criterio:

**Si el criterio menciona "K-Means" o "k-means"**:
- Busca: Implementación de K-Means, método del codo, Silhouette Score, selección de número de clusters, perfiles de clusters
- Código Python: KMeans(), inertia, silhouette_score
- Si encuentra esta implementación -> TRUE

**Si el criterio menciona "DBSCAN"**:
- Busca: Implementación de DBSCAN, selección de epsilon y min_samples, identificación de clusters y puntos de ruido
- Código Python: DBSCAN(), eps, min_samples, labels, outliers, noise
- IMPORTANTE: Busca también preparación de datos (StandardScaler, variables numéricas)
- Si encuentra esta implementación -> TRUE

**Si el criterio menciona "Agglomerative" o "jerárquico"**:
- Busca: Implementación de Agglomerative Clustering, dendrogramas, selección de variables, número óptimo de clusters
- Código Python: AgglomerativeClustering(), dendrogram, linkage
- Si encuentra esta implementación -> TRUE

**Si el criterio menciona "regresión"**:
- Busca: Implementación de regresión, métricas (MAE, MSE, RMSE, R²)
- Si encuentra modelos de regresión -> TRUE

**Si el criterio menciona "clasificación"**:
- Busca: Implementación de clasificación, métricas (accuracy, precision, recall, F1)
- Si encuentra modelos de clasificación -> TRUE

**Si el criterio menciona "foro" o "participación"**:
- Busca: Menciones de foro, retroalimentación, participación, screenshot
- Si encuentra participación -> TRUE

**Si el criterio menciona "formato" o "entrega"**:
- Siempre TRUE (evalúa formato del documento)

IMPORTANTE: Si encuentras evidencia razonable del criterio, marca como TRUE.
No seas demasiado estricto. Si hay dudas, da el beneficio de la duda al estudiante.

Responde SOLO con JSON:
{{
  "presente": true/false,
  "razon": "<explicación breve>",
  "confianza": "<alta/media/baja>"
}}
"""
            # Sistema de evaluación según contexto
            if detected_criterion is None:
                system_msg = "Eres un evaluador académico MUY PERMISIVO. El estudiante presentó un trabajo completo. Marca 'presente: true' si encuentras CUALQUIER evidencia del criterio, por mínima que sea."
            else:
                system_msg = "Eres un evaluador académico JUSTO. Marca 'presente: true' si hay evidencia razonable del criterio."

            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": system_msg},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.0,  # Más determinístico
                max_tokens=200,
                response_format={"type": "json_object"}
            )

            result = json.loads(response.choices[0].message.content)
            is_present = result.get('presente', False)
            confidence = result.get('confianza', 'baja')
            reason = result.get('razon', '')

            # DECISIÓN FINAL: Combinar keywords + GPT + pista de archivo
            # Si GPT dice que NO está presente, rechazar inmediatamente
            if not is_present:
                # PERO: Si el nombre del archivo coincide, dar una segunda oportunidad
                if file_hint_matches:
                    print(f"  [WARN] Criterio {criterion_num}: GPT dice NO PRESENTE pero archivo indica este criterio")
                    print(f"     -> ACEPTAR por pista de archivo (razón GPT: {reason[:80]})")
                    return True
                else:
                    print(f"  [ERROR] Criterio {criterion_num}: GPT confirmó NO PRESENTE -> {reason}")
                    return False

            # Si GPT dice SÍ pero con confianza BAJA
            if is_present and confidence == 'baja':
                # Si hay pista de archivo, ACEPTAR igual
                if file_hint_matches:
                    print(f"  [OK] Criterio {criterion_num}: Confianza baja pero archivo coincide -> ACEPTAR")
                    return True
                else:
                    print(f"  [WARN] Criterio {criterion_num}: GPT dice PRESENTE pero confianza BAJA -> NO PRESENTADO ({reason})")
                    return False

            # Si llegó aquí: GPT confirmó con confianza media/alta
            print(f"  [OK] Criterio {criterion_num}: PRESENTE confirmado (grupos: {groups_matched}, confianza: {confidence})")
            print(f"     Razón: {reason[:100]}")
            return True

        except Exception as e:
            print(f"[WARN] Error verificando presencia del criterio: {e}")
            # En caso de error, RECHAZAR por defecto (modo estricto)
            return False

    def _detect_criterion_from_filename(self, file_name: str) -> int:
        """
        Detecta el número de criterio/tarea desde el nombre del archivo
        Ignora números entre paréntesis como (1), (2), etc.

        Args:
            file_name: Nombre del archivo (ej: "tarea_2.pdf", "criterio3.ipynb", "ejercicio_1.png")

        Returns:
            Número del criterio detectado (1-5) o None si no se detecta
        """
        import re

        if not file_name:
            return None

        # Eliminar números entre paréntesis primero (para evitar confusión con versiones)
        file_lower = re.sub(r'\(\d+\)', '', file_name.lower())

        # Patrones para detectar criterio/tarea/ejercicio
        # IMPORTANTE: Usar \b (word boundary) para evitar coincidencias dentro de palabras como "Fase2"
        patterns = [
            r'criterio[_\s-]?(\d)',
            r'tarea[_\s-]?(\d)',
            r'ejercicio[_\s-]?(\d)',
            r'actividad[_\s-]?(\d)',
            r'punto[_\s-]?(\d)',
            r'task[_\s-]?(\d)',
            r'criterion[_\s-]?(\d)',
            r'activity[_\s-]?(\d)',
            r'\bc(\d)',  # c1, c2, c3 (solo al inicio de palabra)
            r'\bt(\d)',  # t1, t2, t3 (solo al inicio de palabra)
            r'\be(\d)',  # e1, e2, e3 (solo al inicio de palabra)
        ]

        for pattern in patterns:
            match = re.search(pattern, file_lower)
            if match:
                criterion_num = int(match.group(1))
                # Validar que sea un número válido (1-5)
                if 1 <= criterion_num <= 5:
                    return criterion_num

        return None

    def _get_timestamp(self) -> str:
        """Retorna timestamp actual"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def _load_condiciones(self, course_folder: str) -> Dict:
        """
        Carga el archivo condiciones.json de un curso

        Args:
            course_folder: Nombre de la carpeta del curso (ej: 'machine_learning_fase3')

        Returns:
            Dict con las condiciones o dict vacío si no existe
        """
        # Verificar cache
        if course_folder in self.condiciones_cache:
            return self.condiciones_cache[course_folder]

        # Buscar archivo condiciones.json
        condiciones_path = Path(f"courses/{course_folder}/condiciones.json")

        if not condiciones_path.exists():
            print(f"  [INFO] No se encontró condiciones.json para {course_folder}")
            return {}

        try:
            with open(condiciones_path, 'r', encoding='utf-8') as f:
                condiciones = json.load(f)
                self.condiciones_cache[course_folder] = condiciones
                print(f"  [OK] Cargadas condiciones para {course_folder}")
                return condiciones
        except Exception as e:
            print(f"  [ERROR] Error cargando condiciones: {e}")
            return {}

    def _get_detailed_tasks_for_criterion(self, criterion_num: int, condiciones: Dict) -> Dict:
        """
        Obtiene las tareas detalladas para un criterio específico

        Args:
            criterion_num: Número del criterio (1, 2, 3, etc.)
            condiciones: Dict con las condiciones del curso

        Returns:
            Dict con:
            - tasks: list (lista de tareas específicas)
            - deliverables: list (entregables esperados)
            - description: str (descripción del ejercicio)
        """
        if not condiciones or 'ejercicios' not in condiciones:
            return {'tasks': [], 'deliverables': [], 'description': ''}

        # Buscar el ejercicio correspondiente
        for ejercicio in condiciones['ejercicios']:
            if ejercicio.get('numero') == criterion_num:
                tasks = []
                deliverables = ejercicio.get('entregables', [])
                description = ejercicio.get('descripcion', '')

                # Tareas directas
                if 'tareas' in ejercicio:
                    tasks.extend(ejercicio['tareas'])

                # Si tiene escenarios (como K-Means)
                if 'escenarios' in ejercicio:
                    for escenario in ejercicio['escenarios']:
                        escenario_num = escenario.get('escenario', 0)
                        escenario_nombre = escenario.get('nombre', f'Escenario {escenario_num}')

                        if 'tareas' in escenario:
                            for tarea in escenario['tareas']:
                                tasks.append(f"[{escenario_nombre}] {tarea}")

                return {
                    'tasks': tasks,
                    'deliverables': deliverables,
                    'description': description
                }

        return {'tasks': [], 'deliverables': [], 'description': ''}

    def _get_course_folder_from_name(self, course_name: str) -> str:
        """
        Obtiene el nombre de la carpeta del curso desde el nombre del curso

        Args:
            course_name: Nombre del curso (ej: "Machine Learning - Fase 3")

        Returns:
            Nombre de la carpeta (ej: "machine_learning_fase3")
        """
        # Mapeo de nombres de curso a carpetas
        mappings = {
            'Machine Learning - Fase 2': 'machine_learning',
            'Machine Learning - Fase 3': 'machine_learning_fase3',
            'Machine Learning': 'machine_learning',
            'Big Data Integration': 'big_data_integration'
        }

        return mappings.get(course_name, '')


if __name__ == "__main__":
    # Test del generador de feedback
    print("=== Test GPT Feedback Generator ===\n")

    generator = GPTFeedbackGenerator()

    # Cargar rúbrica de ejemplo
    rubric_path = "../courses/machine_learning/condiciones.json"
    with open(rubric_path, 'r', encoding='utf-8') as f:
        rubric = json.load(f)

    # Documento de ejemplo
    test_document = """
    # Proyecto de Machine Learning: Predicción de Precios

    ## Introducción
    Este proyecto aborda el problema de predecir precios de casas usando regresión.
    El objetivo es crear un modelo preciso que ayude a estimar valores de propiedades.

    ## Exploración de Datos
    El dataset contiene 1000 registros con 15 features.
    Se identificaron 20 valores faltantes y 3 outliers.
    La correlación entre área y precio es 0.85.

    ## Modelado
    import pandas as pd
    from sklearn.linear_model import LinearRegression
    from sklearn.ensemble import RandomForestRegressor

    # Modelo entrenado con 80/20 split
    model = RandomForestRegressor(n_estimators=100)
    model.fit(X_train, y_train)

    ## Resultados
    RMSE: 15000
    R²: 0.82
    """

    # Evaluar documento
    result = generator.evaluate_document(test_document, rubric)

    if result['success']:
        print(f"\n[OK] Evaluación completada")
        print(f"  - Puntaje total: {result['total_score']}/100")
        print(f"  - Secciones evaluadas: {len(result['section_feedbacks'])}")
        print(f"\n  Feedback general:")
        print(f"  {result['overall_feedback']['summary'][:200]}...")
    else:
        print(f"[ERROR] Error en evaluación")
