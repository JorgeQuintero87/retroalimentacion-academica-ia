"""
Procesador de Jupyter Notebooks (.ipynb)
Extrae código, markdown y outputs
"""
import nbformat
from nbconvert import MarkdownExporter
import json
from typing import Dict, List

class NotebookProcessor:
    """Procesa notebooks de Jupyter y extrae contenido estructurado"""

    def __init__(self):
        self.supported_formats = ['.ipynb']

    def extract_content(self, notebook_path: str) -> Dict[str, any]:
        """
        Extrae todo el contenido de un notebook

        Args:
            notebook_path: Ruta al archivo .ipynb

        Returns:
            Dict con contenido estructurado del notebook
        """
        try:
            # Leer notebook
            with open(notebook_path, 'r', encoding='utf-8') as f:
                nb = nbformat.read(f, as_version=4)

            cells_content = []
            code_cells = []
            markdown_cells = []
            full_text = ""

            # Procesar cada celda
            for i, cell in enumerate(nb.cells):
                cell_info = {
                    'index': i,
                    'type': cell.cell_type,
                    'source': cell.source
                }

                if cell.cell_type == 'code':
                    # Extraer código y outputs
                    code_cells.append(cell.source)

                    outputs = []
                    if hasattr(cell, 'outputs'):
                        for output in cell.outputs:
                            if hasattr(output, 'text'):
                                outputs.append(output.text)
                            elif hasattr(output, 'data'):
                                # Extraer texto de data (puede contener resultados)
                                if 'text/plain' in output.data:
                                    outputs.append(output.data['text/plain'])

                    cell_info['outputs'] = outputs
                    full_text += f"\n--- Código {i + 1} ---\n{cell.source}\n"

                    if outputs:
                        full_text += f"Output: {' '.join(outputs)}\n"

                elif cell.cell_type == 'markdown':
                    # Extraer markdown
                    markdown_cells.append(cell.source)
                    cell_info['rendered'] = cell.source
                    full_text += f"\n--- Markdown {i + 1} ---\n{cell.source}\n"

                cells_content.append(cell_info)

            return {
                'success': True,
                'cells': cells_content,
                'code_cells': code_cells,
                'markdown_cells': markdown_cells,
                'full_text': full_text,
                'total_cells': len(nb.cells),
                'metadata': nb.metadata if hasattr(nb, 'metadata') else {}
            }

        except Exception as e:
            return {
                'success': False,
                'error': str(e),
                'cells': [],
                'full_text': ''
            }

    def analyze_code_quality(self, code_cells: List[str]) -> Dict:
        """
        Analiza la calidad del código en el notebook

        Args:
            code_cells: Lista de celdas de código

        Returns:
            Dict con métricas de calidad
        """
        total_lines = 0
        has_imports = False
        has_functions = False
        has_classes = False
        has_comments = False
        libraries_used = set()

        common_ml_libs = ['pandas', 'numpy', 'sklearn', 'tensorflow', 'keras',
                         'torch', 'matplotlib', 'seaborn', 'scipy']

        for code in code_cells:
            lines = code.split('\n')
            total_lines += len(lines)

            for line in lines:
                line_stripped = line.strip()

                # Detectar imports
                if line_stripped.startswith('import ') or line_stripped.startswith('from '):
                    has_imports = True
                    # Extraer librería
                    for lib in common_ml_libs:
                        if lib in line_stripped:
                            libraries_used.add(lib)

                # Detectar definiciones
                if line_stripped.startswith('def '):
                    has_functions = True
                if line_stripped.startswith('class '):
                    has_classes = True

                # Detectar comentarios
                if '#' in line_stripped:
                    has_comments = True

        return {
            'total_lines': total_lines,
            'has_imports': has_imports,
            'has_functions': has_functions,
            'has_classes': has_classes,
            'has_comments': has_comments,
            'libraries_used': list(libraries_used),
            'is_ml_notebook': bool(libraries_used & set(common_ml_libs))
        }

    def extract_visualizations(self, cells: List[Dict]) -> List[str]:
        """
        Identifica celdas que generan visualizaciones

        Args:
            cells: Lista de celdas procesadas

        Returns:
            Lista de código que genera visualizaciones
        """
        viz_cells = []
        viz_keywords = ['plt.', 'plot(', 'sns.', 'seaborn', 'matplotlib',
                       'fig,', 'ax.', 'plotly', 'altair']

        for cell in cells:
            if cell['type'] == 'code':
                code = cell['source'].lower()
                if any(keyword in code for keyword in viz_keywords):
                    viz_cells.append(cell['source'])

        return viz_cells

    def process(self, notebook_path: str) -> Dict:
        """
        Procesa completamente un notebook extrayendo todo el contenido

        Args:
            notebook_path: Ruta al archivo .ipynb

        Returns:
            Dict con todo el contenido procesado
        """
        # Extraer contenido base
        extraction_result = self.extract_content(notebook_path)

        if not extraction_result['success']:
            return extraction_result

        # Analizar calidad del código
        code_quality = self.analyze_code_quality(extraction_result['code_cells'])

        # Extraer visualizaciones
        visualizations = self.extract_visualizations(extraction_result['cells'])

        return {
            'success': True,
            'full_text': extraction_result['full_text'],
            'cells': extraction_result['cells'],
            'code_cells': extraction_result['code_cells'],
            'markdown_cells': extraction_result['markdown_cells'],
            'total_cells': extraction_result['total_cells'],
            'code_quality': code_quality,
            'visualizations': visualizations,
            'metadata': extraction_result['metadata']
        }


if __name__ == "__main__":
    # Test del procesador
    # Crear un notebook simple de prueba
    nb = nbformat.v4.new_notebook()

    # Celda de markdown
    nb.cells.append(nbformat.v4.new_markdown_cell("# Test Notebook\nAnálisis de Machine Learning"))

    # Celda de código
    nb.cells.append(nbformat.v4.new_code_cell("import pandas as pd\nimport numpy as np\n\ndf = pd.read_csv('data.csv')"))

    # Guardar notebook de prueba
    with open('test_notebook.ipynb', 'w') as f:
        nbformat.write(nb, f)

    # Procesar
    processor = NotebookProcessor()
    result = processor.process('test_notebook.ipynb')

    if result['success']:
        print(f"✓ Notebook procesado exitosamente")
        print(f"  - Total celdas: {result['total_cells']}")
        print(f"  - Celdas de código: {len(result['code_cells'])}")
        print(f"  - Es notebook ML: {result['code_quality']['is_ml_notebook']}")
        print(f"  - Librerías usadas: {result['code_quality']['libraries_used']}")
    else:
        print(f"✗ Error: {result['error']}")
