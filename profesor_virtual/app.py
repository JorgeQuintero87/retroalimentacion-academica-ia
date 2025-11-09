"""
Aplicación de Profesor Virtual con IA
Permite hacer preguntas basadas en documentos, escuchar al estudiante y dar retroalimentación
"""
import streamlit as st
import os
from document_loader import DocumentLoader
from question_generator import QuestionGenerator
from answer_evaluator import AnswerEvaluator
from dotenv import load_dotenv
import streamlit.components.v1 as components
import time

# Cargar variables de entorno
load_dotenv()

# Configuración de la página
st.set_page_config(
    page_title="Profesor Virtual con IA",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    .question-box {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
        color: #1a1a1a;
    }
    .question-box h3 {
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .question-box p {
        color: #2c2c2c;
        font-size: 1.2rem;
        line-height: 1.6;
    }
    .answer-box {
        background-color: #e8f4f8;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
    }
    .feedback-correct {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 8px;
        border-left: 5px solid #28a745;
        color: #155724;
    }
    .feedback-incorrect {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 8px;
        border-left: 5px solid #dc3545;
        color: #721c24;
    }
    .score-badge {
        display: inline-block;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        font-weight: bold;
        font-size: 1.2rem;
    }
    .score-excellent {
        background-color: #28a745;
        color: white;
    }
    .score-good {
        background-color: #17a2b8;
        color: white;
    }
    .score-regular {
        background-color: #ffc107;
        color: #212529;
    }
    .score-poor {
        background-color: #dc3545;
        color: white;
    }
    .stButton>button {
        width: 100%;
        background-color: #1f77b4;
        color: white;
        border-radius: 5px;
        padding: 0.5rem 1rem;
        font-size: 1rem;
        border: none;
        transition: all 0.3s;
    }
    .stButton>button:hover {
        background-color: #155a8a;
        transform: scale(1.02);
    }
</style>
""", unsafe_allow_html=True)

# Función para síntesis de voz (TTS)
def speak_text(text: str):
    """Usa Web Speech API para reproducir texto como voz"""
    # Limpiar comillas para evitar errores en JavaScript
    text_clean = text.replace('"', '\\"').replace("'", "\\'").replace("\n", " ")
    speech_html = f"""
    <script>
        if ('speechSynthesis' in window) {{
            const utterance = new SpeechSynthesisUtterance("{text_clean}");
            utterance.lang = 'es-ES';
            utterance.rate = 0.9;
            utterance.pitch = 1.0;
            window.speechSynthesis.speak(utterance);
        }} else {{
            console.error('Speech Synthesis no está disponible en este navegador');
        }}
    </script>
    """
    components.html(speech_html, height=0)

# Función para obtener reconocimiento de voz (STT) - Mejorado con más tiempo
def get_voice_input_component():
    """Componente para capturar voz del estudiante con más tiempo de grabación"""
    voice_html = """
    <div style="text-align: center; padding: 20px;">
        <button id="startBtn" style="padding: 15px 30px; font-size: 18px; background-color: #28a745; color: white; border: none; border-radius: 5px; cursor: pointer;">
            🎤 Mantén presionado para hablar
        </button>
        <button id="stopBtn" style="padding: 15px 30px; font-size: 18px; background-color: #dc3545; color: white; border: none; border-radius: 5px; cursor: pointer; margin-left: 10px; display: none;">
            ⏹️ Detener
        </button>
        <p id="status" style="margin-top: 15px; font-size: 16px; color: #666;"></p>
        <div id="transcriptBox" style="margin-top: 15px; padding: 15px; background-color: #f0f2f6; border-radius: 8px; min-height: 60px; display: none;">
            <p id="transcript" style="font-size: 18px; font-weight: bold; color: #1f77b4; margin: 0;"></p>
        </div>
        <input type="hidden" id="transcriptValue" value="">
    </div>
    <script>
        const startBtn = document.getElementById('startBtn');
        const stopBtn = document.getElementById('stopBtn');
        const status = document.getElementById('status');
        const transcript = document.getElementById('transcript');
        const transcriptBox = document.getElementById('transcriptBox');
        const transcriptValue = document.getElementById('transcriptValue');

        let recognition = null;
        let finalTranscript = '';
        let isRecording = false;

        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();
            recognition.lang = 'es-ES';
            recognition.continuous = true;  // Grabación continua
            recognition.interimResults = true;  // Mostrar resultados intermedios
            recognition.maxAlternatives = 1;

            startBtn.onclick = function() {
                if (!isRecording) {
                    finalTranscript = '';
                    recognition.start();
                    isRecording = true;
                    status.textContent = '🎤 Grabando... Habla ahora';
                    startBtn.style.display = 'none';
                    stopBtn.style.display = 'inline-block';
                    transcriptBox.style.display = 'block';
                    transcript.textContent = 'Esperando tu voz...';
                }
            };

            stopBtn.onclick = function() {
                if (isRecording) {
                    recognition.stop();
                    isRecording = false;
                }
            };

            recognition.onresult = function(event) {
                let interimTranscript = '';

                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const transcriptText = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {
                        finalTranscript += transcriptText + ' ';
                    } else {
                        interimTranscript += transcriptText;
                    }
                }

                transcript.textContent = finalTranscript + interimTranscript;
                transcriptValue.value = finalTranscript;

                // Enviar a Streamlit
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: finalTranscript.trim()
                }, '*');
            };

            recognition.onerror = function(event) {
                if (event.error === 'no-speech') {
                    status.textContent = '⚠️ No se detectó voz. Intenta de nuevo.';
                } else if (event.error === 'aborted') {
                    status.textContent = '✅ Grabación detenida';
                } else {
                    status.textContent = '❌ Error: ' + event.error;
                }
                isRecording = false;
                startBtn.style.display = 'inline-block';
                stopBtn.style.display = 'none';
            };

            recognition.onend = function() {
                if (isRecording) {
                    // Si se detuvo automáticamente pero queríamos seguir, reiniciar
                    recognition.start();
                } else {
                    status.textContent = '✅ Grabación completada: ' + finalTranscript;
                    startBtn.style.display = 'inline-block';
                    stopBtn.style.display = 'none';
                    startBtn.textContent = '🎤 Grabar otra vez';
                }
            };
        } else {
            status.textContent = '❌ Tu navegador no soporta reconocimiento de voz. Usa Chrome, Edge o Safari.';
            startBtn.disabled = true;
        }
    </script>
    """
    return components.html(voice_html, height=250)

# Inicializar estado de sesión
if "document_loaded" not in st.session_state:
    st.session_state.document_loaded = False
if "document_content" not in st.session_state:
    st.session_state.document_content = ""
if "questions" not in st.session_state:
    st.session_state.questions = []
if "current_question_index" not in st.session_state:
    st.session_state.current_question_index = 0
if "evaluation_history" not in st.session_state:
    st.session_state.evaluation_history = []
if "total_score" not in st.session_state:
    st.session_state.total_score = 0
if "show_evaluation" not in st.session_state:
    st.session_state.show_evaluation = False
if "current_evaluation" not in st.session_state:
    st.session_state.current_evaluation = None
if "voice_transcript" not in st.session_state:
    st.session_state.voice_transcript = ""

# Header
st.markdown('<div class="main-header">🎓 Profesor Virtual con IA 🤖</div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("📚 Panel de Control")

    # Información de la API
    api_key = os.getenv("OPENAI_API_KEY")
    if api_key:
        st.success("✅ API Key de OpenAI configurada")
    else:
        st.error("❌ No se encontró API Key de OpenAI")
        st.info("Configura OPENAI_API_KEY en tu archivo .env")

    st.markdown("---")

    # Configuración
    st.subheader("⚙️ Configuración")
    num_questions = st.slider("Número de preguntas", 1, 10, 5)
    difficulty = st.selectbox(
        "Nivel de dificultad",
        ["easy", "medium", "hard"],
        index=1,
        format_func=lambda x: {"easy": "Fácil", "medium": "Medio", "hard": "Difícil"}[x]
    )

    st.markdown("---")

    # Estadísticas
    if st.session_state.evaluation_history:
        st.subheader("📊 Estadísticas")
        total_questions = len(st.session_state.evaluation_history)
        correct_answers = sum(1 for e in st.session_state.evaluation_history if e.get("es_correcta", False))
        avg_score = sum(e.get("puntaje", 0) for e in st.session_state.evaluation_history) / total_questions

        st.metric("Preguntas respondidas", total_questions)
        st.metric("Respuestas correctas", correct_answers)
        st.metric("Puntuación promedio", f"{avg_score:.1f}/100")

        # Botón para reiniciar
        if st.button("🔄 Reiniciar sesión"):
            st.session_state.document_loaded = False
            st.session_state.document_content = ""
            st.session_state.questions = []
            st.session_state.current_question_index = 0
            st.session_state.evaluation_history = []
            st.session_state.total_score = 0
            st.session_state.show_evaluation = False
            st.session_state.current_evaluation = None
            st.rerun()

    st.markdown("---")
    st.markdown("### 👨‍💻 Desarrollado con IA")
    st.caption("Ing. Jorge Quintero")
    st.caption("lucho19q@gmail.com")

# Main content
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📄 Paso 1: Cargar Documento")

    st.info("""
    Sube un documento (PDF, TXT o DOCX) con el contenido que deseas estudiar.
    El profesor virtual generará preguntas basadas en este documento.
    """)

    uploaded_file = st.file_uploader(
        "Selecciona un archivo",
        type=["pdf", "txt", "docx"],
        help="Formatos soportados: PDF, TXT, DOCX"
    )

    if uploaded_file:
        if not st.session_state.document_loaded:
            with st.spinner("📖 Cargando documento..."):
                try:
                    loader = DocumentLoader()
                    content = loader.load_document(uploaded_file, uploaded_file.name)

                    if loader.validate_document_length(content):
                        st.session_state.document_content = content
                        st.session_state.document_loaded = True
                        st.success(f"✅ Documento cargado: {uploaded_file.name}")
                        st.info(f"📊 Longitud del documento: {len(content)} caracteres")

                        # Mostrar preview
                        with st.expander("👁️ Ver contenido del documento"):
                            st.text_area(
                                "Contenido",
                                content[:1000] + "..." if len(content) > 1000 else content,
                                height=200,
                                disabled=True
                            )
                    else:
                        st.error("❌ El documento es demasiado corto. Por favor, sube un documento con más contenido.")
                except Exception as e:
                    st.error(f"❌ Error al cargar el documento: {str(e)}")

with col2:
    st.header("❓ Paso 2: Generar Preguntas")

    if st.session_state.document_loaded:
        st.success("✅ Documento listo para generar preguntas")

        if not st.session_state.questions:
            if st.button("🎯 Generar preguntas", use_container_width=True):
                with st.spinner("🤔 Generando preguntas inteligentes..."):
                    try:
                        generator = QuestionGenerator()
                        questions = generator.generate_questions(
                            st.session_state.document_content,
                            num_questions=num_questions,
                            difficulty=difficulty
                        )
                        st.session_state.questions = questions
                        st.success(f"✅ Se generaron {len(questions)} preguntas")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Error al generar preguntas: {str(e)}")
        else:
            st.info(f"✅ {len(st.session_state.questions)} preguntas generadas")
            if st.button("🔄 Generar nuevas preguntas", use_container_width=True):
                st.session_state.questions = []
                st.session_state.current_question_index = 0
                st.session_state.evaluation_history = []
                st.session_state.show_evaluation = False
                st.session_state.current_evaluation = None
                st.rerun()
    else:
        st.warning("⚠️ Primero debes cargar un documento")

# Sección de preguntas y respuestas
if st.session_state.questions:
    st.markdown("---")
    st.header("🎯 Paso 3: Responde las Preguntas")

    current_idx = st.session_state.current_question_index

    if current_idx < len(st.session_state.questions):
        current_q = st.session_state.questions[current_idx]

        # Mostrar progreso
        progress = (current_idx) / len(st.session_state.questions)
        st.progress(progress, text=f"Pregunta {current_idx + 1} de {len(st.session_state.questions)}")

        # Mostrar pregunta con mejor contraste
        st.markdown(f"""
        <div class="question-box">
            <h3 style="color: #1f77b4;">Pregunta {current_idx + 1}</h3>
            <p style="font-size: 1.2rem; color: #2c2c2c; font-weight: 500;">{current_q.get("pregunta", "")}</p>
        </div>
        """, unsafe_allow_html=True)

        # Mostrar contexto adicional si está disponible
        if current_q.get("contexto"):
            st.info(f"📖 Contexto: {current_q.get('contexto')}")

        # Botón para leer pregunta en voz alta
        col_speak, col_space = st.columns([1, 3])
        with col_speak:
            if st.button("🔊 Escuchar pregunta", use_container_width=True):
                speak_text(current_q.get("pregunta", ""))

        # Si ya se mostró una evaluación, mostrarla y dar opción de continuar
        if st.session_state.show_evaluation and st.session_state.current_evaluation:
            evaluation = st.session_state.current_evaluation
            is_correct = evaluation.get("es_correcta", False)
            score = evaluation.get("puntaje", 0)
            feedback = evaluation.get("feedback", "")

            # Clase CSS según el resultado
            feedback_class = "feedback-correct" if is_correct else "feedback-incorrect"

            # Badge de puntaje
            if score >= 90:
                score_class = "score-excellent"
            elif score >= 70:
                score_class = "score-good"
            elif score >= 50:
                score_class = "score-regular"
            else:
                score_class = "score-poor"

            st.markdown(f'<div class="{feedback_class}">', unsafe_allow_html=True)
            st.markdown(f'<span class="score-badge {score_class}">Puntaje: {score}/100</span>', unsafe_allow_html=True)
            st.markdown(f'<p style="margin-top: 1rem; color: inherit; font-size: 1.1rem;">{feedback}</p>', unsafe_allow_html=True)
            st.markdown('</div>', unsafe_allow_html=True)

            # Botón para siguiente pregunta (siempre visible después de evaluar)
            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                if st.button("➡️ Continuar a la siguiente pregunta", use_container_width=True, type="primary"):
                    st.session_state.current_question_index += 1
                    st.session_state.show_evaluation = False
                    st.session_state.current_evaluation = None
                    st.rerun()

        else:
            # Tabs para respuesta por texto o voz
            tab1, tab2 = st.tabs(["✍️ Escribir respuesta", "🎤 Responder por voz"])

            with tab1:
                student_answer = st.text_area(
                    "Tu respuesta:",
                    height=150,
                    placeholder="Escribe tu respuesta aquí...",
                    key=f"text_answer_{current_idx}"
                )

                if st.button("📤 Enviar respuesta escrita", use_container_width=True, key=f"submit_text_{current_idx}"):
                    if student_answer.strip():
                        with st.spinner("🤖 Evaluando tu respuesta..."):
                            try:
                                evaluator = AnswerEvaluator()
                                evaluation = evaluator.evaluate_answer(
                                    question=current_q.get("pregunta", ""),
                                    student_answer=student_answer,
                                    expected_answer=current_q.get("respuesta_esperada", ""),
                                    keywords=current_q.get("palabras_clave", []),
                                    document_context=st.session_state.document_content
                                )

                                # Guardar evaluación
                                st.session_state.evaluation_history.append(evaluation)
                                st.session_state.show_evaluation = True
                                st.session_state.current_evaluation = evaluation

                                # Leer feedback en voz
                                feedback_speech = evaluator.format_feedback_for_speech(evaluation)
                                speak_text(feedback_speech)

                                # Recargar para mostrar evaluación
                                st.rerun()

                            except Exception as e:
                                st.error(f"❌ Error al evaluar: {str(e)}")
                    else:
                        st.warning("⚠️ Por favor, escribe una respuesta")

            with tab2:
                st.info("🎤 **Instrucciones:** Presiona 'Mantén presionado para hablar', habla tu respuesta completa, y luego presiona 'Detener' cuando termines.")

                # Componente de voz mejorado
                voice_result = get_voice_input_component()

                st.markdown("---")
                st.markdown("**Revisa y edita tu respuesta capturada:**")

                voice_answer = st.text_area(
                    "Tu respuesta por voz:",
                    height=120,
                    key=f"voice_answer_{current_idx}",
                    placeholder="Tu respuesta por voz aparecerá aquí. Puedes editarla antes de enviar.",
                    value=st.session_state.get("voice_transcript", "")
                )

                if st.button("📤 Enviar respuesta por voz", use_container_width=True, key=f"submit_voice_{current_idx}"):
                    if voice_answer and voice_answer.strip():
                        with st.spinner("🤖 Evaluando tu respuesta..."):
                            try:
                                evaluator = AnswerEvaluator()
                                evaluation = evaluator.evaluate_answer(
                                    question=current_q.get("pregunta", ""),
                                    student_answer=voice_answer,
                                    expected_answer=current_q.get("respuesta_esperada", ""),
                                    keywords=current_q.get("palabras_clave", []),
                                    document_context=st.session_state.document_content
                                )

                                # Guardar evaluación
                                st.session_state.evaluation_history.append(evaluation)
                                st.session_state.show_evaluation = True
                                st.session_state.current_evaluation = evaluation

                                # Leer feedback en voz
                                feedback_speech = evaluator.format_feedback_for_speech(evaluation)
                                speak_text(feedback_speech)

                                # Recargar para mostrar evaluación
                                st.rerun()

                            except Exception as e:
                                st.error(f"❌ Error al evaluar: {str(e)}")
                    else:
                        st.warning("⚠️ Por favor, graba tu respuesta o escríbela manualmente en el cuadro de texto")

    else:
        # Completado
        st.success("🎉 ¡Felicidades! Has completado todas las preguntas")

        if st.session_state.evaluation_history:
            # Resumen final
            total_questions = len(st.session_state.evaluation_history)
            correct_answers = sum(1 for e in st.session_state.evaluation_history if e.get("es_correcta", False))
            avg_score = sum(e.get("puntaje", 0) for e in st.session_state.evaluation_history) / total_questions

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total de preguntas", total_questions)
            with col2:
                st.metric("Respuestas correctas", f"{correct_answers}/{total_questions}")
            with col3:
                st.metric("Puntuación promedio", f"{avg_score:.1f}/100")

            # Mensaje de ánimo final
            if avg_score >= 90:
                final_message = "🏆 ¡Excelente trabajo! Dominas muy bien este tema."
            elif avg_score >= 70:
                final_message = "👏 ¡Muy bien! Tienes un buen entendimiento del material."
            elif avg_score >= 50:
                final_message = "📚 Bien hecho, pero hay espacio para mejorar. Sigue estudiando."
            else:
                final_message = "💪 No te desanimes. Revisa el material y vuelve a intentarlo."

            st.info(final_message)
            speak_text(final_message)

            # Mostrar historial
            with st.expander("📋 Ver historial de respuestas"):
                for idx, eval_item in enumerate(st.session_state.evaluation_history, 1):
                    st.markdown(f"**Pregunta {idx}**")
                    st.write(f"Puntaje: {eval_item.get('puntaje', 0)}/100")
                    st.write(f"Nivel: {eval_item.get('nivel', 'N/A')}")
                    st.write(f"Correcta: {'✅' if eval_item.get('es_correcta') else '❌'}")
                    st.markdown("---")

# Footer
st.markdown("---")
st.markdown("""
<div style="text-align: center; color: #666; padding: 2rem;">
    <p><strong>Profesor Virtual con IA</strong> - Desarrollado con Streamlit y OpenAI GPT-4</p>
    <p>Ing. Jorge Quintero | lucho19q@gmail.com</p>
</div>
""", unsafe_allow_html=True)
