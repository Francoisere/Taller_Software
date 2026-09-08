# DataCheck.cl - Plataforma de Auditoría de Cumplimiento de Datos Personales (Chile)

**Asignatura:** Taller de Desarrollo de Software  
**Equipo:** Sofía Díaz - Benjamín Rodriguez - Franco Vela - Benjamín Vidal  
**Marca Oficial:** DataCheck.cl  

## Descripción del Proyecto

**DataCheck.cl** es una plataforma de escaneo pasivo e inspección técnica de sitios web externos para emitir un diagnóstico preliminar de cumplimiento basado en la **Ley N° 19.628** y el proyecto de la **Nueva Ley de Protección de Datos Personales en Chile**.

---

## Pilares de Evaluación Pasiva

1. **Política de Privacidad:** Existencia, accesibilidad (HTTP 200) y presencia de cláusulas informativas mínimas.
2. **Derechos ARCO:** Canales formales y visibles para el ejercicio de derechos Acceso, Rectificación, Cancelación u Oposición.
3. **Consentimiento & Cookies:** Bloqueo pasivo previo de scripts y cookies no esenciales de rastreo (`Google Analytics`, `Meta Pixel`, `Hotjar`, `TikTok Pixel`, etc.).

---

## Ejecución con Docker Compose

```bash
docker compose down
docker compose up --build
```

Navega a `http://localhost:8000` para acceder a **DataCheck.cl**.