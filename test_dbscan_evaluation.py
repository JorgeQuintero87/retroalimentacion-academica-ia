"""
Script de prueba para verificar detección de DBSCAN
"""
import json
import sys
from pathlib import Path

# Agregar path del proyecto
sys.path.insert(0, str(Path(__file__).parent))

from feedback.gpt_feedback import GPTFeedbackGenerator

def test_dbscan_detection():
    print("="*80)
    print("PRUEBA DE DETECCIÓN DE DBSCAN")
    print("="*80)

    # Cargar documento de prueba
    with open('test_dbscan_document.txt', 'r', encoding='utf-8') as f:
        document_content = f.read()

    print(f"\n✓ Documento cargado: {len(document_content)} caracteres")
    print(f"✓ Contiene 'DBSCAN': {'DBSCAN' in document_content}")
    print(f"✓ Contiene 'eps': {'eps' in document_content}")
    print(f"✓ Contiene 'min_samples': {'min_samples' in document_content}")
    print(f"✓ Contiene 'outliers': {'outliers' in document_content or 'outlier' in document_content}")

    # Cargar rúbrica de Fase 3
    rubric_path = Path("courses/machine_learning_fase3/rubrica_estructurada.json")
    with open(rubric_path, 'r', encoding='utf-8') as f:
        rubric_data = json.load(f)

    print(f"\n✓ Rúbrica cargada: {rubric_data['nombre_curso']}")
    print(f"✓ Total criterios: {len(rubric_data['criterios_evaluacion'])}")

    # Inicializar generador de feedback
    print("\n" + "="*80)
    print("INICIANDO EVALUACIÓN...")
    print("="*80 + "\n")

    generator = GPTFeedbackGenerator()

    # Evaluar documento
    result = generator.evaluate_document(
        document_content=document_content,
        rubric_data=rubric_data,
        relevant_sections=None,
        file_name="ejercicio2_dbscan.txt"  # Simular que el archivo indica ejercicio 2
    )

    # Mostrar resultados
    print("\n" + "="*80)
    print("RESULTADOS DE LA EVALUACIÓN")
    print("="*80)

    if result.get('success'):
        print(f"\n✓ Evaluación completada exitosamente")
        print(f"  Puntaje total: {result['total_score']}/{result['max_score']}")
        print(f"  Porcentaje: {(result['total_score']/result['max_score']*100):.1f}%")

        print(f"\n{'='*80}")
        print("RESULTADOS POR CRITERIO")
        print('='*80)

        for fb in result['criteria_feedbacks']:
            criterion_num = fb['criterion_number']
            criterion_name = fb['criterion_name']
            score = fb['score']
            max_score = fb['max_score']
            level = fb['level_achieved']

            print(f"\n📌 Criterio {criterion_num}: {criterion_name}")
            print(f"   Puntaje: {score}/{max_score} pts")
            print(f"   Nivel: {level.upper()}")

            # CRITERIO 2 (DBSCAN) - EL MÁS IMPORTANTE PARA ESTA PRUEBA
            if criterion_num == 2:
                print(f"\n   🔍 ANÁLISIS DETALLADO DEL CRITERIO 2 (DBSCAN):")
                print(f"   {'='*70}")

                if level == 'no_presentado':
                    print(f"   ❌ PROBLEMA: Sistema marcó como NO PRESENTADO")
                    print(f"   ❌ Esto es INCORRECTO - el código SÍ contiene DBSCAN")
                else:
                    print(f"   ✅ ÉXITO: Sistema detectó DBSCAN correctamente")
                    print(f"   ✅ Nivel alcanzado: {level.upper()}")

                print(f"\n   📝 Feedback recibido:")
                feedback_text = fb['feedback']
                # Mostrar primeros 500 caracteres
                print(f"   {feedback_text[:500]}...")

                print(f"\n   ✅ Aspectos cumplidos ({len(fb['aspects_met'])}):")
                for aspect in fb['aspects_met']:
                    print(f"      - {aspect}")

                print(f"\n   💡 Mejoras sugeridas ({len(fb['improvements'])}):")
                for improvement in fb['improvements']:
                    print(f"      - {improvement}")

        print(f"\n{'='*80}")
        print("RETROALIMENTACIÓN GENERAL")
        print('='*80)

        overall = result['overall_feedback']
        print(f"\n{overall['summary']}")

        print(f"\n✅ Fortalezas:")
        for strength in overall['strengths']:
            print(f"   - {strength}")

        print(f"\n⚠️ Áreas de mejora:")
        for area in overall['improvement_areas']:
            print(f"   - {area}")

        print(f"\n💬 Conclusión:")
        print(f"   {overall['conclusion']}")

        # DIAGNÓSTICO FINAL
        print(f"\n{'='*80}")
        print("DIAGNÓSTICO FINAL")
        print('='*80)

        criterio_2 = None
        for fb in result['criteria_feedbacks']:
            if fb['criterion_number'] == 2:
                criterio_2 = fb
                break

        if criterio_2:
            if criterio_2['level_achieved'] == 'no_presentado':
                print(f"\n❌ FALLÓ LA PRUEBA")
                print(f"   El sistema NO detectó DBSCAN a pesar de estar implementado")
                print(f"   Se requieren más correcciones en el código")
            elif criterio_2['score'] >= 42:  # Nivel medio o alto
                print(f"\n✅ PRUEBA EXITOSA")
                print(f"   El sistema detectó DBSCAN correctamente")
                print(f"   Puntaje: {criterio_2['score']}/{criterio_2['max_score']} pts")
                print(f"   Nivel: {criterio_2['level_achieved'].upper()}")
            else:
                print(f"\n⚠️ PRUEBA PARCIAL")
                print(f"   El sistema detectó DBSCAN pero dio puntaje bajo")
                print(f"   Puntaje: {criterio_2['score']}/{criterio_2['max_score']} pts")
                print(f"   Puede requerir ajustes en las instrucciones de evaluación")
        else:
            print(f"\n❌ ERROR: No se encontró evaluación del Criterio 2")

    else:
        print(f"\n✗ Error en la evaluación:")
        print(f"   {result.get('error', 'Error desconocido')}")

    print(f"\n{'='*80}\n")

if __name__ == "__main__":
    try:
        test_dbscan_detection()
    except Exception as e:
        print(f"\n❌ ERROR DURANTE LA PRUEBA:")
        print(f"   {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
