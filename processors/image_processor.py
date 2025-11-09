"""
Procesador de imágenes con OCR avanzado
Extrae texto de imágenes usando Tesseract con preprocesamiento optimizado
"""
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import pytesseract
import cv2
import numpy as np
import os
from typing import Dict, List, Tuple
import re

class ImageProcessor:
    """Procesa imágenes y extrae texto mediante OCR con técnicas avanzadas"""

    def __init__(self):
        self.supported_formats = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']

        # Configurar ruta de Tesseract (ajustar según instalación)
        # En Windows, descomentar y ajustar la ruta:
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

        # Configuraciones de Tesseract para diferentes tipos de documentos
        self.psm_modes = [
            3,   # Segmentación automática de página (default)
            6,   # Bloque uniforme de texto
            4,   # Columna de texto variable
            1,   # Segmentación automática con OSD
        ]

    def deskew_image(self, image: np.ndarray) -> np.ndarray:
        """
        Corrige la inclinación de la imagen

        Args:
            image: Imagen en formato numpy array (escala de grises)

        Returns:
            Imagen corregida
        """
        try:
            # Detectar ángulo de inclinación
            coords = np.column_stack(np.where(image > 0))
            if len(coords) == 0:
                return image

            angle = cv2.minAreaRect(coords)[-1]

            # Ajustar ángulo
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle

            # Rotar imagen solo si el ángulo es significativo
            if abs(angle) > 0.5:
                (h, w) = image.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                image = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC,
                                      borderMode=cv2.BORDER_REPLICATE)

            return image
        except Exception as e:
            print(f"  [OCR] Advertencia en deskew: {e}")
            return image

    def advanced_preprocessing(self, image_path: str) -> List[np.ndarray]:
        """
        Aplica múltiples técnicas de preprocesamiento a la imagen

        Args:
            image_path: Ruta a la imagen

        Returns:
            Lista de imágenes procesadas con diferentes técnicas
        """
        # Leer imagen
        img = cv2.imread(image_path)
        if img is None:
            return []

        processed_images = []

        # Convertir a escala de grises
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Técnica 1: Binarización adaptativa con Otsu
        try:
            _, binary_otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            processed_images.append(('otsu', binary_otsu))
        except:
            pass

        # Técnica 2: Binarización adaptativa gaussiana
        try:
            adaptive_gaussian = cv2.adaptiveThreshold(
                gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
            )
            processed_images.append(('adaptive_gaussian', adaptive_gaussian))
        except:
            pass

        # Técnica 3: Eliminación de ruido + Otsu
        try:
            denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
            _, binary_denoised = cv2.threshold(denoised, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            processed_images.append(('denoised_otsu', binary_denoised))
        except:
            pass

        # Técnica 4: Corrección de inclinación + binarización
        try:
            deskewed = self.deskew_image(gray.copy())
            _, binary_deskewed = cv2.threshold(deskewed, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            processed_images.append(('deskewed', binary_deskewed))
        except:
            pass

        # Técnica 5: Aumento de contraste + nitidez
        try:
            # Ecualización de histograma
            equalized = cv2.equalizeHist(gray)
            # Nitidez
            kernel = np.array([[-1,-1,-1], [-1,9,-1], [-1,-1,-1]])
            sharpened = cv2.filter2D(equalized, -1, kernel)
            _, binary_sharp = cv2.threshold(sharpened, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            processed_images.append(('sharpened', binary_sharp))
        except:
            pass

        # Técnica 6: Morfología (cerrar espacios pequeños)
        try:
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
            morph = cv2.morphologyEx(gray, cv2.MORPH_CLOSE, kernel)
            _, binary_morph = cv2.threshold(morph, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
            processed_images.append(('morphology', binary_morph))
        except:
            pass

        return processed_images

    def clean_text(self, text: str) -> str:
        """
        Limpia y mejora el texto extraído por OCR

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

        # Eliminar caracteres extraños comunes del OCR
        text = text.replace('|', 'I')  # Barra vertical confundida con I
        text = text.replace('°', 'o')  # Grado confundido con o

        return text.strip()

    def extract_text(self, image_path: str, lang='spa+eng') -> Dict[str, any]:
        """
        Extrae texto de una imagen usando OCR avanzado con múltiples técnicas

        Args:
            image_path: Ruta a la imagen
            lang: Idiomas para OCR ('spa' español, 'eng' inglés)

        Returns:
            Dict con texto extraído y metadatos
        """
        try:
            # Abrir imagen original
            image = Image.open(image_path)
            width, height = image.size
            format_type = image.format

            # Convertir a RGB si es necesario
            if image.mode != 'RGB':
                image = image.convert('RGB')

            best_text = ""
            best_confidence = 0
            best_method = "basic"

            # Método 1: OCR básico en imagen original
            try:
                text_basic = pytesseract.image_to_string(image, lang=lang)
                if text_basic and len(text_basic.strip()) > len(best_text):
                    best_text = text_basic
                    best_method = "basic"
            except:
                pass

            # Método 2: Probar con diferentes preprocesamientos
            processed_images = self.advanced_preprocessing(image_path)

            for method_name, processed_img in processed_images:
                for psm_mode in self.psm_modes:
                    try:
                        # Configuración personalizada de Tesseract
                        custom_config = f'--psm {psm_mode} --oem 3'

                        # Convertir numpy array a PIL Image
                        pil_img = Image.fromarray(processed_img)

                        # Extraer texto
                        text = pytesseract.image_to_string(pil_img, lang=lang, config=custom_config)

                        # Seleccionar el mejor resultado (más largo con contenido significativo)
                        if text and len(text.strip()) > len(best_text.strip()):
                            # Validar que tenga contenido útil (no solo ruido)
                            words = text.split()
                            if len(words) > 3:  # Al menos 3 palabras
                                best_text = text
                                best_method = f"{method_name}_psm{psm_mode}"
                    except Exception as e:
                        continue

            # Limpiar texto final
            best_text = self.clean_text(best_text)

            print(f"  [OCR] Mejor método: {best_method}, {len(best_text)} caracteres")

            return {
                'success': True,
                'text': best_text,
                'metadata': {
                    'width': width,
                    'height': height,
                    'format': format_type,
                    'mode': image.mode,
                    'ocr_method': best_method
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
        Mejora la imagen para mejor OCR usando técnicas avanzadas de OpenCV

        Args:
            image_path: Ruta a la imagen original
            output_path: Ruta para guardar imagen mejorada

        Returns:
            Ruta de la imagen mejorada
        """
        try:
            # Leer imagen con OpenCV
            img = cv2.imread(image_path)
            if img is None:
                return image_path

            # Convertir a escala de grises
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Eliminar ruido
            denoised = cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)

            # Corrección de inclinación
            deskewed = self.deskew_image(denoised)

            # Binarización adaptativa con Otsu
            _, binary = cv2.threshold(deskewed, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

            # Morfología para limpiar
            kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (1, 1))
            cleaned = cv2.morphologyEx(binary, cv2.MORPH_CLOSE, kernel)

            # Guardar imagen mejorada
            if output_path is None:
                name, ext = os.path.splitext(image_path)
                output_path = f"{name}_enhanced{ext}"

            cv2.imwrite(output_path, cleaned)

            return output_path

        except Exception as e:
            print(f"Error mejorando imagen: {e}")
            return image_path

    def process(self, image_path: str, enhance: bool = True) -> Dict:
        """
        Procesa completamente una imagen extrayendo texto con OCR avanzado

        Args:
            image_path: Ruta a la imagen
            enhance: Parámetro mantenido por compatibilidad (extract_text ya usa técnicas avanzadas)

        Returns:
            Dict con contenido procesado
        """
        print(f"\n[IMG] Procesando imagen con OCR avanzado: {image_path}")

        # El nuevo extract_text ya prueba múltiples técnicas automáticamente
        extraction_result = self.extract_text(image_path)

        if not extraction_result['success']:
            return extraction_result

        # Analizar contenido extraído
        text = extraction_result['text']
        has_code = any(keyword in text.lower() for keyword in ['import', 'def ', 'class ', 'function', 'return', 'print'])
        has_diagrams = len(text) < 100  # Imágenes con poco texto probablemente son diagramas

        print(f"[IMG] ✓ Procesado: {len(text)} caracteres, código detectado: {has_code}")

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
