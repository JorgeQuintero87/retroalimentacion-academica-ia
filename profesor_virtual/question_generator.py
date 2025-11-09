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
        Genera preguntas basadas en el contenido del documento con contexto amplio

        Args:
            document_content: Contenido del documento
            num_questions: Número de preguntas a generar
            difficulty: Nivel de dificultad (easy, medium, hard)

        Returns:
            List[Dict]: Lista de preguntas con respuestas esperadas y contexto
        """
        try:
            # Traducir nivel de dificultad
            difficulty_es = {
                "easy": "fácil - preguntas directas sobre conceptos básicos",
                "medium": "medio - preguntas que requieren comprensión y análisis",
                "hard": "difícil - preguntas que requieren pensamiento crítico y aplicación"
            }.get(difficulty, "medio")

            prompt = f"""
Eres un profesor experto diseñando un examen oral. Basándote en el siguiente documento, genera {num_questions} preguntas de nivel {difficulty_es} para evaluar la comprensión profunda del estudiante.

DOCUMENTO COMPLETO:
{document_content[:6000]}  # Aumentado el límite para más contexto

INSTRUCCIONES IMPORTANTES:
1. Las preguntas deben basarse ÚNICAMENTE en el contenido del documento
2. Cada pregunta debe incluir suficiente contexto para que el estudiante entienda qué se pregunta
3. Las preguntas deben ser claras y específicas
4. Varía el tipo de preguntas:
   - Conceptuales: "¿Qué es...?", "Define..."
   - De comprensión: "¿Por qué...?", "Explica..."
   - De aplicación: "¿Cómo se relaciona...?", "¿Cuál es la diferencia entre...?"
   - De análisis: "Compara...", "Analiza..."
5. Incluye en cada pregunta el contexto necesario del documento
6. Las respuestas esperadas deben ser detalladas y basadas en el documento
7. Identifica palabras clave que deberían aparecer en una buena respuesta

FORMATO DE RESPUESTA (JSON):
Devuelve ÚNICAMENTE un array JSON con esta estructura exacta:
[
  {{
    "pregunta": "Según el documento, ¿qué es el Machine Learning y cómo se relaciona con la Inteligencia Artificial?",
    "respuesta_esperada": "El Machine Learning es un subcampo de la inteligencia artificial que se centra en desarrollar algoritmos que permiten a las computadoras aprender de los datos sin ser programadas explícitamente...",
    "palabras_clave": ["subcampo", "inteligencia artificial", "algoritmos", "aprender", "datos"],
    "contexto": "Esta pregunta se basa en la sección del documento que explica la relación entre IA y ML"
  }}
]

Responde ÚNICAMENTE con el JSON, sin texto adicional, sin markdown, sin explicaciones.
"""

            response = self.client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {
                        "role": "system",
                        "content": "Eres un profesor experto que genera preguntas educativas de alta calidad con contexto claro. Siempre respondes en formato JSON válido sin markdown."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=3000  # Aumentado para preguntas más detalladas
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

            # Validar que todas las preguntas tengan los campos necesarios
            for q in questions:
                if "pregunta" not in q or "respuesta_esperada" not in q:
                    raise ValueError("Pregunta mal formada")
                if "palabras_clave" not in q:
                    q["palabras_clave"] = []
                if "contexto" not in q:
                    q["contexto"] = ""

            return questions

        except json.JSONDecodeError as e:
            print(f"Error al decodificar JSON: {e}")
            print(f"Respuesta recibida: {questions_json}")
            # Fallback: crear preguntas genéricas basadas en el documento
            return self._generate_fallback_questions(document_content, num_questions)
        except Exception as e:
            print(f"Error general: {str(e)}")
            raise Exception(f"Error al generar preguntas: {str(e)}")

    def _generate_fallback_questions(self, document_content: str, num_questions: int) -> List[Dict]:
        """
        Genera preguntas de respaldo si falla el método principal

        Args:
            document_content: Contenido del documento
            num_questions: Número de preguntas

        Returns:
            List[Dict]: Lista de preguntas de respaldo
        """
        # Extraer las primeras oraciones del documento para contexto
        sentences = document_content[:1000].split('.')[:5]
        main_topic = sentences[0].strip() if sentences else "el documento"

        fallback_questions = [
            {
                "pregunta": f"Según {main_topic}, ¿cuáles son los conceptos principales que se explican en el documento?",
                "respuesta_esperada": "Los conceptos principales incluyen los temas centrales tratados en el documento",
                "palabras_clave": ["conceptos", "principales", "temas"],
                "contexto": "Pregunta general sobre el contenido principal"
            },
            {
                "pregunta": f"¿Qué información clave proporciona el documento sobre {main_topic}?",
                "respuesta_esperada": "El documento proporciona información detallada sobre los temas tratados",
                "palabras_clave": ["información", "clave", "detalles"],
                "contexto": "Pregunta sobre información específica del documento"
            },
            {
                "pregunta": "¿Puedes explicar con tus propias palabras los puntos más importantes del documento?",
                "respuesta_esperada": "Los puntos importantes son aquellos que destacan en el contenido",
                "palabras_clave": ["importantes", "destacar", "contenido"],
                "contexto": "Pregunta de comprensión general"
            }
        ]

        return fallback_questions[:num_questions]

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
        pregunta_text = question.get("pregunta", "")
        contexto_text = question.get("contexto", "")

        # Si hay contexto, agregarlo antes de la pregunta
        if contexto_text:
            return f"{contexto_text}. {pregunta_text}"
        else:
            return pregunta_text
