@echo off
echo ========================================
echo Sistema de Retroalimentacion Academica
echo ========================================
echo.

REM Activar entorno virtual si existe
if exist venv\Scripts\activate.bat (
    echo Activando entorno virtual...
    call venv\Scripts\activate.bat
)

REM Verificar dependencias
echo Verificando dependencias...
python -c "import streamlit, pinecone, openai" 2>nul
if errorlevel 1 (
    echo.
    echo [ERROR] Faltan dependencias. Instalando...
    pip install -r requirements.txt
)

echo.
echo Iniciando aplicacion Streamlit...
echo Abre tu navegador en: http://localhost:8501
echo.
echo Presiona Ctrl+C para detener
echo ========================================
echo.

streamlit run app.py

pause
