"""
Sistema de Retroalimentación Académica Automática
Interfaz principal con Streamlit
"""
import streamlit as st
import os
import json
from pathlib import Path

# Importar módulos del sistema
from processors.pdf_processor import PDFProcessor
from processors.image_processor import ImageProcessor
from processors.notebook_processor import NotebookProcessor
from vector_store.pinecone_manager import PineconeManager
from feedback.gpt_feedback import GPTFeedbackGenerator
from feedback.phase_validator import PhaseValidator
from feedback.document_type_validator import DocumentTypeValidator

# Configuración de la página
st.set_page_config(
    page_title="Sistema de Retroalimentación Académica",
    page_icon="📚",
    layout="wide"
)

# Inicializar sesión
if 'initialized' not in st.session_state:
    st.session_state.initialized = False
    st.session_state.pinecone_manager = None
    st.session_state.feedback_generator = None

def initialize_system():
    """Inicializa los componentes del sistema"""
    try:
        with st.spinner("Inicializando sistema..."):
            # Inicializar Pinecone
            st.session_state.pinecone_manager = PineconeManager()

            # Inicializar generador de feedback
            st.session_state.feedback_generator = GPTFeedbackGenerator()

            st.session_state.initialized = True
            st.success("✓ Sistema inicializado correctamente")
    except Exception as e:
        st.error(f"✗ Error inicializando sistema: {e}")
        st.stop()

def load_available_courses():
    """Carga la lista de cursos disponibles desde JSON estructurados"""
    courses_dir = Path("courses")
    courses = {}

    if not courses_dir.exists():
        return courses

    # Configuración de cursos
    course_configs = {
        'machine_learning': 'rubrica_estructurada.json',
        'machine_learning_fase3': 'rubrica_estructurada.json',
        'big_data_integration': 'rubrica_estructurada.json'
    }

    for course_folder, json_file in course_configs.items():
        course_path = courses_dir / course_folder
        rubric_json_path = course_path / json_file

        if rubric_json_path.exists():
            with open(rubric_json_path, 'r', encoding='utf-8') as f:
                rubric_data = json.load(f)
                courses[rubric_data['nombre_curso']] = {
                    'path': str(rubric_json_path),
                    'data': rubric_data,
                    'from_json': True
                }

    return courses

def process_document(file, file_type):
    """Procesa el documento subido según su tipo"""
    try:
        # Guardar archivo temporalmente
        temp_path = f"uploads/{file.name}"
        os.makedirs("uploads", exist_ok=True)

        with open(temp_path, 'wb') as f:
            f.write(file.getbuffer())

        # Procesar según tipo
        if file_type == 'pdf':
            processor = PDFProcessor()
            result = processor.process(temp_path)
            content = result.get('full_text', '')

        elif file_type in ['png', 'jpg', 'jpeg']:
            processor = ImageProcessor()
            result = processor.process(temp_path)
            content = result.get('full_text', '')

        elif file_type == 'ipynb':
            processor = NotebookProcessor()
            result = processor.process(temp_path)
            content = result.get('full_text', '')
        else:
            return None, "Formato no soportado"

        # Limpiar archivo temporal
        try:
            os.remove(temp_path)
        except:
            pass

        return content, None

    except Exception as e:
        return None, str(e)

def display_feedback(evaluation_result):
    """Muestra la retroalimentación de manera estructurada - SOPORTA NUEVA ESTRUCTURA"""

    # Encabezado con puntaje
    st.header(f"📊 Evaluación: {evaluation_result['course']}")

    # Determinar si es estructura nueva (criterios) o antigua (secciones)
    is_criteria_based = 'criteria_feedbacks' in evaluation_result
    feedbacks_list = evaluation_result.get('criteria_feedbacks' if is_criteria_based else 'section_feedbacks', [])

    # Métrica principal
    col1, col2, col3 = st.columns([2, 1, 1])
    with col1:
        score = evaluation_result['total_score']
        max_score = evaluation_result.get('max_score', 100)
        percentage = (score / max_score * 100) if max_score > 0 else 0

        color = "🟢" if percentage >= 70 else "🟡" if percentage >= 50 else "🔴"
        st.metric(
            label="Puntaje Final",
            value=f"{score}/{max_score}",
            delta=f"{color} {percentage:.1f}% - {'Aprobado' if percentage >= 60 else 'Necesita mejorar'}"
        )

    with col2:
        # Calcular criterios/secciones OK
        if is_criteria_based:
            items_ok = sum(1 for fb in feedbacks_list
                          if fb.get('max_score', 0) > 0 and fb.get('score', 0) / fb.get('max_score', 1) >= 0.6)
            label = "Criterios OK"
        else:
            items_ok = sum(1 for fb in feedbacks_list if fb.get('score', 0) >= 60)
            label = "Secciones OK"

        st.metric(label, f"{items_ok}/{len(feedbacks_list)}")

    with col3:
        st.metric("Timestamp", evaluation_result.get('timestamp', 'N/A'))

    st.divider()

    # Retroalimentación General
    st.subheader("📝 Retroalimentación General")
    overall = evaluation_result['overall_feedback']

    if overall.get('success'):
        st.write(overall['summary'])

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("**✓ Fortalezas:**")
            for strength in overall.get('strengths', []):
                st.markdown(f"- {strength}")

        with col2:
            st.markdown("**⚠ Áreas de Mejora:**")
            for area in overall.get('improvement_areas', []):
                st.markdown(f"- {area}")

        st.info(overall['conclusion'])

    st.divider()

    # Retroalimentación por Criterio/Sección
    if is_criteria_based:
        st.subheader("📑 Evaluación por Criterio")

        for i, criterion_fb in enumerate(feedbacks_list, 1):
            if not criterion_fb.get('success'):
                continue

            # Mostrar como "Criterio 1", "Criterio 2", etc.
            criterion_num = criterion_fb.get('criterion_number', i)
            criterion_name = criterion_fb.get('criterion_name', 'Sin nombre')
            score = criterion_fb.get('score', 0)
            max_score = criterion_fb.get('max_score', 0)
            level = criterion_fb.get('level_achieved', 'medio').upper()

            # Color según nivel
            if level.upper() == 'NO_PRESENTADO':
                level_color = "⚫"
                level_display = "NO PRESENTADO"
            elif level.upper() == 'ALTO' or level.upper() == 'HIGH':
                level_color = "🟢"
                level_display = level.upper()
            elif level.upper() == 'MEDIO' or level.upper() == 'AVERAGE':
                level_color = "🟡"
                level_display = level.upper()
            else:
                level_color = "🔴"
                level_display = level.upper()

            with st.expander(f"🔍 Criterio {criterion_num}: {criterion_name} - {score}/{max_score} pts ({level_color} {level_display})"):
                # Feedback del criterio
                st.write(criterion_fb['feedback'])

                # Aspectos cumplidos y mejoras
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**✅ Aspectos Cumplidos:**")
                    for aspect in criterion_fb.get('aspects_met', []):
                        st.markdown(f"- {aspect}")

                with col2:
                    st.markdown("**💡 Sugerencias de Mejora:**")
                    for improvement in criterion_fb.get('improvements', []):
                        st.markdown(f"- {improvement}")

    else:
        # ESTRUCTURA ANTIGUA: Secciones
        st.subheader("📑 Evaluación por Sección")

        for i, section_fb in enumerate(feedbacks_list, 1):
            if not section_fb.get('success'):
                continue

            with st.expander(f"🔍 {section_fb['section']} - {section_fb['score']}/100 (Peso: {section_fb['weight']}%)"):
                # Feedback de la sección
                st.write(section_fb['feedback'])

                # Criterios cumplidos/no cumplidos
                col1, col2 = st.columns(2)

                with col1:
                    st.markdown("**✅ Criterios Cumplidos:**")
                    for criteria in section_fb.get('criteria_met', []):
                        st.markdown(f"- {criteria}")

                with col2:
                    st.markdown("**❌ Criterios No Cumplidos:**")
                    for criteria in section_fb.get('criteria_not_met', []):
                        st.markdown(f"- {criteria}")

                # Sugerencias de mejora
                if section_fb.get('improvements'):
                    st.markdown("**💡 Sugerencias de Mejora:**")
                    for improvement in section_fb['improvements']:
                        st.markdown(f"- {improvement}")

def main():
    """Función principal de la aplicación"""

    # Título
    st.title("📚 Sistema de Retroalimentación Académica")

    # FIRMA PROFESIONAL - MUY VISIBLE
    st.markdown("""
    <div style='background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                padding: 20px;
                border-radius: 10px;
                text-align: center;
                margin-bottom: 20px;
                box-shadow: 0 4px 6px rgba(0,0,0,0.1);'>
        <h3 style='color: white; margin: 0; font-size: 24px;'>
            💻 Desarrollado por: <strong>Ing. Jorge Quintero</strong>
        </h3>
        <p style='color: #e0e0e0; margin: 10px 0 0 0; font-size: 18px;'>
            📧 Contacto: <a href='mailto:lucho19q@gmail.com' style='color: #ffd700; text-decoration: none; font-weight: bold;'>lucho19q@gmail.com</a>
        </p>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Inicializar sistema
    if not st.session_state.initialized:
        initialize_system()

    # Sidebar - Menú de cursos
    st.sidebar.header("⚙ Configuración")

    # FIRMA EN SIDEBAR
    st.sidebar.markdown("""
    ---
    ### 👨‍💻 Desarrollador
    **Ing. Jorge Quintero**

    📧 [lucho19q@gmail.com](mailto:lucho19q@gmail.com)

    🤖 **Desarrollado con:**
    - Claude AI (Anthropic)

    🔧 **Tecnologías:**
    - GPT-4o-mini
    - Pinecone Vector DB
    - Tesseract OCR
    - Streamlit
    ---
    """)

    # Opción: Nuevo curso o curso existente
    mode = st.sidebar.radio(
        "Modo de operación:",
        ["Evaluar con curso existente", "Crear nuevo curso"]
    )

    if mode == "Evaluar con curso existente":
        # Cargar cursos disponibles
        courses = load_available_courses()

        if not courses:
            st.sidebar.warning("No hay cursos configurados. Crea uno nuevo.")
            st.stop()

        # Seleccionar curso
        selected_course_name = st.sidebar.selectbox(
            "Selecciona un curso:",
            list(courses.keys())
        )

        selected_course = courses[selected_course_name]
        rubric_data = selected_course['data']

        # Mostrar información del curso
        st.sidebar.success(f"✓ Curso: {selected_course_name}")

        # Determinar si es estructura nueva (criterios) o antigua (secciones)
        if 'criterios_evaluacion' in rubric_data:
            num_items = len(rubric_data['criterios_evaluacion'])
            label = "Criterios"
        else:
            num_items = len(rubric_data.get('condiciones_entrega', []))
            label = "Secciones"

        st.sidebar.info(f"📋 {label}: {num_items}")

        # Botón para recargar rúbricas en Pinecone
        if st.sidebar.button("🔄 Recargar Rúbricas en Pinecone"):
            with st.spinner("Cargando rúbricas..."):
                st.session_state.pinecone_manager.load_all_rubrics()
                st.sidebar.success("✓ Rúbricas recargadas")

        st.divider()

        # Área principal - Subir documento
        st.header(f"📤 Subir Documento para: {selected_course_name}")

        uploaded_file = st.file_uploader(
            "Selecciona el documento del estudiante:",
            type=['pdf', 'png', 'jpg', 'jpeg', 'ipynb'],
            help="Formatos soportados: PDF, imágenes (PNG/JPG), Jupyter Notebooks (.ipynb)"
        )

        if uploaded_file:
            # Detectar tipo de archivo
            file_extension = uploaded_file.name.split('.')[-1].lower()

            st.info(f"📄 Archivo: {uploaded_file.name} ({file_extension.upper()})")

            # Botón para evaluar
            if st.button("🚀 Evaluar Documento", type="primary"):

                # Procesar documento
                with st.spinner("Procesando documento..."):
                    content, error = process_document(uploaded_file, file_extension)

                if error:
                    st.error(f"✗ Error procesando documento: {error}")
                    st.stop()

                if not content or len(content.strip()) < 50:
                    st.warning("⚠ El documento parece estar vacío o no se pudo extraer texto.")
                    st.stop()

                st.success(f"✓ Documento procesado: {len(content)} caracteres extraídos")

                # VALIDACIÓN 1: Tipo de Documento - Prevenir calificar guías/instrucciones
                with st.spinner("🔍 Validando que el documento sea una entrega del estudiante..."):
                    type_validator = DocumentTypeValidator()
                    type_result = type_validator.validate_is_student_work(content)

                    # Mostrar resultado de validación de tipo
                    if type_result['is_student_work']:
                        st.success("✓ Documento validado: Es una entrega de estudiante")
                    else:
                        # Si NO es trabajo del estudiante, BLOQUEAR
                        confidence = type_result['confidence']

                        if confidence in ['alta', 'media']:
                            # Confianza alta/media: BLOQUEAR
                            st.error("❌ " + type_result['recommendation'])

                            # Mostrar explicación detallada
                            with st.expander("📋 Ver detalles de validación", expanded=True):
                                st.write("**Explicación:**")
                                st.write(type_result['explanation'])

                                st.write(f"**Tipo de documento detectado:** `{type_result['document_type']}`")
                                st.write(f"**Confianza:** `{type_result['confidence']}`")

                                col1, col2 = st.columns(2)

                                with col1:
                                    st.write("**📖 Evidencias de que es GUÍA/INSTRUCCIONES:**")
                                    for evidence in type_result['evidence_guide']:
                                        st.markdown(f"- {evidence}")

                                with col2:
                                    st.write("**📝 Evidencias de que es TRABAJO del estudiante:**")
                                    if type_result['evidence_student_work']:
                                        for evidence in type_result['evidence_student_work']:
                                            st.markdown(f"- {evidence}")
                                    else:
                                        st.markdown("- *(Ninguna evidencia encontrada)*")

                            st.warning("⚠️ **La evaluación ha sido bloqueada.** Este documento parece ser una guía de actividad o instrucciones, NO una entrega real del estudiante. Por favor, suba el trabajo desarrollado por el estudiante.")
                            st.stop()  # Detener ejecución
                        else:
                            # Confianza baja: ADVERTENCIA pero permitir continuar
                            st.warning("⚠️ " + type_result['recommendation'])

                # VALIDACIÓN 2: Fase - Prevenir evaluación cruzada
                with st.spinner("🔍 Validando correspondencia con la fase seleccionada..."):
                    validator = PhaseValidator()
                    validation_result = validator.validate_document_phase(content, rubric_data)

                    # Mostrar resultado de validación
                    if validation_result['is_valid']:
                        st.success(validation_result['recommendation'])
                    else:
                        # Si NO es válido, mostrar advertencia/error según confianza
                        confidence = validation_result['confidence']

                        if confidence in ['alta', 'media']:
                            # Confianza alta/media: BLOQUEAR evaluación
                            st.error(validation_result['recommendation'])

                            # Mostrar explicación detallada
                            with st.expander("📋 Ver detalles de validación", expanded=True):
                                st.write("**Explicación:**")
                                st.write(validation_result['explanation'])

                                col1, col2 = st.columns(2)

                                with col1:
                                    st.write("**🎯 Temas esperados para esta fase:**")
                                    for topic in validation_result['expected_topics'][:5]:
                                        st.markdown(f"- {topic}")

                                with col2:
                                    st.write("**📝 Temas encontrados en el documento:**")
                                    for topic in validation_result['found_topics']:
                                        st.markdown(f"- {topic}")

                                if validation_result['phase_mismatch']:
                                    st.info(f"💡 **Sugerencia**: Este documento parece corresponder a **'{validation_result['phase_mismatch']}'**. Por favor, selecciona esa fase en lugar de '{rubric_data.get('fase', 'esta fase')}'.")

                            st.warning("⚠️ **La evaluación ha sido bloqueada para evitar resultados incorrectos.** Por favor, verifica que hayas seleccionado la fase correcta que corresponde a tu documento.")
                            st.stop()  # Detener ejecución
                        else:
                            # Confianza baja: ADVERTENCIA pero permitir continuar
                            st.warning(validation_result['recommendation'])
                            st.info("⚠️ La validación tiene confianza baja. Procede con precaución. Si sabes que el documento corresponde a esta fase, puedes continuar con la evaluación.")

                # Buscar secciones relevantes en Pinecone (opcional)
                with st.spinner("Analizando relevancia con rúbrica..."):
                    relevant_sections = st.session_state.pinecone_manager.search_relevant_criteria(
                        content, selected_course_name, top_k=5
                    )

                # Generar retroalimentación
                with st.spinner("Generando retroalimentación con GPT..."):
                    evaluation_result = st.session_state.feedback_generator.evaluate_document(
                        document_content=content,
                        rubric_data=rubric_data,
                        relevant_sections=relevant_sections,
                        file_name=uploaded_file.name  # NUEVO: Pasar nombre del archivo
                    )

                # Mostrar resultados
                if evaluation_result.get('success'):
                    st.divider()
                    display_feedback(evaluation_result)

                    # Opción para descargar reporte
                    st.divider()
                    report_json = json.dumps(evaluation_result, indent=2, ensure_ascii=False)
                    st.download_button(
                        label="📥 Descargar Reporte (JSON)",
                        data=report_json,
                        file_name=f"evaluacion_{selected_course_name.replace(' ', '_')}_{uploaded_file.name}.json",
                        mime="application/json"
                    )
                else:
                    st.error("✗ Error generando retroalimentación")

    else:
        # Modo: Crear nuevo curso
        st.header("➕ Crear Nuevo Curso")
        st.info("Funcionalidad en desarrollo. Por ahora, crea manualmente el archivo `condiciones.json` en `courses/nombre_curso/`")

    # FOOTER - FIRMA PROFESIONAL
    st.markdown("---")
    st.markdown("""
    <div style='background-color: #f0f2f6;
                padding: 15px;
                border-radius: 8px;
                text-align: center;
                margin-top: 30px;'>
        <p style='margin: 0; color: #555; font-size: 16px;'>
            <strong>Sistema desarrollado por:</strong> Ing. Jorge Quintero
        </p>
        <p style='margin: 5px 0 0 0; color: #666; font-size: 14px;'>
            📧 <a href='mailto:lucho19q@gmail.com' style='color: #667eea; text-decoration: none;'>lucho19q@gmail.com</a>
        </p>
        <p style='margin: 5px 0 0 0; color: #888; font-size: 13px;'>
            🤖 Desarrollado con asistencia de <strong>Claude AI (Anthropic)</strong>
            <br>
            🚀 Powered by: GPT-4o-mini • Pinecone • Tesseract OCR • Streamlit
        </p>
    </div>
    """, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
