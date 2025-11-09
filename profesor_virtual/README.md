# 🎓 Profesor Virtual con IA

Sistema de enseñanza interactivo que utiliza Inteligencia Artificial para hacer preguntas basadas en documentos, escuchar las respuestas de los estudiantes mediante voz, y proporcionar retroalimentación personalizada.

## 🌟 Características

- **📄 Carga de Documentos**: Soporta PDF, TXT y DOCX
- **🤖 Generación Inteligente de Preguntas**: Usa GPT-4 para crear preguntas basadas en el contenido
- **🎤 Reconocimiento de Voz**: Escucha las respuestas del estudiante (Speech-to-Text)
- **🔊 Síntesis de Voz**: Lee las preguntas y retroalimentación en voz alta (Text-to-Speech)
- **✅ Evaluación Automática**: Analiza y califica las respuestas del estudiante
- **💬 Retroalimentación Personalizada**: Proporciona feedback constructivo o felicitaciones
- **📊 Seguimiento de Progreso**: Muestra estadísticas de desempeño

## 🚀 Instalación

### Requisitos previos

- Python 3.11+
- Cuenta de OpenAI con API Key

### Pasos de instalación

1. **Clonar el repositorio** (si aún no lo has hecho)

```bash
git clone <url-del-repositorio>
cd retroalimentacion-academica-ia
```

2. **Instalar dependencias**

```bash
pip install -r requirements.txt
```

3. **Configurar variables de entorno**

Crea un archivo `.env` en la raíz del proyecto con tu API Key de OpenAI:

```env
OPENAI_API_KEY=tu-api-key-aquí
```

## 🎯 Uso

### Ejecutar la aplicación

Desde el directorio `profesor_virtual`:

```bash
cd profesor_virtual
streamlit run app.py
```

O desde la raíz del proyecto:

```bash
streamlit run profesor_virtual/app.py
```

La aplicación se abrirá en tu navegador en `http://localhost:8501`

### Flujo de uso

1. **Cargar un documento**
   - Haz clic en "Selecciona un archivo"
   - Sube un archivo PDF, TXT o DOCX con el contenido a estudiar
   - El sistema extraerá automáticamente el texto

2. **Generar preguntas**
   - Configura el número de preguntas (1-10)
   - Selecciona el nivel de dificultad (Fácil, Medio, Difícil)
   - Haz clic en "Generar preguntas"
   - El sistema creará preguntas basadas en el documento

3. **Responder preguntas**

   Tienes dos opciones:

   **Opción A: Escribir respuesta**
   - Escribe tu respuesta en el cuadro de texto
   - Haz clic en "Enviar respuesta escrita"

   **Opción B: Responder por voz**
   - Haz clic en "🎤 Presiona para hablar"
   - Habla tu respuesta (asegúrate de permitir el acceso al micrófono)
   - Haz clic en "Enviar respuesta por voz"

4. **Recibir retroalimentación**
   - El sistema evaluará tu respuesta
   - Verás tu puntaje (0-100)
   - Recibirás retroalimentación escrita
   - La retroalimentación se leerá en voz alta automáticamente

5. **Continuar aprendiendo**
   - Haz clic en "Siguiente pregunta" para continuar
   - Revisa tus estadísticas en el panel lateral
   - Al finalizar, verás un resumen completo

## 🔧 Arquitectura

### Componentes principales

```
profesor_virtual/
├── app.py                    # Aplicación Streamlit principal
├── document_loader.py        # Carga y procesa documentos
├── question_generator.py     # Genera preguntas con IA
├── answer_evaluator.py       # Evalúa respuestas del estudiante
└── README.md                 # Esta documentación
```

### Tecnologías utilizadas

- **Streamlit**: Framework para la interfaz web
- **OpenAI GPT-4**: Generación de preguntas y evaluación de respuestas
- **Web Speech API**: Reconocimiento y síntesis de voz
- **PyPDF2 / python-docx**: Procesamiento de documentos

## 🎨 Características técnicas

### Generación de preguntas

El sistema utiliza GPT-4o-mini para:
- Analizar el contenido del documento
- Generar preguntas relevantes
- Crear respuestas esperadas
- Identificar palabras clave

### Evaluación de respuestas

El evaluador analiza:
- Corrección de la respuesta
- Presencia de palabras clave
- Coherencia con el contenido del documento
- Nivel de comprensión demostrado

Proporciona:
- Puntaje (0-100)
- Clasificación (excelente, bueno, regular, necesita mejorar)
- Retroalimentación constructiva personalizada

### Funcionalidades de voz

**Text-to-Speech (TTS)**:
- Lee preguntas en voz alta
- Lee retroalimentación automáticamente
- Usa voces en español
- Velocidad y tono ajustables

**Speech-to-Text (STT)**:
- Captura respuestas por voz
- Transcribe automáticamente
- Soporta español
- Interfaz visual de grabación

## 📊 Panel de estadísticas

El panel lateral muestra:
- Número total de preguntas respondidas
- Cantidad de respuestas correctas
- Puntuación promedio
- Progreso en tiempo real

## 🎯 Mejores prácticas

1. **Documentos claros**: Usa documentos bien estructurados para mejores preguntas
2. **Longitud adecuada**: Documentos de al menos 100 caracteres
3. **Respuestas completas**: Proporciona respuestas detalladas para mejor evaluación
4. **Micrófono**: Asegúrate de tener un micrófono funcional para respuestas por voz
5. **Navegador**: Usa Chrome, Edge o Safari para mejor compatibilidad con Web Speech API

## 🔒 Seguridad y privacidad

- Las respuestas se procesan en tiempo real
- No se almacenan datos personales permanentemente
- La API Key de OpenAI debe mantenerse privada
- Los documentos se procesan localmente antes de enviar a la API

## 🐛 Solución de problemas

### El reconocimiento de voz no funciona

- Asegúrate de usar Chrome, Edge o Safari
- Permite el acceso al micrófono cuando lo solicite el navegador
- Verifica que tu micrófono esté funcionando correctamente

### La síntesis de voz no funciona

- Algunos navegadores requieren interacción del usuario antes de reproducir audio
- Haz clic en cualquier botón antes de esperar que se reproduzca la voz

### Error al cargar documento

- Verifica que el formato sea PDF, TXT o DOCX
- Asegúrate de que el documento tenga contenido suficiente
- Revisa que el archivo no esté corrupto

### Error de API Key

- Verifica que `OPENAI_API_KEY` esté configurada en el archivo `.env`
- Asegúrate de que la API Key sea válida
- Verifica que tengas créditos disponibles en tu cuenta de OpenAI

## 📝 Ejemplos de uso

### Ejemplo 1: Estudiar un tema de matemáticas

1. Sube un PDF con teoremas de cálculo
2. Genera 5 preguntas de dificultad media
3. Responde las preguntas por escrito o por voz
4. Recibe retroalimentación instantánea

### Ejemplo 2: Aprender un nuevo idioma

1. Sube un documento con vocabulario en inglés
2. Genera 10 preguntas fáciles
3. Responde por voz para practicar pronunciación
4. Mejora tu comprensión con la retroalimentación

### Ejemplo 3: Preparar un examen

1. Sube tus apuntes de clase
2. Genera 8 preguntas difíciles
3. Evalúa tu nivel de preparación
4. Revisa las estadísticas para identificar áreas de mejora

## 🤝 Contribuciones

Este proyecto fue desarrollado como parte del sistema de retroalimentación académica con IA.

## 👨‍💻 Autor

**Ing. Jorge Quintero**
- Email: lucho19q@gmail.com
- Desarrollado con ❤️ usando IA

## 📄 Licencia

Este proyecto es parte del sistema de retroalimentación académica con IA.

---

## 🎓 Notas adicionales

### Requisitos del navegador

Para una experiencia óptima, se recomienda:
- **Chrome 25+**
- **Edge 79+**
- **Safari 14.1+**
- **Firefox** (soporte limitado para Web Speech API)

### Limitaciones conocidas

- El reconocimiento de voz requiere conexión a internet
- La precisión del reconocimiento depende de la calidad del micrófono
- Algunos navegadores pueden tener compatibilidad limitada con Web Speech API

### Próximas características

- [ ] Soporte para más idiomas
- [ ] Exportación de resultados a PDF
- [ ] Modo de práctica cronometrada
- [ ] Integración con bases de datos de preguntas
- [ ] Análisis de tendencias de aprendizaje

---

**¡Disfruta aprendiendo con tu Profesor Virtual con IA! 🎓🤖**
