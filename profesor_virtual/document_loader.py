"""
Módulo para cargar y procesar documentos
"""
import os
from typing import Optional
import PyPDF2
import docx
from io import BytesIO


class DocumentLoader:
    """Carga y extrae texto de diferentes tipos de documentos"""

    @staticmethod
    def load_pdf(file) -> str:
        """
        Extrae texto de un archivo PDF

        Args:
            file: Archivo PDF cargado

        Returns:
            str: Texto extraído del PDF
        """
        try:
            pdf_reader = PyPDF2.PdfReader(file)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error al leer PDF: {str(e)}")

    @staticmethod
    def load_txt(file) -> str:
        """
        Lee un archivo de texto plano

        Args:
            file: Archivo TXT cargado

        Returns:
            str: Contenido del archivo
        """
        try:
            content = file.read()
            if isinstance(content, bytes):
                content = content.decode('utf-8')
            return content.strip()
        except Exception as e:
            raise Exception(f"Error al leer archivo de texto: {str(e)}")

    @staticmethod
    def load_docx(file) -> str:
        """
        Extrae texto de un archivo DOCX

        Args:
            file: Archivo DOCX cargado

        Returns:
            str: Texto extraído del documento
        """
        try:
            doc = docx.Document(file)
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
        except Exception as e:
            raise Exception(f"Error al leer DOCX: {str(e)}")

    @staticmethod
    def load_document(file, filename: str) -> str:
        """
        Detecta el tipo de archivo y extrae el texto

        Args:
            file: Archivo cargado
            filename: Nombre del archivo

        Returns:
            str: Texto extraído
        """
        ext = os.path.splitext(filename)[1].lower()

        if ext == '.pdf':
            return DocumentLoader.load_pdf(file)
        elif ext == '.txt':
            return DocumentLoader.load_txt(file)
        elif ext == '.docx':
            return DocumentLoader.load_docx(file)
        else:
            raise ValueError(f"Tipo de archivo no soportado: {ext}")

    @staticmethod
    def validate_document_length(text: str, min_length: int = 100) -> bool:
        """
        Valida que el documento tenga suficiente contenido

        Args:
            text: Texto del documento
            min_length: Longitud mínima requerida

        Returns:
            bool: True si el documento es válido
        """
        return len(text.strip()) >= min_length
