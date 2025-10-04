"""
Script de prueba del sistema completo
Carga rúbricas desde PDF y las indexa en Pinecone
"""
import sys
import os

# Añadir directorio actual al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from vector_store.pinecone_manager import PineconeManager
from processors.rubric_processor import RubricProcessor

def test_rubric_extraction():
    """Prueba la extracción de rúbricas desde PDF"""
    print("=" * 60)
    print("TEST 1: Extracción de Rúbricas desde PDF")
    print("=" * 60)

    processor = RubricProcessor()

    # Test Machine Learning
    print("\n1. Procesando rúbrica de Machine Learning...")
    rubric_ml = processor.extract_rubric_from_pdf(
        "courses/machine_learning/Rúbrica de evaluación - Fase 2 - Componente práctico - Prácticas simuladas.pdf",
        "Machine Learning"
    )

    if rubric_ml['success']:
        print(f"   ✓ Rúbrica extraída exitosamente")
        print(f"   - Puntaje total: {rubric_ml['puntaje_total']}")
        print(f"   - Criterios encontrados: {len(rubric_ml['criterios_evaluacion'])}")

        print("\n   Criterios extraídos:")
        for criterio in rubric_ml['criterios_evaluacion']:
            print(f"   {criterio['numero']}. {criterio['nombre']}")
            print(f"      Max: {criterio['puntaje_maximo']} pts | Niveles: {len(criterio['niveles'])}")
    else:
        print(f"   ✗ Error: {rubric_ml['error']}")
        return False

    # Test Big Data
    print("\n2. Procesando rúbrica de Big Data Integration...")
    rubric_bd = processor.extract_rubric_from_pdf(
        "courses/big_data_integration/Evaluation Rubric - Stage 2 - Big Data Analytics and Machine Learning.pdf",
        "Big Data Integration"
    )

    if rubric_bd['success']:
        print(f"   ✓ Rúbrica extraída exitosamente")
        print(f"   - Criterios encontrados: {len(rubric_bd['criterios_evaluacion'])}")

        print("\n   Criterios extraídos:")
        for criterio in rubric_bd['criterios_evaluacion']:
            print(f"   {criterio['numero']}. {criterio['nombre'][:50]}...")
            print(f"      Max: {criterio['puntaje_maximo']} pts")
    else:
        print(f"   ✗ Error: {rubric_bd['error']}")
        return False

    return True

def test_pinecone_indexing():
    """Prueba la indexación en Pinecone"""
    print("\n" + "=" * 60)
    print("TEST 2: Indexación en Pinecone")
    print("=" * 60)

    try:
        manager = PineconeManager()

        print("\n1. Cargando rúbricas desde PDFs...")
        manager.load_all_rubrics(use_pdf=True)

        print("\n2. Verificando estadísticas del índice...")
        stats = manager.get_index_stats()
        print(f"   - Total vectores: {stats.get('total_vectors', 0)}")
        print(f"   - Namespaces: {stats.get('namespaces', {})}")

        print("\n✓ Indexación completada")
        return True

    except Exception as e:
        print(f"\n✗ Error en indexación: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    print("\n" + "=" * 60)
    print("PRUEBA COMPLETA DEL SISTEMA DE RETROALIMENTACIÓN")
    print("=" * 60 + "\n")

    # Test 1: Extracción de rúbricas
    if not test_rubric_extraction():
        print("\n✗ FALLO: No se pudieron extraer las rúbricas")
        return False

    # Test 2: Indexación en Pinecone
    if not test_pinecone_indexing():
        print("\n✗ FALLO: No se pudo indexar en Pinecone")
        return False

    # Resumen final
    print("\n" + "=" * 60)
    print("✓ TODOS LOS TESTS PASARON")
    print("=" * 60)
    print("\nEl sistema está listo para usar:")
    print("1. Las rúbricas se leen automáticamente desde PDFs")
    print("2. Los criterios están indexados en Pinecone")
    print("3. La app mostrará retroalimentación por criterios")
    print("\nEjecuta: python -m streamlit run app.py")
    print("=" * 60)

    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
