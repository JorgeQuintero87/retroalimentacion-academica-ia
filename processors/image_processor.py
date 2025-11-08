"""
Procesador de imágenes con OCR mejorado
Extrae texto de imágenes usando Tesseract con preprocesamiento avanzado
"""
from PIL import Image, ImageEnhance, ImageFilter, ImageOps
import pytesseract
import os
import numpy as np
import cv2
from typing import Dict, Tuple, List

class ImageProcessor:
    """Procesa imágenes y extrae texto mediante OCR con técnicas avanzadas"""

    def __init__(self):
        self.supported_formats = ['.png', '.jpg', '.jpeg', '.bmp', '.tiff']
        self.min_dpi = 300  # DPI mínimo recomendado para OCR

        # Configurar ruta de Tesseract (ajustar según instalación)
        # En Windows, descomentar y ajustar la ruta:
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

        # Configuraciones de Tesseract optimizadas para diferentes tipos de contenido
        self.tesseract_configs = {
            'default': '--psm 3 --oem 3',  # PSM 3: Automatic page segmentation
            'single_block': '--psm 6 --oem 3',  # PSM 6: Uniform block of text
            'single_line': '--psm 7 --oem 3',  # PSM 7: Single text line
            'sparse': '--psm 11 --oem 3',  # PSM 11: Sparse text
            'dense': '--psm 1 --oem 3',  # PSM 1: Automatic with OSD
        }

    def pil_to_cv2(self, pil_image: Image.Image) -> np.ndarray:
        """Convierte imagen PIL a formato OpenCV (numpy array)"""
        return cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

    def cv2_to_pil(self, cv2_image: np.ndarray) -> Image.Image:
        """Convierte imagen OpenCV a PIL"""
        return Image.fromarray(cv2.cvtColor(cv2_image, cv2.COLOR_BGR2RGB))

    def upscale_image(self, image: Image.Image, target_dpi: int = 300) -> Image.Image:
        """
        Aumenta la resolución de la imagen para mejorar OCR

        Args:
            image: Imagen PIL
            target_dpi: DPI objetivo (default 300)

        Returns:
            Imagen escalada
        """
        width, height = image.size
        # Calcular factor de escala basado en tamaño (asumiendo ~72 DPI si es pequeña)
        if width < 1000 or height < 1000:
            scale_factor = target_dpi / 72
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            return image.resize((new_width, new_height), Image.Resampling.LANCZOS)
        return image

    def deskew_image(self, image: np.ndarray) -> np.ndarray:
        """
        Corrige la inclinación de la imagen

        Args:
            image: Imagen en formato OpenCV

        Returns:
            Imagen corregida
        """
        try:
            # Convertir a escala de grises
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

            # Invertir colores para detectar texto
            gray = cv2.bitwise_not(gray)

            # Detectar bordes
            thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

            # Encontrar coordenadas de todos los píxeles no cero
            coords = np.column_stack(np.where(thresh > 0))

            # Calcular ángulo de rotación
            angle = cv2.minAreaRect(coords)[-1]

            # Ajustar ángulo
            if angle < -45:
                angle = -(90 + angle)
            else:
                angle = -angle

            # Rotar imagen si el ángulo es significativo
            if abs(angle) > 0.5:
                (h, w) = image.shape[:2]
                center = (w // 2, h // 2)
                M = cv2.getRotationMatrix2D(center, angle, 1.0)
                rotated = cv2.warpAffine(image, M, (w, h),
                                        flags=cv2.INTER_CUBIC,
                                        borderMode=cv2.BORDER_REPLICATE)
                return rotated

            return image
        except:
            return image

    def remove_noise(self, image: np.ndarray) -> np.ndarray:
        """
        Elimina ruido de la imagen

        Args:
            image: Imagen en formato OpenCV

        Returns:
            Imagen sin ruido
        """
        # Aplicar filtro bilateral (preserva bordes mientras reduce ruido)
        denoised = cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
        return denoised

    def adaptive_threshold(self, image: np.ndarray) -> np.ndarray:
        """
        Aplica binarización adaptativa para mejorar contraste

        Args:
            image: Imagen en formato OpenCV

        Returns:
            Imagen binarizada
        """
        # Convertir a escala de grises
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

        # Aplicar binarización adaptativa
        binary = cv2.adaptiveThreshold(
            gray, 255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY,
            11, 2
        )

        # Convertir de vuelta a BGR para consistencia
        return cv2.cvtColor(binary, cv2.COLOR_GRAY2BGR)

    def enhance_image_advanced(self, image: Image.Image) -> List[Image.Image]:
        """
        Crea múltiples versiones mejoradas de la imagen para probar con OCR

        Args:
            image: Imagen PIL original

        Returns:
            Lista de imágenes mejoradas con diferentes técnicas
        """
        enhanced_images = []

        # Convertir a OpenCV
        cv2_img = self.pil_to_cv2(image)

        # Versión 1: Eliminación de ruido + Deskew
        try:
            img1 = self.remove_noise(cv2_img)
            img1 = self.deskew_image(img1)
            enhanced_images.append(('noise_removal', self.cv2_to_pil(img1)))
        except:
            pass

        # Versión 2: Binarización adaptativa
        try:
            img2 = self.deskew_image(cv2_img)
            img2 = self.adaptive_threshold(img2)
            enhanced_images.append(('adaptive_threshold', self.cv2_to_pil(img2)))
        except:
            pass

        # Versión 3: Procesamiento completo (ruido + binarización + deskew)
        try:
            img3 = self.remove_noise(cv2_img)
            img3 = self.deskew_image(img3)
            img3 = self.adaptive_threshold(img3)
            enhanced_images.append(('full_processing', self.cv2_to_pil(img3)))
        except:
            pass

        # Versión 4: Mejora clásica con PIL (contraste + nitidez)
        try:
            img4 = image.convert('L')  # Escala de grises
            enhancer = ImageEnhance.Contrast(img4)
            img4 = enhancer.enhance(2.0)
            img4 = img4.filter(ImageFilter.SHARPEN)
            enhanced_images.append(('classic', img4))
        except:
            pass

        return enhanced_images

    def extract_text_with_config(self, image: Image.Image, lang: str, config: str) -> Tuple[str, float]:
        """
        Extrae texto usando una configuración específica de Tesseract

        Args:
            image: Imagen PIL
            lang: Idiomas para OCR
            config: Configuración de Tesseract

        Returns:
            Tupla (texto extraído, confianza promedio)
        """
        try:
            # Extraer texto
            text = pytesseract.image_to_string(image, lang=lang, config=config)

            # Obtener datos de confianza
            data = pytesseract.image_to_data(image, lang=lang, config=config, output_type=pytesseract.Output.DICT)
            confidences = [float(conf) for conf in data['conf'] if conf != '-1']
            avg_confidence = sum(confidences) / len(confidences) if confidences else 0

            return text.strip(), avg_confidence
        except:
            return "", 0.0

    def extract_text(self, image_path: str, lang='spa+eng') -> Dict[str, any]:
        """
        Extrae texto de una imagen usando OCR con múltiples técnicas
        Prueba diferentes preprocesaminetos y configuraciones, retorna el mejor resultado

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
            if image.mode not in ['RGB', 'L']:
                image = image.convert('RGB')

            # Upscaling si la imagen es pequeña
            width, height = image.size
            original_size = (width, height)
            if width < 1000 or height < 1000:
                print(f"  [OCR] Imagen pequeña detectada ({width}x{height}), aplicando upscaling...")
                image = self.upscale_image(image)
                width, height = image.size

            # Obtener información adicional
            format_type = image.format

            # Crear versiones mejoradas de la imagen
            enhanced_versions = self.enhance_image_advanced(image)

            # Agregar imagen original
            enhanced_versions.insert(0, ('original', image))

            # Probar cada versión con diferentes configuraciones
            best_text = ""
            best_confidence = 0.0
            best_method = "original"

            print(f"  [OCR] Probando {len(enhanced_versions)} versiones de preprocesamiento...")

            for method_name, enhanced_img in enhanced_versions:
                # Probar con configuración por defecto
                text, confidence = self.extract_text_with_config(
                    enhanced_img, lang, self.tesseract_configs['default']
                )

                if confidence > best_confidence and len(text) > 10:
                    best_text = text
                    best_confidence = confidence
                    best_method = f"{method_name}_default"

                # Si el resultado no es bueno, probar con configuración sparse
                if confidence < 70 and len(text) < 100:
                    text, confidence = self.extract_text_with_config(
                        enhanced_img, lang, self.tesseract_configs['sparse']
                    )

                    if confidence > best_confidence and len(text) > 10:
                        best_text = text
                        best_confidence = confidence
                        best_method = f"{method_name}_sparse"

            print(f"  [OCR] Mejor resultado: {best_method} (confianza: {best_confidence:.1f}%)")
            print(f"  [OCR] Texto extraído: {len(best_text)} caracteres")

            return {
                'success': True,
                'text': best_text,
                'confidence': best_confidence,
                'method': best_method,
                'metadata': {
                    'width': width,
                    'height': height,
                    'original_size': original_size,
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

    def enhance_image_for_ocr(self, image_path: str, output_path: str = None, method: str = 'full_processing') -> str:
        """
        Mejora la imagen para mejor OCR (VERSIÓN MEJORADA)

        Args:
            image_path: Ruta a la imagen original
            output_path: Ruta para guardar imagen mejorada
            method: Método de mejora ('full_processing', 'adaptive_threshold', 'noise_removal', 'classic')

        Returns:
            Ruta de la imagen mejorada
        """
        try:
            image = Image.open(image_path)

            # Upscaling si es necesario
            image = self.upscale_image(image)

            # Aplicar mejora según método
            cv2_img = self.pil_to_cv2(image)

            if method == 'full_processing':
                cv2_img = self.remove_noise(cv2_img)
                cv2_img = self.deskew_image(cv2_img)
                cv2_img = self.adaptive_threshold(cv2_img)
                enhanced = self.cv2_to_pil(cv2_img)
            elif method == 'adaptive_threshold':
                cv2_img = self.deskew_image(cv2_img)
                cv2_img = self.adaptive_threshold(cv2_img)
                enhanced = self.cv2_to_pil(cv2_img)
            elif method == 'noise_removal':
                cv2_img = self.remove_noise(cv2_img)
                cv2_img = self.deskew_image(cv2_img)
                enhanced = self.cv2_to_pil(cv2_img)
            else:  # classic
                enhanced = image.convert('L')
                enhancer = ImageEnhance.Contrast(enhanced)
                enhanced = enhancer.enhance(2.0)
                enhanced = enhanced.filter(ImageFilter.SHARPEN)

            # Guardar imagen mejorada
            if output_path is None:
                name, ext = os.path.splitext(image_path)
                output_path = f"{name}_enhanced{ext}"

            enhanced.save(output_path)
            print(f"  [OCR] Imagen mejorada guardada: {output_path}")

            return output_path

        except Exception as e:
            print(f"  [OCR] Error mejorando imagen: {e}")
            return image_path

    def process(self, image_path: str, enhance: bool = True) -> Dict:
        """
        Procesa completamente una imagen extrayendo texto con OCR mejorado

        Args:
            image_path: Ruta a la imagen
            enhance: Si True, usa preprocesamiento avanzado (RECOMENDADO)

        Returns:
            Dict con contenido procesado
        """
        # El nuevo método extract_text ya incluye preprocesamiento avanzado automático
        # Prueba múltiples técnicas y retorna el mejor resultado
        print(f"\n[IMG] Procesando imagen: {image_path}")
        extraction_result = self.extract_text(image_path)

        if not extraction_result['success']:
            return extraction_result

        # Analizar contenido extraído
        text = extraction_result['text']
        confidence = extraction_result.get('confidence', 0)

        has_code = any(keyword in text.lower() for keyword in ['import', 'def ', 'class ', 'function', 'print(', 'return'])
        has_diagrams = len(text) < 100  # Imágenes con poco texto probablemente son diagramas

        print(f"[IMG] ✓ Procesado: {len(text)} caracteres (confianza: {confidence:.1f}%)")

        return {
            'success': True,
            'full_text': text,
            'has_code': has_code,
            'has_diagrams': has_diagrams,
            'confidence': confidence,
            'method': extraction_result.get('method', 'unknown'),
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
