"""
Procesador de documentos PDF
Extrae texto y estructura del documento
Incluye OCR para PDFs con imágenes
"""
import PyPDF2
import pdfplumber
from typing import Dict, List
from pdf2image import convert_from_path
import pytesseract
import os

class PDFProcessor:
    """Procesa archivos PDF y extrae contenido estructurado"""

    def __init__(self):
        self.supported_formats = ['.pdf']
        # Configurar ruta de tesseract si está en Windows
        if os.name == 'nt':  # Windows
            # Rutas comunes de instalación de Tesseract en Windows
            possible_paths = [
                r'C:\Program Files\Tesseract-OCR\tesseract.exe',
                r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
                r'C:\Users\DELL\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    pytesseract.pytesseract.tesseract_cmd = path
                    break

    def extract_text_with_ocr(self, pdf_path: str, use_advanced_ocr: bool = True) -> Dict[str, any]:
        """
        Extrae texto de PDF usando OCR MEJORADO (para PDFs con imágenes)

        Args:
            pdf_path: Ruta al archivo PDF
            use_advanced_ocr: Si True, usa preprocesamiento avanzado (RECOMENDADO)

        Returns:
            Dict con texto extraído mediante OCR
        """
        try:
            # Buscar ruta de Poppler automáticamente
            poppler_path = None
            if os.name == 'nt':  # Windows
                possible_poppler_paths = [
                    r'C:\Program Files\poppler-25.07.0\Library\bin',
                    r'C:\Program Files\poppler\Library\bin',
                    r'C:\Program Files (x86)\poppler\Library\bin',
                    r'C:\Users\DELL\poppler\Library\bin'
                ]
                for path in possible_poppler_paths:
                    if os.path.exists(path):
                        poppler_path = path
                        print(f"  [OCR] Usando Poppler desde: {poppler_path}")
                        break

            print(f"  [OCR] Convirtiendo PDF a imágenes con DPI alto...")
            # Convertir PDF a imágenes con DPI más alto para mejor calidad
            if poppler_path:
                images = convert_from_path(pdf_path, dpi=400, poppler_path=poppler_path)
            else:
                images = convert_from_path(pdf_path, dpi=400)

            pages_content = []
            full_text = ""

            # Importar ImageProcessor para usar OCR mejorado
            if use_advanced_ocr:
                from processors.image_processor import ImageProcessor
                img_processor = ImageProcessor()
                print(f"  [OCR] ✨ Usando OCR MEJORADO con preprocesamiento avanzado")

            print(f"  [OCR] Procesando {len(images)} páginas con OCR mejorado...")

            for i, image in enumerate(images):
                if use_advanced_ocr:
                    # Usar OCR mejorado con múltiples técnicas
                    # Guardar imagen temporalmente
                    import tempfile
                    with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                        image.save(tmp_file.name, 'PNG')
                        tmp_path = tmp_file.name

                    try:
                        # Extraer texto con OCR avanzado
                        result = img_processor.extract_text(tmp_path, lang='spa+eng')
                        page_text = result.get('text', '')
                        confidence = result.get('confidence', 0)
                        method = result.get('method', 'unknown')

                        print(f"  [OCR] Página {i + 1}: {len(page_text)} caracteres "
                              f"(confianza: {confidence:.1f}%, método: {method})")
                    finally:
                        # Limpiar archivo temporal
                        try:
                            os.unlink(tmp_path)
                        except:
                            pass
                else:
                    # OCR básico
                    import pytesseract
                    page_text = pytesseract.image_to_string(image, lang='spa+eng')
                    confidence = 0
                    print(f"  [OCR] Página {i + 1}: {len(page_text)} caracteres extraídos")

                if page_text and len(page_text.strip()) > 10:
                    page_info = {
                        'page_number': i + 1,
                        'text': page_text,
                        'has_tables': False,
                        'extracted_with': 'OCR_ADVANCED' if use_advanced_ocr else 'OCR_BASIC'
                    }

                    if use_advanced_ocr:
                        page_info['confidence'] = confidence
                        page_info['method'] = method

                    pages_content.append(page_info)
                    full_text += f"\n--- Página {i + 1} (OCR) ---\n{page_text}"

            avg_confidence = sum(p.get('confidence', 0) for p in pages_content) / len(pages_content) if pages_content else 0

            print(f"  [OCR] ✓ Procesadas {len(pages_content)} páginas con éxito")
            if use_advanced_ocr:
                print(f"  [OCR] ✓ Confianza promedio: {avg_confidence:.1f}%")

            return {
                'success': True,
                'full_text': full_text,
                'pages': pages_content,
                'total_pages': len(images),
                'avg_confidence': avg_confidence,
                'metadata': {
                    'extraction_method': 'OCR_ADVANCED' if use_advanced_ocr else 'OCR_BASIC'
                }
            }

        except Exception as e:
            print(f"  [OCR] ✗ Error: {e}")
            import traceback
            traceback.print_exc()
            return {
                'success': False,
                'error': str(e),
                'full_text': '',
                'pages': []
            }

    def extract_text(self, pdf_path: str) -> Dict[str, any]:
        """
        Extrae texto de PDF usando pdfplumber (mejor para tablas y estructura)

        Args:
            pdf_path: Ruta al archivo PDF

        Returns:
            Dict con texto extraído, páginas, y metadatos
        """
        try:
            with pdfplumber.open(pdf_path) as pdf:
                pages_content = []
                full_text = ""

                for i, page in enumerate(pdf.pages):
                    page_text = page.extract_text()
                    if page_text:
                        pages_content.append({
                            'page_number': i + 1,
                            'text': page_text,
                            'has_tables': len(page.extract_tables()) > 0
                        })
                        full_text += f"\n--- Página {i + 1} ---\n{page_text}"

                return {
                    'success': True,
                    'full_text': full_text,
                    'pages': pages_content,
                    'total_pages': len(pdf.pages),
                    'metadata': pdf.metadata if hasattr(pdf, 'metadata') else {}
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'full_text': '',
                'pages': []
            }

    def extract_sections(self, text: str) -> Dict[str, str]:
        """
        Intenta detectar secciones del documento basándose en títulos comunes

        Args:
            text: Texto completo del documento

        Returns:
            Dict con secciones identificadas
        """
        sections = {}
        common_headers = [
            'introducción', 'introduction',
            'metodología', 'methodology',
            'resultados', 'results',
            'conclusiones', 'conclusions',
            'referencias', 'references',
            'implementación', 'implementation',
            'análisis', 'analysis',
            'arquitectura', 'architecture'
        ]

        lines = text.split('\n')
        current_section = 'general'
        current_content = []

        for line in lines:
            line_lower = line.lower().strip()

            # Detectar si es un encabezado
            is_header = False
            for header in common_headers:
                if header in line_lower and len(line.strip()) < 50:
                    # Guardar sección anterior
                    if current_content:
                        sections[current_section] = '\n'.join(current_content)

                    # Iniciar nueva sección
                    current_section = line.strip()
                    current_content = []
                    is_header = True
                    break

            if not is_header and line.strip():
                current_content.append(line)

        # Guardar última sección
        if current_content:
            sections[current_section] = '\n'.join(current_content)

        return sections

    def extract_code_blocks(self, text: str) -> List[str]:
        """
        Intenta extraer bloques de código del PDF

        Args:
            text: Texto del documento

        Returns:
            Lista de bloques de código encontrados
        """
        code_blocks = []

        # Buscar patrones comunes de código
        code_indicators = ['import ', 'def ', 'class ', 'if __name__', 'for ', 'while ', '```']

        lines = text.split('\n')
        in_code_block = False
        current_block = []

        for line in lines:
            # Detectar inicio/fin de bloque de código markdown
            if '```' in line:
                if in_code_block:
                    code_blocks.append('\n'.join(current_block))
                    current_block = []
                in_code_block = not in_code_block
                continue

            if in_code_block:
                current_block.append(line)
            else:
                # Detectar código por indentación o palabras clave
                if any(indicator in line for indicator in code_indicators):
                    if not current_block or len(current_block) < 3:
                        current_block.append(line)
                elif current_block and line.startswith('    '):
                    current_block.append(line)
                elif current_block and len(current_block) > 2:
                    code_blocks.append('\n'.join(current_block))
                    current_block = []

        # Agregar último bloque si existe
        if current_block and len(current_block) > 2:
            code_blocks.append('\n'.join(current_block))

        return code_blocks

    def process(self, pdf_path: str) -> Dict:
        """
        Procesa completamente un PDF extrayendo texto, secciones y código
        Si el PDF tiene poco texto, intenta OCR automáticamente

        Args:
            pdf_path: Ruta al archivo PDF

        Returns:
            Dict con todo el contenido procesado
        """
        print(f"\n[PDF] Procesando: {pdf_path}")

        # MODO DEBUG: SIEMPRE usar OCR primero para PDFs con imágenes
        print(f"[PDF] 🔍 MODO DEBUG: Intentando OCR primero...")
        ocr_result = self.extract_text_with_ocr(pdf_path)

        if ocr_result['success']:
            ocr_text_length = len(ocr_result.get('full_text', ''))
            print(f"[PDF] ✓ OCR exitoso: {ocr_text_length} caracteres extraídos")
            extraction_result = ocr_result
            full_text = ocr_result['full_text']
        else:
            print(f"[PDF] ✗ OCR falló, intentando extracción normal...")
            extraction_result = self.extract_text(pdf_path)
            full_text = extraction_result.get('full_text', '')

        # Procesar secciones
        sections = self.extract_sections(full_text)

        # Extraer código
        code_blocks = self.extract_code_blocks(full_text)

        print(f"[PDF] ✓ Procesado: {len(full_text)} caracteres totales")

        return {
            'success': True,
            'full_text': full_text,
            'sections': sections,
            'code_blocks': code_blocks,
            'pages': extraction_result.get('pages', []),
            'total_pages': extraction_result.get('total_pages', 0),
            'metadata': extraction_result.get('metadata', {})
        }


if __name__ == "__main__":
    # Test del procesador
    processor = PDFProcessor()
    result = processor.process("test.pdf")

    if result['success']:
        print(f"✓ PDF procesado exitosamente")
        print(f"  - Páginas: {result['total_pages']}")
        print(f"  - Secciones encontradas: {len(result['sections'])}")
        print(f"  - Bloques de código: {len(result['code_blocks'])}")
    else:
        print(f"✗ Error: {result['error']}")
