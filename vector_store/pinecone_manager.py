"""
Gestor de Pinecone Vector Store
Maneja embeddings y búsqueda semántica de rúbricas
"""
from pinecone import Pinecone, ServerlessSpec
from openai import OpenAI
import json
import os
from typing import List, Dict
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class PineconeManager:
    """Gestiona la indexación y búsqueda en Pinecone"""

    def __init__(self):
        """Inicializa conexión con Pinecone y OpenAI"""
        self.pinecone_api_key = os.getenv('PINECONE_API_KEY')
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.index_name = os.getenv('INDEX_NAME', 'rubricamachine')
        self.namespace = os.getenv('NAMESPACE', 'solomachine')

        # Inicializar clientes
        self.pc = Pinecone(api_key=self.pinecone_api_key)
        self.openai_client = OpenAI(api_key=self.openai_api_key)

        # Dimensión de embeddings (text-embedding-3-large = 3072)
        # IMPORTANTE: Tu índice 'rubricamachine' está configurado para 3072 dimensiones
        self.embedding_dimension = 3072
        self.embedding_model = "text-embedding-3-large"

        # Conectar o crear índice
        self.index = self._get_or_create_index()

    def _get_or_create_index(self):
        """Obtiene el índice existente o crea uno nuevo"""
        try:
            # Verificar si el índice existe
            existing_indexes = self.pc.list_indexes()

            if self.index_name not in [idx.name for idx in existing_indexes]:
                print(f"[INIT] Creando nuevo índice: {self.index_name}")

                # Crear índice con especificación serverless
                self.pc.create_index(
                    name=self.index_name,
                    dimension=self.embedding_dimension,
                    metric='cosine',
                    spec=ServerlessSpec(
                        cloud='aws',
                        region='us-east-1'
                    )
                )
                print(f"✓ Índice creado exitosamente")
            else:
                print(f"✓ Índice '{self.index_name}' ya existe")

            return self.pc.Index(self.index_name)

        except Exception as e:
            print(f"✗ Error creando/accediendo al índice: {e}")
            raise

    def create_embedding(self, text: str) -> List[float]:
        """
        Crea embedding de texto usando OpenAI

        Args:
            text: Texto a convertir en embedding

        Returns:
            Vector embedding
        """
        try:
            response = self.openai_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding

        except Exception as e:
            print(f"✗ Error creando embedding: {e}")
            return [0.0] * self.embedding_dimension

    def index_rubric(self, course_name: str, rubric_data: Dict):
        """
        Indexa una rúbrica completa en Pinecone
        Soporta NUEVA estructura con criterios de evaluación

        Args:
            course_name: Nombre del curso
            rubric_data: Datos de la rúbrica
        """
        try:
            vectors_to_upsert = []

            # NUEVA ESTRUCTURA: criterios_evaluacion (desde PDF)
            if 'criterios_evaluacion' in rubric_data:
                for i, criterio in enumerate(rubric_data['criterios_evaluacion']):
                    # Crear texto descriptivo del criterio
                    niveles_text = '\n'.join([
                        f"  - {nivel['nivel'].upper()}: {nivel['descripcion'][:150]} ({nivel['puntaje_minimo']}-{nivel['puntaje_maximo']} pts)"
                        for nivel in criterio.get('niveles', [])
                    ])

                    criterion_text = f"""
Curso: {course_name}
Criterio {criterio['numero']}: {criterio['nombre']}
Puntaje máximo: {criterio['puntaje_maximo']} puntos

Niveles de desempeño:
{niveles_text}

Descripción: {criterio.get('descripcion', '')}
"""

                    # Crear embedding
                    embedding = self.create_embedding(criterion_text)

                    # Preparar metadatos
                    metadata = {
                        'course': course_name,
                        'criterion_number': criterio['numero'],
                        'criterion_name': criterio['nombre'],
                        'max_score': criterio['puntaje_maximo'],
                        'levels': json.dumps(criterio['niveles'], ensure_ascii=False)
                    }

                    # ID único para este criterio
                    vector_id = f"{course_name.lower().replace(' ', '_')}_criterio_{i}"

                    vectors_to_upsert.append({
                        'id': vector_id,
                        'values': embedding,
                        'metadata': metadata
                    })

                print(f"✓ Rúbrica de '{course_name}' indexada: {len(vectors_to_upsert)} criterios")

            # ESTRUCTURA ANTIGUA: condiciones_entrega (compatibilidad)
            elif 'condiciones_entrega' in rubric_data:
                for i, seccion in enumerate(rubric_data['condiciones_entrega']):
                    criterios_text = '\n'.join([f"- {c}" for c in seccion['criterios']])

                    section_text = f"""
Curso: {course_name}
Sección: {seccion['seccion']}
Peso: {seccion['peso']}%
Criterios de evaluación:
{criterios_text}
"""

                    embedding = self.create_embedding(section_text)

                    metadata = {
                        'course': course_name,
                        'section': seccion['seccion'],
                        'weight': seccion['peso'],
                        'criteria_count': len(seccion['criterios']),
                        'criteria': json.dumps(seccion['criterios'], ensure_ascii=False)
                    }

                    vector_id = f"{course_name.lower().replace(' ', '_')}_section_{i}"

                    vectors_to_upsert.append({
                        'id': vector_id,
                        'values': embedding,
                        'metadata': metadata
                    })

                print(f"✓ Rúbrica de '{course_name}' indexada: {len(vectors_to_upsert)} secciones")

            # Insertar en Pinecone
            if vectors_to_upsert:
                self.index.upsert(
                    vectors=vectors_to_upsert,
                    namespace=self.namespace
                )
            else:
                print(f"⚠ No se encontraron criterios en la rúbrica de '{course_name}'")

        except Exception as e:
            print(f"✗ Error indexando rúbrica: {e}")
            raise

    def search_relevant_criteria(self, document_text: str, course_name: str, top_k: int = 5) -> List[Dict]:
        """
        Busca criterios relevantes para un documento

        Args:
            document_text: Texto del documento del estudiante
            course_name: Nombre del curso
            top_k: Número de resultados a retornar

        Returns:
            Lista de criterios relevantes con scores
        """
        try:
            # Crear embedding del documento
            query_embedding = self.create_embedding(document_text)

            # Buscar en Pinecone
            results = self.index.query(
                vector=query_embedding,
                top_k=top_k,
                namespace=self.namespace,
                filter={'course': course_name},
                include_metadata=True
            )

            # Procesar resultados
            relevant_criteria = []
            for match in results['matches']:
                relevant_criteria.append({
                    'section': match['metadata']['section'],
                    'weight': match['metadata']['weight'],
                    'criteria': json.loads(match['metadata']['criteria']),
                    'relevance_score': match['score']
                })

            return relevant_criteria

        except Exception as e:
            print(f"✗ Error buscando criterios: {e}")
            return []

    def load_all_rubrics(self, courses_dir: str = 'courses', use_pdf: bool = False):
        """
        Carga todas las rúbricas desde el directorio de cursos
        NUEVA OPCIÓN: Leer directamente desde PDFs si use_pdf=True

        Args:
            courses_dir: Directorio donde están las carpetas de cursos
            use_pdf: Si True, busca archivos PDF de rúbricas en vez de JSON
        """
        try:
            # Obtener directorio base del proyecto
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            courses_path = os.path.join(base_dir, courses_dir)

            print(f"[LOAD] Cargando rúbricas desde: {courses_path}")
            print(f"       Modo: {'PDFs automáticos' if use_pdf else 'JSON manual'}")

            if use_pdf:
                # NUEVO: Cargar desde PDFs automáticamente
                import sys
                # Agregar directorio padre al path
                parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
                if parent_dir not in sys.path:
                    sys.path.insert(0, parent_dir)

                from processors.rubric_processor import RubricProcessor
                rubric_processor = RubricProcessor()

                course_configs = {
                    'machine_learning': {
                        'name': 'Machine Learning',
                        'rubric_pdf': 'Rúbrica de evaluación - Fase 2 - Componente práctico - Prácticas simuladas.pdf'
                    },
                    'big_data_integration': {
                        'name': 'Big Data Integration',
                        'rubric_pdf': 'Evaluation Rubric - Stage 2 - Big Data Analytics and Machine Learning.pdf'
                    }
                }

                for course_folder, config in course_configs.items():
                    course_path = os.path.join(courses_path, course_folder)
                    rubric_pdf_path = os.path.join(course_path, config['rubric_pdf'])

                    if os.path.exists(rubric_pdf_path):
                        print(f"  - Procesando PDF: {course_folder}")

                        # Procesar PDF y extraer rúbrica
                        rubric_data = rubric_processor.extract_rubric_from_pdf(
                            rubric_pdf_path,
                            config['name']
                        )

                        if rubric_data['success']:
                            # Indexar en Pinecone
                            self.index_rubric(config['name'], rubric_data)
                        else:
                            print(f"    ✗ Error procesando PDF: {rubric_data.get('error')}")
                    else:
                        print(f"    ⚠ No se encontró: {config['rubric_pdf']}")

            else:
                # CARGAR DESDE JSON ESTRUCTURADOS
                course_configs = {
                    'machine_learning': 'rubrica_estructurada.json',
                    'big_data_integration': 'rubrica_estructurada.json'
                }

                for course_folder, json_file in course_configs.items():
                    course_path = os.path.join(courses_path, course_folder)
                    rubric_json_path = os.path.join(course_path, json_file)

                    if os.path.exists(rubric_json_path):
                        print(f"  - Procesando JSON: {course_folder}")

                        # Leer rúbrica
                        with open(rubric_json_path, 'r', encoding='utf-8') as f:
                            rubric_data = json.load(f)

                        # Indexar en Pinecone
                        self.index_rubric(rubric_data['nombre_curso'], rubric_data)

            print(f"✓ Todas las rúbricas cargadas en Pinecone")

        except Exception as e:
            print(f"✗ Error cargando rúbricas: {e}")
            raise

    def get_index_stats(self) -> Dict:
        """Obtiene estadísticas del índice"""
        try:
            stats = self.index.describe_index_stats()
            return {
                'total_vectors': stats.total_vector_count,
                'namespaces': stats.namespaces
            }
        except Exception as e:
            print(f"✗ Error obteniendo estadísticas: {e}")
            return {}


if __name__ == "__main__":
    # Test del gestor de Pinecone
    print("=== Test Pinecone Manager ===\n")

    manager = PineconeManager()

    # Cargar todas las rúbricas
    print("\n1. Cargando rúbricas...")
    manager.load_all_rubrics()

    # Mostrar estadísticas
    print("\n2. Estadísticas del índice:")
    stats = manager.get_index_stats()
    print(f"   - Total vectores: {stats.get('total_vectors', 0)}")
    print(f"   - Namespaces: {stats.get('namespaces', {})}")

    # Test de búsqueda
    print("\n3. Test de búsqueda:")
    test_text = "Implementé un pipeline de ETL usando PySpark para procesar datos de Hadoop"
    results = manager.search_relevant_criteria(test_text, "Big Data Integration", top_k=3)

    print(f"   Resultados para: '{test_text[:50]}...'")
    for i, result in enumerate(results, 1):
        print(f"\n   {i}. Sección: {result['section']}")
        print(f"      Peso: {result['weight']}%")
        print(f"      Relevancia: {result['relevance_score']:.2f}")
        print(f"      Criterios: {len(result['criteria'])}")

    print("\n✓ Test completado")
