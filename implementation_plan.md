# Plan de Implementación - Fase 1: Cimientos, Reglas Normativas y PoC de Extracción Web

Este documento detalla la estrategia de implementación para la **Fase 1** de la Plataforma de Auditoría de Cumplimiento de Datos Personales (Chile), transformando los requerimientos de `Roadmap.md` en una Prueba de Concepto (PoC) funcional, dockerizada y lista para pruebas.

---

## 1. Mapeo Normativo y Matriz de Reglas de Cumplimiento (Chile)

Basándonos en la **Ley N° 19.628** y la **Nueva Ley de Protección de Datos Personales de Chile (Boletín 11144-07 / principio de responsabilidad proactiva y consentimiento transparente)**, hemos traducido los aspectos legales en 3 pilares verificables mediante inspección pasiva (caja negra):

| Pilar Verificable | Criterio Determinista Binario | Evaluación de Cumplimiento |
| :--- | :--- | :--- |
| **1. Política de Privacidad** | - Enlace visible en Footer/Header (selectores `/privacidad`, `/politica-de-privacidad`, `privacy-policy`, `aviso-legal`).<br>- Código de respuesta HTTP = 200.<br>- Contenido textual contiene palabras clave esenciales (*titular*, *responsable*, *derechos*, *tratamiento*, *finalidad*). | **Cumple:** Enlace activo, accesible y válido.<br>**Falla:** Enlace roto (404/500), inaccesible o ausente. |
| **2. Canales de Derechos ARCO** | - Presencia de canales de contacto formales para Acceso, Rectificación, Cancelación u Oposición (correo electrónico tipo `privacidad@...`, `contacto@...`, formularios web o mención explícita de derechos ARCO). | **Cumple:** Canal ARCO explícito detectado.<br>**Advertencia:** Canal de contacto genérico.<br>**Falla:** Sin canal de contacto. |
| **3. Consentimiento Previo y Cookies** | - Intercepción de cookies y peticiones HTTP de terceros (ej. Google Analytics `_ga`, Meta Pixel `_fbp`, Hotjar `_hj`, TikTok Pixel) **antes** de que el usuario otorgue consentimiento. | **Cumple:** 0 trackers de 3ros activos al cargar.<br>**Falla:** Trackers/Cookies de rastreo inyectados sin consentimiento previo. |

---

## 2. Selección Tecnológica y Arquitectura de Extracción

### Stack Seleccionado
- **Motor de Scraping & Inspección:** **Python 3.12 + Playwright Async**  
  *Justificación:* Playwright permite ejecutar navegadores Headless Chromium/Firefox de forma totalmente asíncrona, interceptar tráfico de red en vivo (`page.on("request")`), inspeccionar cookies (`context.cookies()`), evaluar `localStorage` / `sessionStorage`, y renderizar Single Page Applications (SPA).
- **Backend API:** **FastAPI (Python)**  
  *Justificación:* API asíncrona de alto rendimiento, documentación OpenAPI interactiva (`/docs`), integración directa con Playwright y validación estricta con Pydantic.
- **Base de Datos:** **PostgreSQL 16** (vía Docker) para persistir auditorías e historiales.
- **Frontend & UI de Pruebas:** **Vite + React (JavaScript/HTML/CSS Vanilla Premium)** con panel de control interactivo, semáforo de diagnóstico y un **Bookmarklet / Botón para navegador**.
- **Dockerización:** Entorno multicontenedor con `docker-compose`.

---

## 3. Cambios Propuestos

```
.
├── docker-compose.yml              # Orquestación de servicios (scanner, postgres, ui)
├── Dockerfile.scanner              # Contenedor Playwright + FastAPI
├── requirements.txt                # Dependencias de Python (fastapi, playwright, uvicorn, pydantic)
├── src/
│   ├── scanner/
│   │   ├── __init__.py
│   │   ├── inspector.py            # Script principal con Playwright (captura cookies, tráfico, links)
│   │   ├── rules_engine.py         # Motor de reglas de cumplimiento legal (Ley Chile)
│   │   └── trackers_db.py          # Lista de dominios/cookies conocidas de rastreo
│   ├── api/
│   │   ├── main.py                 # FastAPI REST Endpoints (/api/v1/scan, /api/v1/health)
│   │   └── schemas.py              # Esquemas de solicitud y respuesta del reporte de auditoría
│   └── ui/                         # Interfaz Web de pruebas con botón de escaneo rápido
│       ├── index.html
│       ├── app.js
│       └── style.css
```

---

## 4. Estructura del Reporte JSON de Salida (PoC)

El microservicio retornará una respuesta JSON estructurada como la siguiente:

```json
{
  "target_url": "https://ejemplo.cl",
  "timestamp": "2026-09-03T23:00:00Z",
  "status_verdict": "RECHAZADO", // APROBADO | RECHAZADO | ADVERTENCIA
  "score": 45,
  "summary": "Se detectó inyección de cookies de rastreo antes del consentimiento del usuario.",
  "evaluations": {
    "privacy_policy": {
      "found": true,
      "url": "https://ejemplo.cl/politica-de-privacidad",
      "http_status": 200,
      "has_mandatory_keywords": true,
      "missing_keywords": []
    },
    "arco_channels": {
      "found": true,
      "detected_channels": ["contacto@ejemplo.cl", "Formulario ARCO"]
    },
    "tracker_audit": {
      "cookies_before_consent": ["_ga", "_fbp"],
      "third_party_requests": ["google-analytics.com", "connect.facebook.net"],
      "has_unauthorized_trackers": true
    }
  }
}
```

---

## 5. Plan de Verificación

### Pruebas Automatizadas
1. Ejecucción de test unitarios de validación del motor de reglas de cumplimiento con `pytest`.
2. Prueba de la API REST mediante endpoints `/api/v1/scan` y `/api/v1/health`.

### Pruebas Manuales y Demostración en Navegador
1. **Lanzamiento con Docker Compose:** `docker compose up --build`
2. **Uso de Interfaz Web:** Navegar a `http://localhost:8000` o `http://localhost:3000` para probar URLs en tiempo real.
3. **Botón de Navegador (Bookmarklet):** Generar un botón script drag-and-drop para probar cualquier sitio web activo desde la barra de marcadores del navegador.
