"""
Procesador de Rúbricas desde PDFs
Extrae criterios de evaluación automáticamente
"""
import re
from typing import Dict, List

try:
    from .pdf_processor import PDFProcessor
except ImportError:
    from pdf_processor import PDFProcessor

class RubricProcessor:
    """Procesa rúbricas en formato PDF y extrae criterios estructurados"""

    def __init__(self):
        self.pdf_processor = PDFProcessor()

    def extract_rubric_from_pdf(self, pdf_path: str, course_name: str) -> Dict:
        """
        Extrae la estructura de una rúbrica desde un PDF

        Args:
            pdf_path: Ruta al PDF de la rúbrica
            course_name: Nombre del curso

        Returns:
            Dict con la rúbrica estructurada
        """
        # Extraer texto del PDF
        result = self.pdf_processor.process(pdf_path)

        if not result['success']:
            return {'success': False, 'error': result.get('error', 'Error procesando PDF')}

        full_text = result['full_text']

        # Detectar idioma (español o inglés)
        is_spanish = 'criterio' in full_text.lower() or 'evaluación' in full_text.lower()

        # Extraer criterios
        if is_spanish:
            criteria = self._extract_criteria_spanish(full_text)
        else:
            criteria = self._extract_criteria_english(full_text)

        # Extraer puntaje total
        total_score = self._extract_total_score(full_text)

        return {
            'success': True,
            'nombre_curso': course_name,
            'descripcion': f'Rúbrica de evaluación para {course_name}',
            'puntaje_total': total_score,
            'criterios_evaluacion': criteria,
            'formato_aceptado': ['pdf', 'ipynb', 'png', 'jpg'],
            'idioma': 'español' if is_spanish else 'inglés'
        }

    def _extract_criteria_spanish(self, text: str) -> List[Dict]:
        """Extrae criterios de una rúbrica en español"""
        criteria_list = []

        # PATRÓN CORRECTO basado en la estructura real:
        # "Primer criterio de\nevaluación:\nNOMBRE DEL CRITERIO\nEste criterio tiene"
        pattern = r'(Primer|Segundo|Tercer|Cuarto|Quinto|Sexto|Séptimo)\s+criterio\s+de[\s\n]+evaluaci[óo]n[:\s]+(.*?)Este\s+criterio\s+tiene'

        matches = re.finditer(pattern, text, re.DOTALL | re.IGNORECASE)

        for i, match in enumerate(matches, 1):
            criterion_prefix = match.group(1)  # Primer, Segundo, etc.
            criterion_section = match.group(2).strip()

            # El nombre del criterio está en esta sección, después de los niveles iniciales
            # Buscar la línea que NO es "Nivel alto/medio/bajo"
            lines = criterion_section.split('\n')
            criterion_name = None

            for line in lines:
                line_clean = line.strip()
                if line_clean and 10 < len(line_clean) < 200:
                    # Saltar líneas que son niveles o instrucciones
                    if not any(line_clean.lower().startswith(prefix) for prefix in
                              ['nivel', 'si su', 'en este', 'obtener entre', 'la ', 'el ', 'presenta', 'aplica']):
                        # Esta probablemente es el nombre
                        if not any(word in line_clean.lower() for word in ['medio:', 'alto:', 'bajo:']):
                            criterion_name = line_clean
                            break

            if not criterion_name:
                # Buscar en reversa desde el final
                for line in reversed(lines):
                    line_clean = line.strip()
                    if line_clean and 10 < len(line_clean) < 150:
                        if 'seg' in line_clean.lower() or 'según' in line_clean.lower() or 'dataset' in line_clean.lower() or 'modelo' in line_clean.lower():
                            criterion_name = line_clean
                            break

            if not criterion_name:
                criterion_name = f"{criterion_prefix} criterio de evaluación"

            # Buscar el puntaje máximo DESPUÉS de "Este criterio tiene"
            score_section_start = match.end()
            score_section = text[score_section_start:score_section_start+150]
            score_pattern = r'una\s+valoraci[óo]n\s+m[áa]xima\s+de[:\s]+(\d+)\s*puntos'
            score_match = re.search(score_pattern, score_section, re.IGNORECASE)
            max_score = int(score_match.group(1)) if score_match else 0

            # Extraer niveles
            levels = self._extract_levels_spanish(text, match.start())

            criteria_list.append({
                'numero': i,
                'nombre': criterion_name,
                'puntaje_maximo': max_score,
                'niveles': levels,
                'descripcion': criterion_section[:200]
            })

        return criteria_list

    def _extract_criteria_english(self, text: str) -> List[Dict]:
        """Extrae criterios de una rúbrica en inglés"""
        criteria_list = []

        # Patrón para detectar criterios (First evaluation criterion, Second, etc.)
        pattern = r'(First|Second|Third|Fourth|Fifth|Sixth|Seventh)\s+evaluation\s+criterion[:\s]+(.*?)(?=This\s+criterion\s+has)'

        matches = re.finditer(pattern, text, re.DOTALL | re.IGNORECASE)

        for i, match in enumerate(matches, 1):
            criterion_number = match.group(1)
            criterion_text = match.group(2).strip()

            # Extraer nombre del criterio
            criterion_name = self._clean_criterion_name(criterion_text)

            # Extraer puntaje máximo
            score_pattern = r'maximum\s+score\s+of[:\s]+(\d+)\s*points'
            score_match = re.search(score_pattern, text[match.end():match.end()+200])
            max_score = int(score_match.group(1)) if score_match else 0

            # Extraer niveles
            levels = self._extract_levels_english(text, match.end())

            criteria_list.append({
                'numero': i,
                'nombre': criterion_name,
                'puntaje_maximo': max_score,
                'niveles': levels,
                'descripcion': criterion_text[:200]
            })

        return criteria_list

    def _clean_criterion_name(self, text: str) -> str:
        """Limpia y extrae el nombre del criterio"""
        # Tomar las primeras líneas
        lines = text.split('\n')
        clean_lines = [line.strip() for line in lines if line.strip()]

        # Retornar primera línea significativa
        for line in clean_lines[:3]:
            if len(line) > 10 and len(line) < 200:
                return line

        return clean_lines[0] if clean_lines else "Criterio sin nombre"

    def _extract_levels_spanish(self, text: str, start_pos: int) -> List[Dict]:
        """Extrae niveles de desempeño en español"""
        levels = []
        section_text = text[start_pos:start_pos+2000]

        # Buscar Nivel alto, medio, bajo
        level_patterns = {
            'alto': r'Nivel\s+alto[:\s]+(.*?)(?=Si\s+su\s+trabajo)',
            'medio': r'Nivel\s+medio[:\s]+(.*?)(?=Si\s+su\s+trabajo)',
            'bajo': r'Nivel\s+bajo[:\s]+(.*?)(?=Si\s+su\s+trabajo)'
        }

        for level_name, pattern in level_patterns.items():
            match = re.search(pattern, section_text, re.DOTALL | re.IGNORECASE)
            if match:
                description = match.group(1).strip()

                # Extraer rango de puntos
                score_pattern = r'entre\s+(\d+)\s+puntos?\s+y\s+(\d+)\s+puntos?'
                score_match = re.search(score_pattern, section_text[match.end():match.end()+100])

                if score_match:
                    min_score = int(score_match.group(1))
                    max_score = int(score_match.group(2))
                else:
                    min_score = 0
                    max_score = 0

                levels.append({
                    'nivel': level_name,
                    'descripcion': description[:300],
                    'puntaje_minimo': min_score,
                    'puntaje_maximo': max_score
                })

        return levels

    def _extract_levels_english(self, text: str, start_pos: int) -> List[Dict]:
        """Extrae niveles de desempeño en inglés"""
        levels = []
        section_text = text[start_pos:start_pos+2000]

        # Buscar High Level, Average Level, Low Level
        level_patterns = {
            'high': r'High\s+Level[:\s]+(.*?)(?=If\s+your\s+work)',
            'average': r'Average\s+Level[:\s]+(.*?)(?=If\s+your\s+work)',
            'low': r'Low\s+Level[:\s]+(.*?)(?=If\s+your\s+work)'
        }

        for level_name, pattern in level_patterns.items():
            match = re.search(pattern, section_text, re.DOTALL | re.IGNORECASE)
            if match:
                description = match.group(1).strip()

                # Extraer rango de puntos
                score_pattern = r'between\s+(\d+)\s+points?\s+and\s+(\d+)\s+points?'
                score_match = re.search(score_pattern, section_text[match.end():match.end()+100])

                if score_match:
                    min_score = int(score_match.group(1))
                    max_score = int(score_match.group(2))
                else:
                    min_score = 0
                    max_score = 0

                levels.append({
                    'nivel': level_name,
                    'descripcion': description[:300],
                    'puntaje_minimo': min_score,
                    'puntaje_maximo': max_score
                })

        return levels

    def _extract_total_score(self, text: str) -> int:
        """Extrae el puntaje total de la actividad"""
        # Buscar "Activity score: XXX" o "Puntaje de la actividad: XXX"
        patterns = [
            r'Activity\s+score[:\s]+(\d+)',
            r'Puntaje\s+de\s+la\s+actividad[:\s]+(\d+)'
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return int(match.group(1))

        return 150  # Valor por defecto


if __name__ == "__main__":
    # Test del procesador
    processor = RubricProcessor()

    # Test con rúbrica de Machine Learning
    print("=== Test Rubric Processor ===\n")
    print("1. Procesando rúbrica de Machine Learning...")

    rubric_ml = processor.extract_rubric_from_pdf(
        "../courses/machine_learning/Rúbrica de evaluación - Fase 2 - Componente práctico - Prácticas simuladas.pdf",
        "Machine Learning"
    )

    if rubric_ml['success']:
        print(f"   ✓ Rúbrica procesada exitosamente")
        print(f"   - Curso: {rubric_ml['nombre_curso']}")
        print(f"   - Puntaje total: {rubric_ml['puntaje_total']}")
        print(f"   - Criterios encontrados: {len(rubric_ml['criterios_evaluacion'])}")
        print(f"   - Idioma: {rubric_ml['idioma']}")

        print("\n   Criterios:")
        for criterio in rubric_ml['criterios_evaluacion']:
            print(f"   {criterio['numero']}. {criterio['nombre']}")
            print(f"      Puntaje máximo: {criterio['puntaje_maximo']}")
            print(f"      Niveles: {len(criterio['niveles'])}")
    else:
        print(f"   ✗ Error: {rubric_ml['error']}")

    # Test con rúbrica de Big Data
    print("\n2. Procesando rúbrica de Big Data Integration...")

    rubric_bd = processor.extract_rubric_from_pdf(
        "../courses/big_data_integration/Evaluation Rubric - Stage 2 - Big Data Analytics and Machine Learning.pdf",
        "Big Data Integration"
    )

    if rubric_bd['success']:
        print(f"   ✓ Rúbrica procesada exitosamente")
        print(f"   - Criterios encontrados: {len(rubric_bd['criterios_evaluacion'])}")

        print("\n   Criterios:")
        for criterio in rubric_bd['criterios_evaluacion']:
            print(f"   {criterio['numero']}. {criterio['nombre']}")
            print(f"      Puntaje máximo: {criterio['puntaje_maximo']}")
    else:
        print(f"   ✗ Error: {rubric_bd['error']}")
