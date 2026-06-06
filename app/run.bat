@echo off
REM ── SISTAC Web App — Script de inicio ──────────────────────────────────────
REM Ejecutar desde cualquier lugar: doble click o desde terminal
REM
REM Requisitos:
REM   1. Python 3.10+ instalado (py -3 disponible)
REM   2. pip install -r scripts/python/requirements.txt (desde raiz del proyecto)
REM   3. Archivo .env en la raiz del proyecto con ANTHROPIC_API_KEY=sk-ant-...

cd /d "%~dp0.."

echo.
echo  ██████╗ ██╗███████╗████████╗ █████╗  ██████╗
echo  ██╔══██╗██║██╔════╝╚══██╔══╝██╔══██╗██╔════╝
echo  ██████╔╝██║███████╗   ██║   ███████║██║
echo  ██╔══██╗██║╚════██║   ██║   ██╔══██║██║
echo  ██║  ██║██║███████║   ██║   ██║  ██║╚██████╗
echo  ╚═╝  ╚═╝╚═╝╚══════╝   ╚═╝   ╚═╝  ╚═╝ ╚═════╝
echo.
echo  Sistema Inteligente de Seleccion de Talento y Analisis Curricular
echo  http://localhost:8000
echo.

REM Verificar que existe el .env
if not exist ".env" (
    echo [WARN] No se encontro el archivo .env en la raiz del proyecto.
    echo        Copia .env.example a .env y configura tus API keys.
    echo        El sistema puede funcionar con C1 si tienes ANTHROPIC_API_KEY.
    echo.
)

REM Verificar si Python está instalado
where py >nul 2>nul
if errorlevel 1 (
    where python >nul 2>nul
    if errorlevel 1 (
        echo [ERROR] No se encontro Python en el sistema.
        echo         Por favor, descarga e instala Python 3.11 desde:
        echo         https://www.python.org/downloads/
        echo         Asegurate de marcar la casilla "Add python.exe to PATH" durante la instalacion.
        echo.
        pause
        exit /b 1
    )
)

REM Instalar/verificar todas las dependencias del proyecto
echo [INFO] Verificando e instalando dependencias (requirements.txt)...
py -3 -m pip install -r scripts/python/requirements.txt
if errorlevel 1 (
    echo [WARN] Fallo al usar 'py -3', intentando con 'python'...
    python -m pip install -r scripts/python/requirements.txt
)

REM Instalar el modelo de spaCy en español si falta
echo [INFO] Verificando modelo de spaCy en español (es_core_news_lg)...
py -3 -m spacy info es_core_news_lg >nul 2>nul
if errorlevel 1 (
    echo [INFO] Descargando modelo de spaCy en español...
    py -3 -m spacy download es_core_news_lg
    if errorlevel 1 (
        python -m spacy download es_core_news_lg
    )
)

REM Iniciar servidor
REM   --timeout-keep-alive 300  permite requests lentos (carga modelo embeddings)
REM   --workers 1               evita problemas de multiprocessing en Windows
echo.
echo [INFO] Iniciando servidor en http://localhost:8000
echo [INFO] Presiona Ctrl+C para detener
echo.

py -3 -m uvicorn app.main:app --reload --port 8000 --timeout-keep-alive 300 --workers 1
if errorlevel 1 (
    python -m uvicorn app.main:app --reload --port 8000 --timeout-keep-alive 300 --workers 1
)

pause
