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

REM Instalar dependencias minimas si faltan
py -3 -c "import fastapi, uvicorn" 2>nul
if errorlevel 1 (
    echo [INFO] Instalando dependencias...
    py -3 -m pip install fastapi uvicorn python-multipart pdfplumber python-docx python-dotenv requests -q
)

REM Iniciar servidor
REM   --timeout-keep-alive 300  permite requests lentos (carga modelo embeddings)
REM   --workers 1               evita problemas de multiprocessing en Windows
echo [INFO] Iniciando servidor en http://localhost:8000
echo [INFO] Presiona Ctrl+C para detener
echo.

py -3 -m uvicorn app.main:app --reload --port 8000 --timeout-keep-alive 300 --workers 1

pause
