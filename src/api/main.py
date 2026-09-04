import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse

from src.api.schemas import ScanRequest, ScanResponse
from src.scanner.inspector import WebInspector
from src.scanner.rules_engine import RulesEngine

app = FastAPI(
    title="Plataforma de Auditoría de Cumplimiento de Datos Personales (Chile)",
    description="API de escaneo pasivo y evaluación normativa binaria para la Ley N° 19.628 y Nueva Ley de Protección de Datos Personales de Chile.",
    version="1.0.0"
)

# Configurar CORS para permitir peticiones desde cualquier origen (incluyendo bookmarklets y extensiones)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inicializar inspector pasivo
inspector = WebInspector(timeout_ms=25000)

@app.get("/api/v1/health")
async def health_check():
    return {"status": "ok", "service": "Audit Scanner Microservice", "version": "1.0.0"}

@app.post("/api/v1/scan", response_model=ScanResponse)
async def run_scan(request: ScanRequest):
    """
    Ejecuta una auditoría completa de una URL mediante Playwright y aplica el motor de reglas de cumplimiento legal.
    """
    url = request.url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="La URL provista no es válida.")

    try:
        raw_inspection = await inspector.scan_url(url)
        audit_result = RulesEngine.evaluate(raw_inspection)
        return audit_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante el escaneo: {str(e)}")

@app.get("/api/v1/scan")
async def run_scan_get(url: str = Query(..., description="URL a auditar vía GET (útil para Bookmarklets)")):
    """
    Endpoint GET para invocar auditorías fácilmente desde botones de navegador o Bookmarklets.
    """
    url = url.strip()
    if not url:
        raise HTTPException(status_code=400, detail="Se requiere el parámetro 'url'.")

    try:
        raw_inspection = await inspector.scan_url(url)
        audit_result = RulesEngine.evaluate(raw_inspection)
        return audit_result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error durante el escaneo: {str(e)}")

# Montar archivos estáticos de la interfaz web en la raíz "/" (debe ir después de los endpoints de la API)
ui_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ui")
if os.path.exists(ui_dir):
    app.mount("/", StaticFiles(directory=ui_dir, html=True), name="ui")

