"""
Módulo para generar preguntas basadas en documentos usando IA
"""
import os
from openai import OpenAI
from typing import List, Dict
import json


class QuestionGenerator:
    """Genera preguntas inteligentes basadas en el contenido de documentos"""

    def __init__(self, api_key: str = None):
        """
        Inicializa el generador de preguntas

        Args:
            api_key: Clave de API de OpenAI (si no se provee, se busca en env)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("Se requiere una API Key de OpenAI")
        self.client = OpenAI(api_key=self.api_key)

    def generate_questions(
        self,
        document_content: str,
        num_questions: int = 5,
        difficulty: str = "medium"
    ) -> List[Dict[str, str]]:
        """
        Genera preguntas basadas en el contenido del documento

        Args:
            document_content: Contenido del documento
            num_questions: Número de preguntas a generar
            difficulty: Nivel de dificultad (easy, medium, hard)

        Returns:
            List[Dict]: Lista de preguntas con respuestas esperadas
        """
        try:
            prompt = f"""
Eres un profesor experto. Basándote en el siguiente documento, genera {num_questions} preguntas de nivel {difficulty}
para evaluar la comprensión del estudiante.

DOCUMENTO:
{document_content[:4000]}  # Limitamos a 4000 caracteres para no exceder límites

INSTRUCCIONES:
- Las preguntas deben ser específicas sobre el contenido del documento
- Cada pregunta debe tener una respuesta clara basada en el documento
- No preguntes cosas que no estén en el documento
- Varía el tipo de preguntas: conceptuales, de aplicación, de análisis
- Devuelve la respuesta en formato JSON con esta estructura:
[
  {{
    "pregunta": "¿Cuál es...?",
    "respuesta_esperada": "La respuesta correcta basada en el documento",
    "palabras_clave": ["palabra1", "palabra2"]
  }}
]

Responde ÚNICAMENTE con el JSON, sin texto adicional.
"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un profesor experto que genera preguntas educativas basadas en documentos. Siempre respondes en formato JSON válido."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=2000
            )

            questions_json = response.choices[0].message.content.strip()

            # Limpiar posibles marcadores de código
            if questions_json.startswith("```json"):
                questions_json = questions_json[7:]
            if questions_json.startswith("```"):
                questions_json = questions_json[3:]
            if questions_json.endswith("```"):
                questions_json = questions_json[:-3]

            questions = json.loads(questions_json.strip())

            return questions

        except json.JSONDecodeError as e:
            print(f"Error al decodificar JSON: {e}")
            print(f"Respuesta recibida: {questions_json}")
            # Fallback: crear una pregunta genérica
            return [{
                "pregunta": "¿Cuáles son los conceptos principales del documento?",
                "respuesta_esperada": "Los conceptos principales incluyen los temas tratados en el documento",
                "palabras_clave": ["conceptos", "temas", "principales"]
            }]
        except Exception as e:
            raise Exception(f"Error al generar preguntas: {str(e)}")

    def get_next_question(self, questions: List[Dict], current_index: int) -> Dict[str, str]:
        """
        Obtiene la siguiente pregunta

        Args:
            questions: Lista de preguntas
            current_index: Índice actual

        Returns:
            Dict: Pregunta actual o None si no hay más
        """
        if current_index < len(questions):
            return questions[current_index]
        return None

    def format_question_for_speech(self, question: Dict[str, str]) -> str:
        """
        Formatea la pregunta para ser leída por síntesis de voz

        Args:
            question: Diccionario con la pregunta

        Returns:
            str: Pregunta formateada para voz
        """
        return question.get("pregunta", "")
