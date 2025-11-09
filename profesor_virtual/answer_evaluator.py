"""
Módulo para evaluar respuestas de estudiantes usando IA
"""
import os
from openai import OpenAI
from typing import Dict, Tuple
import json


class AnswerEvaluator:
    """Evalúa respuestas de estudiantes y proporciona retroalimentación"""

    def __init__(self, api_key: str = None):
        """
        Inicializa el evaluador

        Args:
            api_key: Clave de API de OpenAI
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("Se requiere una API Key de OpenAI")
        self.client = OpenAI(api_key=self.api_key)

    def evaluate_answer(
        self,
        question: str,
        student_answer: str,
        expected_answer: str,
        keywords: list = None,
        document_context: str = ""
    ) -> Dict:
        """
        Evalúa la respuesta del estudiante

        Args:
            question: Pregunta realizada
            student_answer: Respuesta del estudiante
            expected_answer: Respuesta esperada
            keywords: Palabras clave que deberían aparecer
            document_context: Contexto del documento (opcional)

        Returns:
            Dict con evaluación, puntaje, feedback y es_correcta
        """
        try:
            # Preparar el contexto de palabras clave
            keywords_text = ""
            if keywords:
                keywords_text = f"\nPalabras clave esperadas: {', '.join(keywords)}"

            # Limitar el contexto del documento
            context_preview = document_context[:2000] if document_context else ""

            prompt = f"""
Eres un profesor evaluando la respuesta de un estudiante.

PREGUNTA:
{question}

RESPUESTA ESPERADA:
{expected_answer}
{keywords_text}

RESPUESTA DEL ESTUDIANTE:
{student_answer}

CONTEXTO DEL DOCUMENTO:
{context_preview}

INSTRUCCIONES:
1. Evalúa si la respuesta del estudiante es correcta o incorrecta
2. Asigna un puntaje del 0 al 100
3. Proporciona retroalimentación constructiva
4. Si la respuesta es incorrecta, explica por qué y da pistas
5. Si la respuesta es correcta, felicita al estudiante y refuerza el concepto
6. Sé amable pero honesto en tu evaluación

Devuelve la respuesta en formato JSON con esta estructura:
{{
  "es_correcta": true o false,
  "puntaje": número del 0 al 100,
  "feedback": "Retroalimentación detallada para el estudiante",
  "nivel": "excelente" | "bueno" | "regular" | "necesita mejorar"
}}

Responde ÚNICAMENTE con el JSON, sin texto adicional.
"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un profesor experto, empático y constructivo. Evalúas respuestas de estudiantes de forma justa y proporcionas retroalimentación útil. Siempre respondes en formato JSON válido."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )

            evaluation_json = response.choices[0].message.content.strip()

            # Limpiar posibles marcadores de código
            if evaluation_json.startswith("```json"):
                evaluation_json = evaluation_json[7:]
            if evaluation_json.startswith("```"):
                evaluation_json = evaluation_json[3:]
            if evaluation_json.endswith("```"):
                evaluation_json = evaluation_json[:-3]

            evaluation = json.loads(evaluation_json.strip())

            return evaluation

        except json.JSONDecodeError as e:
            print(f"Error al decodificar JSON: {e}")
            print(f"Respuesta recibida: {evaluation_json}")
            # Fallback
            return {
                "es_correcta": False,
                "puntaje": 50,
                "feedback": "No pude evaluar la respuesta correctamente. Por favor, intenta de nuevo.",
                "nivel": "regular"
            }
        except Exception as e:
            raise Exception(f"Error al evaluar respuesta: {str(e)}")

    def generate_encouragement(self, is_correct: bool, score: int) -> str:
        """
        Genera un mensaje de ánimo personalizado

        Args:
            is_correct: Si la respuesta fue correcta
            score: Puntaje obtenido

        Returns:
            str: Mensaje de ánimo
        """
        if is_correct and score >= 90:
            return "¡Excelente trabajo! Dominas muy bien este tema."
        elif is_correct and score >= 70:
            return "¡Muy bien! Vas por buen camino."
        elif score >= 50:
            return "Bien, pero puedes mejorar. Sigue estudiando."
        else:
            return "No te desanimes, todos aprendemos a nuestro ritmo. Revisa el material y vuelve a intentarlo."

    def format_feedback_for_speech(self, evaluation: Dict) -> str:
        """
        Formatea el feedback para ser leído por voz

        Args:
            evaluation: Diccionario con la evaluación

        Returns:
            str: Feedback formateado para voz
        """
        feedback = evaluation.get("feedback", "")
        encouragement = self.generate_encouragement(
            evaluation.get("es_correcta", False),
            evaluation.get("puntaje", 0)
        )

        return f"{feedback} {encouragement}"
