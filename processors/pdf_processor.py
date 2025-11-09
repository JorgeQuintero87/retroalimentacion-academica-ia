"""
Procesador de documentos PDF con OCR avanzado
Extrae texto y estructura del documento
Incluye OCR mejorado para PDFs con imágenes
"""
import PyPDF2
import pdfplumber
from typing import Dict, List
from pdf2image import convert_from_path
import pytesseract
import cv2
import numpy as np
from PIL import Image
import os
import re

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

        # Configuraciones de Tesseract para PDFs
        self.psm_modes = [3, 6, 4]  # Mejores modos para documentos PDF

    def preprocess_pdf_image(self, pil_image: Image.Image) -> List[tuple]:
        """
        Preprocesa una imagen de página PDF con múltiples técnicas

        Args:
            pil_image: Imagen PIL de la página PDF

        Returns:
            Lista de tuplas (nombre_método, imagen_procesada)
        """
        # Convertir PIL a numpy array
        img_array = np.array(pil_image)

        # Convertir RGB a BGR para OpenCV
        if len(img_array.shape) == 3 and img_array.shape[2] == 3:
            img_bgr = cv2.cvtColor(img_array, cv2.COLOR_RGB2BGR)
        else:
            img_bgr = img_array

        processed_images = []

        # Convertir a escala de grises
        if len(img_bgr.shape) == 3:
            gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        else:
            gray = img_bgr

        # Técnica 1: Alta resolución + Otsu
        try:
            _, binary_otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            processed_images.append(('otsu', Image.fromarray(binary_otsu)))
        except:
            pass

        # Técnica 2: Eliminación de ruido + binarización
        try:
            denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
            _, binary_denoised = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            processed_images.append(('denoised', Image.fromarray(binary_denoised)))
        except:
            pass

        # Técnica 3: Aumento de contraste
        try:
            equalized = cv2.equalizeHist(gray)
            _, binary_eq = cv2.threshold(equalized, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            processed_images.append(('equalized', Image.fromarray(binary_eq)))
        except:
            pass

        # Técnica 4: Adaptativo gaussiano
        try:
            adaptive = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            processed_images.append(('adaptive', Image.fromarray(adaptive)))
        except:
            pass

        return processed_images

    def clean_ocr_text(self, text: str) -> str:
        """
        Limpia el texto extraído por OCR

        Args:
            text: Texto crudo del OCR

        Returns:
            Texto limpio
        """
        if not text:
            return ""

        # Eliminar espacios múltiples
        text = re.sub(r' +', ' ', text)

        # Eliminar líneas vacías múltiples
        text = re.sub(r'\n\s*\n', '\n\n', text)

        # Corregir puntuación mal espaciada
        text = re.sub(r'\s+([.,;:!?])', r'\1', text)

        # Eliminar caracteres extraños comunes
        text = text.replace('|', 'I')
        text = text.replace('°', 'o')

        return text.strip()

    def extract_text_with_ocr(self, pdf_path: str, use_advanced: bool = True) -> Dict[str, any]:
        """
        Extrae texto de PDF usando OCR avanzado con múltiples técnicas

        Args:
            pdf_path: Ruta al archivo PDF
            use_advanced: Si True, usa preprocesamiento avanzado

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

            print(f"  [OCR] Convirtiendo PDF a imágenes de alta resolución (DPI=400)...")
            # Convertir PDF a imágenes con mayor DPI para mejor calidad
            if poppler_path:
                images = convert_from_path(pdf_path, dpi=400, poppler_path=poppler_path)
            else:
                images = convert_from_path(pdf_path, dpi=400)

            pages_content = []
            full_text = ""

            print(f"  [OCR] Procesando {len(images)} páginas con OCR avanzado...")
            for i, image in enumerate(images):
                best_text = ""
                best_method = "basic"

                if use_advanced:
                    # Probar OCR básico primero
                    try:
                        basic_text = pytesseract.image_to_string(image, lang='spa+eng')
                        if basic_text and len(basic_text.strip()) > len(best_text):
                            best_text = basic_text
                            best_method = "basic"
                    except:
                        pass

                    # Probar con preprocesamiento avanzado
                    processed_images = self.preprocess_pdf_image(image)

                    for method_name, processed_img in processed_images:
                        for psm_mode in self.psm_modes:
                            try:
                                custom_config = f'--psm {psm_mode} --oem 3'
                                text = pytesseract.image_to_string(
                                    processed_img, lang='spa+eng', config=custom_config
                                )

                                # Seleccionar mejor resultado
                                if text and len(text.strip()) > len(best_text.strip()):
                                    words = text.split()
                                    if len(words) > 5:  # Contenido significativo
                                        best_text = text
                                        best_method = f"{method_name}_psm{psm_mode}"
                            except:
                                continue
                else:
                    # OCR básico sin preprocesamiento
                    best_text = pytesseract.image_to_string(image, lang='spa+eng')
                    best_method = "basic"

                # Limpiar texto
                best_text = self.clean_ocr_text(best_text)

                if best_text and len(best_text.strip()) > 10:
                    pages_content.append({
                        'page_number': i + 1,
                        'text': best_text,
                        'has_tables': False,
                        'extracted_with': f'OCR_{best_method}'
                    })
                    full_text += f"\n--- Página {i + 1} (OCR) ---\n{best_text}"
                    print(f"  [OCR] Página {i + 1}: {len(best_text)} caracteres extraídos (método: {best_method})")

            print(f"  [OCR] ✓ Extracción completa: {len(full_text)} caracteres totales")

            return {
                'success': True,
                'full_text': full_text,
                'pages': pages_content,
                'total_pages': len(images),
                'metadata': {'extraction_method': 'OCR_Advanced'}
            }

        except Exception as e:
            print(f"  [OCR] Error: {e}")
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

    def process(self, pdf_path: str, force_ocr: bool = False) -> Dict:
        """
        Procesa completamente un PDF con detección inteligente de método de extracción

        Args:
            pdf_path: Ruta al archivo PDF
            force_ocr: Si True, fuerza el uso de OCR sin intentar extracción normal

        Returns:
            Dict con todo el contenido procesado
        """
        print(f"\n[PDF] Procesando con OCR avanzado: {pdf_path}")

        full_text = ""
        extraction_result = None

        if force_ocr:
            # Forzar OCR directamente
            print(f"[PDF] Usando OCR avanzado (forzado)...")
            extraction_result = self.extract_text_with_ocr(pdf_path, use_advanced=True)
            full_text = extraction_result.get('full_text', '')
        else:
            # Intentar extracción normal primero
            print(f"[PDF] Intentando extracción de texto normal...")
            normal_result = self.extract_text(pdf_path)

            if normal_result['success']:
                normal_text = normal_result.get('full_text', '').strip()
                normal_length = len(normal_text)

                # Determinar si el texto extraído es suficiente
                if normal_length > 100:
                    print(f"[PDF] ✓ Texto nativo encontrado: {normal_length} caracteres")
                    extraction_result = normal_result
                    full_text = normal_text
                else:
                    print(f"[PDF] ⚠ Poco texto nativo ({normal_length} caracteres), probando OCR...")
                    ocr_result = self.extract_text_with_ocr(pdf_path, use_advanced=True)

                    if ocr_result['success']:
                        ocr_text = ocr_result.get('full_text', '').strip()
                        ocr_length = len(ocr_text)

                        # Comparar resultados y elegir el mejor
                        if ocr_length > normal_length * 1.5:  # OCR dio al menos 50% más texto
                            print(f"[PDF] ✓ OCR mejor resultado: {ocr_length} caracteres vs {normal_length}")
                            extraction_result = ocr_result
                            full_text = ocr_text
                        else:
                            print(f"[PDF] ✓ Usando texto nativo: {normal_length} caracteres")
                            extraction_result = normal_result
                            full_text = normal_text
                    else:
                        print(f"[PDF] ⚠ OCR falló, usando texto nativo")
                        extraction_result = normal_result
                        full_text = normal_text
            else:
                # Extracción normal falló, intentar OCR
                print(f"[PDF] ✗ Extracción normal falló, usando OCR...")
                extraction_result = self.extract_text_with_ocr(pdf_path, use_advanced=True)
                full_text = extraction_result.get('full_text', '')

        if not extraction_result or not extraction_result.get('success', False):
            return {
                'success': False,
                'error': 'No se pudo extraer texto del PDF',
                'full_text': '',
                'sections': {},
                'code_blocks': [],
                'pages': [],
                'total_pages': 0,
                'metadata': {}
            }

        # Procesar secciones
        sections = self.extract_sections(full_text)

        # Extraer código
        code_blocks = self.extract_code_blocks(full_text)

        print(f"[PDF] ✓ Procesado completo: {len(full_text)} caracteres, {len(sections)} secciones, {len(code_blocks)} bloques de código")

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
