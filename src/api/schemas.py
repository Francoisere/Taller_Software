from pydantic import BaseModel, HttpUrl, Field
from typing import List, Dict, Any, Optional

class ScanRequest(BaseModel):
    url: str = Field(..., example="https://gob.cl", description="URL del sitio web a auditar")

class ScanResponse(BaseModel):
    target_url: str
    page_load_status: int
    verdict: str  # APROBADO | CON_OBSERVACIONES | RECHAZADO
    score: int
    verdict_summary: str
    pilares: Dict[str, Any]
    findings: List[Dict[str, Any]]
    technical_raw: Dict[str, Any]
    legal_disclaimer: str
