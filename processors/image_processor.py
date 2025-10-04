"""
Procesador de imágenes con OCR
Extrae texto de imágenes usando Tesseract
"""
from PIL import Image
import pytesseract
import os
from typing import Dict

class ImageProcessor:
    """Procesa imágenes y extrae texto mediante OCR"""

    def __init__(self):
        self.supported_formats = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']

        # Configurar ruta de Tesseract (ajustar según instalación)
        # En Windows, descomentar y ajustar la ruta:
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

    def extract_text(self, image_path: str, lang='spa+eng') -> Dict[str, any]:
        """
        Extrae texto de una imagen usando OCR

        Args:
            image_path: Ruta a la imagen
            lang: Idiomas para OCR ('spa' español, 'eng' inglés)

        Returns:
            Dict con texto extraído y metadatos
        """
        try:
            # Abrir imagen
            image = Image.open(image_path)

            # Convertir a RGB si es necesario
            if image.mode != 'RGB':
                image = image.convert('RGB')

            # Extraer texto con OCR
            text = pytesseract.image_to_string(image, lang=lang)

            # Obtener información adicional
            width, height = image.size
            format_type = image.format

            return {
                'success': True,
                'text': text.strip(),
                'metadata': {
                    'width': width,
                    'height': height,
                    'format': format_type,
                    'mode': image.mode
                }
            }

        except pytesseract.TesseractNotFoundError:
            return {
                'success': False,
                'error': 'Tesseract no está instalado. Instalar desde: https://github.com/UB-Mannheim/tesseract/wiki',
                'text': ''
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'text': ''
            }

    def enhance_image_for_ocr(self, image_path: str, output_path: str = None) -> str:
        """
        Mejora la imagen para mejor OCR (contraste, nitidez)

        Args:
            image_path: Ruta a la imagen original
            output_path: Ruta para guardar imagen mejorada

        Returns:
            Ruta de la imagen mejorada
        """
        try:
            from PIL import ImageEnhance, ImageFilter

            image = Image.open(image_path)

            # Convertir a escala de grises
            image = image.convert('L')

            # Aumentar contraste
            enhancer = ImageEnhance.Contrast(image)
            image = enhancer.enhance(2.0)

            # Aplicar nitidez
            image = image.filter(ImageFilter.SHARPEN)

            # Guardar imagen mejorada
            if output_path is None:
                name, ext = os.path.splitext(image_path)
                output_path = f"{name}_enhanced{ext}"

            image.save(output_path)

            return output_path

        except Exception as e:
            print(f"Error mejorando imagen: {e}")
            return image_path

    def process(self, image_path: str, enhance: bool = True) -> Dict:
        """
        Procesa completamente una imagen extrayendo texto

        Args:
            image_path: Ruta a la imagen
            enhance: Si True, mejora la imagen antes del OCR

        Returns:
            Dict con contenido procesado
        """
        # Mejorar imagen si se solicita
        if enhance:
            enhanced_path = self.enhance_image_for_ocr(image_path)
            extraction_result = self.extract_text(enhanced_path)

            # Limpiar imagen temporal
            if enhanced_path != image_path and os.path.exists(enhanced_path):
                try:
                    os.remove(enhanced_path)
                except:
                    pass
        else:
            extraction_result = self.extract_text(image_path)

        if not extraction_result['success']:
            return extraction_result

        # Analizar contenido extraído
        text = extraction_result['text']
        has_code = any(keyword in text.lower() for keyword in ['import', 'def ', 'class ', 'function'])
        has_diagrams = len(text) < 100  # Imágenes con poco texto probablemente son diagramas

        return {
            'success': True,
            'full_text': text,
            'has_code': has_code,
            'has_diagrams': has_diagrams,
            'metadata': extraction_result['metadata']
        }


if __name__ == "__main__":
    # Test del procesador
    processor = ImageProcessor()

    # Crear imagen de prueba simple
    test_image = Image.new('RGB', (400, 100), color='white')
    from PIL import ImageDraw, ImageFont
    draw = ImageDraw.Draw(test_image)
    draw.text((10, 40), "Test de OCR - Machine Learning", fill='black')
    test_image.save("test_image.png")

    result = processor.process("test_image.png")

    if result['success']:
        print(f"✓ Imagen procesada exitosamente")
        print(f"  - Texto extraído: {result['full_text'][:100]}...")
        print(f"  - Tiene código: {result['has_code']}")
    else:
        print(f"✗ Error: {result['error']}")
