# 🚀 Guía Completa de Deployment

## Opción 1: Streamlit Cloud (GRATIS - Recomendada)

### ✅ Ventajas:
- 100% gratis
- No necesitas configurar servidores
- URL pública automática: `https://tu-app.streamlit.app`
- Perfecto para proyectos educativos

### 📋 Requisitos Previos:
1. Cuenta de GitHub (gratis)
2. Cuenta de Streamlit Cloud (gratis)
3. Tus API Keys de Pinecone y OpenAI

---

## 📝 Paso 1: Crear Repositorio en GitHub

### Opción A: Desde la Interfaz Web de GitHub

1. Ve a https://github.com
2. Clic en "New repository" (botón verde)
3. Nombre: `retroalimentacion-academica`
4. Descripción: "Sistema automatizado de retroalimentación académica con IA"
5. Público o Privado (tu eliges)
6. NO marcar "Add README" (ya lo tienes)
7. Clic en "Create repository"

### Opción B: Desde la Terminal

```bash
# Navegar a tu proyecto
cd "C:\Users\DELL\Downloads\Gemini Agent\proyecto_retroalimentacion"

# Inicializar Git
git init

# Agregar todos los archivos
git add .

# Primer commit
git commit -m "Sistema de retroalimentación académica completo"

# Conectar con GitHub (reemplaza TU_USUARIO con tu usuario de GitHub)
git remote add origin https://github.com/TU_USUARIO/retroalimentacion-academica.git

# Subir código
git branch -M main
git push -u origin main
```

Si pide credenciales, usa tu usuario y un **Personal Access Token** (no la contraseña):
- Ir a GitHub → Settings → Developer settings → Personal access tokens
- Generar token con permisos de "repo"

---

## 🌐 Paso 2: Desplegar en Streamlit Cloud

### 2.1 Crear Cuenta

1. Ve a https://share.streamlit.io
2. Clic en "Sign up"
3. Autorizar con tu cuenta de GitHub

### 2.2 Crear Nueva App

1. Clic en "New app"
2. Llenar el formulario:
   - **Repository**: Seleccionar `tu-usuario/retroalimentacion-academica`
   - **Branch**: `main`
   - **Main file path**: `app.py`
   - **App URL**: Elegir un nombre (ej: `retroalimentacion-unad`)

### 2.3 Configurar Secrets (API Keys)

IMPORTANTE: Tus API keys NO deben estar en el código público.

1. Antes de hacer deploy, clic en "Advanced settings"
2. En la sección "Secrets", agregar:

```toml
PINECONE_API_KEY = "pcsk_7Lu2AQ_..."
OPENAI_API_KEY = "sk-proj-Vm8pE8nE5lJD..."
INDEX_NAME = "rubricamachine"
NAMESPACE = "solomachine"
```

3. Clic en "Deploy!"

### 2.4 Esperar el Deployment

El proceso toma 5-10 minutos:
- ✅ Instalando dependencias de `requirements.txt`
- ✅ Instalando Tesseract y Poppler desde `packages.txt`
- ✅ Iniciando la aplicación

### 2.5 Probar tu App

Tu app estará disponible en:
```
https://tu-nombre-app.streamlit.app
```

Compártela con quien quieras! 🎉

---

## 🔧 Paso 3: Actualizar tu App

Cuando hagas cambios en el código:

```bash
git add .
git commit -m "Descripción de los cambios"
git push
```

Streamlit Cloud detectará los cambios y actualizará automáticamente!

---

## ⚠️ Solución de Problemas

### Error: "Module not found"
- Verificar que todas las dependencias estén en `requirements.txt`
- Reiniciar la app desde Streamlit Cloud

### Error: "Tesseract not found"
- Verificar que `packages.txt` contenga:
  ```
  tesseract-ocr
  tesseract-ocr-spa
  poppler-utils
  ```

### Error: "API Key not found"
- Verificar que los secrets estén configurados correctamente
- Los nombres deben ser EXACTOS (mayúsculas/minúsculas)

### La app se "duerme"
- Plan gratuito: La app se duerme después de inactividad
- Primera carga después de inactividad puede tomar 30 segundos

---

## 💰 Costos

### Streamlit Cloud:
- **GRATIS** hasta 1 app pública
- Si necesitas más apps: $20/mes por 3 apps

### OpenAI (GPT-4o-mini):
- Muy barato: ~$0.15 por 1000 evaluaciones
- Puedes establecer límites de gasto en OpenAI

### Pinecone:
- Plan gratuito: Suficiente para este proyecto
- 1 índice, 100K vectores

---

## 🎯 Opciones Alternativas

### Si Streamlit Cloud no funciona:

1. **Hugging Face Spaces**: https://huggingface.co/spaces
2. **Render.com**: Plan gratuito disponible
3. **Railway.app**: $5 gratis al mes

---

## 📧 Compartir tu App

Una vez desplegada, puedes:

1. Compartir el link directo: `https://tu-app.streamlit.app`
2. Embeber en tu sitio web (iframe)
3. Agregar a Moodle/Canvas como herramienta externa

---

## 🔒 Seguridad

✅ Las API keys están protegidas (no visibles en el código)
✅ Los archivos subidos se borran después de procesar
✅ No se guarda información del estudiante

---

## 📞 Soporte

Si tienes problemas:
1. Revisar logs en Streamlit Cloud
2. Consultar https://docs.streamlit.io
3. GitHub Issues: https://github.com/streamlit/streamlit

---

¡Tu sistema de retroalimentación ya está listo para usarse en todo el mundo! 🌎
