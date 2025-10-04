# Instalación de OCR para PDFs con Imágenes

## 🎯 Problema Detectado

Los PDFs con **imágenes** (capturas de pantalla de Jupyter Notebooks) NO se estaban leyendo correctamente porque faltaba OCR (Optical Character Recognition).

---

## ✅ Solución: Instalar Tesseract OCR

### **Paso 1: Instalar Tesseract en Windows**

1. Descargar Tesseract desde:
   ```
   https://github.com/UB-Mannheim/tesseract/wiki
   ```

2. Descargar el instalador para Windows:
   ```
   tesseract-ocr-w64-setup-5.3.3.20231005.exe
   ```

3. Ejecutar el instalador y seguir los pasos
   - **IMPORTANTE**: Durante la instalación, seleccionar idiomas:
     - ✅ **Spanish** (español)
     - ✅ **English** (inglés)

4. Ruta de instalación típica:
   ```
   C:\Program Files\Tesseract-OCR\tesseract.exe
   ```

---

### **Paso 2: Instalar Librerías Python**

Abrir terminal y ejecutar:

```bash
cd C:\Users\DELL\Downloads\Gemini Agent\proyecto_retroalimentacion

pip install pytesseract
pip install pdf2image
pip install Pillow
```

---

### **Paso 3: Instalar Poppler (requerido para pdf2image)**

1. Descargar Poppler para Windows:
   ```
   https://github.com/oschwartz10612/poppler-windows/releases/
   ```

2. Descargar el archivo `.zip` más reciente
   ```
   poppler-24.02.0-0.zip
   ```

3. Extraer el contenido a:
   ```
   C:\Program Files\poppler\
   ```

4. Agregar a PATH de Windows:
   - Buscar "Variables de entorno" en Windows
   - Editar "Path" del sistema
   - Agregar: `C:\Program Files\poppler\Library\bin`

---

### **Paso 4: Verificar Instalación**

Ejecutar en Python:

```python
import pytesseract
from pdf2image import convert_from_path

# Verificar Tesseract
print(pytesseract.get_tesseract_version())

# Debería imprimir: 5.3.3 (o similar)
```

---

## 🚀 Cómo Funciona Ahora

El sistema automáticamente:

1. **Intenta extraer texto normal** del PDF
2. Si el texto es **muy poco** (< 100 caracteres) → **Activa OCR**
3. Convierte cada página del PDF a imagen
4. Extrae texto de las imágenes con Tesseract
5. Procesa el texto extraído normalmente

---

## 📊 Logs Esperados

Cuando proceses un PDF con imágenes verás:

```
[PDF] Procesando: G30_Samuel_Cortes_Fase2 (2).pdf
[PDF] Texto extraído muy corto (15 chars), intentando OCR...
  [OCR] Convirtiendo PDF a imágenes...
  [OCR] Procesando 12 páginas con OCR...
  [OCR] Página 1: 1245 caracteres extraídos
  [OCR] Página 2: 1520 caracteres extraídos
  ...
[PDF] ✓ OCR exitoso: 15000 caracteres
[PDF] ✓ Procesado: 15000 caracteres totales

[EVAL] Evaluando documento para: Machine Learning
       🔍 Ejercicios detectados en documento: [1, 2, 3]

✅ Criterio 1: Encontró Ejercicio 1 en el documento → PRESENTE
✅ Criterio 2: Encontró Ejercicio 2 en el documento → PRESENTE
✅ Criterio 3: Encontró Ejercicio 3 en el documento → PRESENTE
```

---

## ⚠️ Si No Tienes Permisos de Administrador

Si no puedes instalar Tesseract en `C:\Program Files`:

1. Instala en tu carpeta de usuario:
   ```
   C:\Users\DELL\Tesseract-OCR\
   ```

2. El sistema buscará automáticamente en esa ubicación

---

## 🎉 Resultado Final

Después de instalar OCR, el sistema podrá:

✅ Leer PDFs con texto normal
✅ Leer PDFs con imágenes (capturas de Jupyter)
✅ Leer PDFs escaneados
✅ Detectar "Ejercicio 1", "Ejercicio 2", etc. en imágenes
✅ Evaluar correctamente trabajos completos

---

## 🔧 Solución de Problemas

### Error: "Tesseract not found"
```
Verificar que tesseract.exe esté en la ruta correcta:
C:\Program Files\Tesseract-OCR\tesseract.exe
```

### Error: "Unable to get page count"
```
Instalar Poppler y agregarlo al PATH de Windows
```

### OCR muy lento
```
Normal - OCR puede tomar 5-10 segundos por página
Para PDFs grandes (>20 páginas), puede tomar varios minutos
```

---

¡Con OCR instalado, el sistema funcionará perfectamente! 🎉
