# Roadmap de Proyecto: Plataforma de Auditoría de Cumplimiento de Datos Personales (Chile)

**Asignatura:** Taller de Desarrollo de Software  
**Equipo:** Sofía Díaz - Benjamín Rodriguez - Franco Vela - Benjamín Vidal
**Objetivo:** Desarrollar un sistema capaz de analizar sitios web externos mediante inspección pasiva (caja negra) para emitir un diagnóstico preliminar de aprobación o rechazo según la Ley de Protección de Datos Personales de Chile.

---

## Resumen Ejecutivo del Flujo
Fase 1: Cimientos y PoC ──> Fase 2: Motor de Inspección ──> Fase 3: Reglas y Reportes ──> Fase 4: MVP y QA
(Semanas 1-2)               (Semanas 3-4)                   (Semanas 5-6)                 (Semanas 7-8)

---

## Desglose de Fases y Tareas

### Fase 1: Fundaciones Técnicas, Criterios y PoC (Semanas 1–2)
*Objetivo: Fijar el estándar normativo auditable y comprobar la viabilidad técnica de la extracción externa.*

* **Mapeo Normativo y Criterios Auditables**
  * Traducir las exigencias legales clave a criterios binarios y deterministas.
  * Identificar los 3 pilares verificables externamente:
    * Existencia y accesibilidad directa de la Política de Privacidad.
    * Canales formales y visibles para el ejercicio de derechos ARCO.
    * Bloqueo previo de scripts y cookies no esenciales antes del consentimiento explícito.
* **Prueba de Concepto (PoC) de Inspección Web**
  * Construir un script base utilizando navegadores headless (**Playwright** o **Puppeteer**).
  * Renderizar Single Page Applications (SPA) y validar la captura de peticiones de red iniciales.
  * Inspeccionar el footer de sitios web para localizar enlaces con selectores semánticos (`/privacidad`, `/terminos`, `privacy-policy`).
* **Arquitectura Base y Entorno de Desarrollo**
  * Definir el stack tecnológico:
    * **Backend:** Node.js (Express/NestJS) o Python (FastAPI).
    * **Frontend:** React / Next.js con TailwindCSS.
    * **Base de datos:** PostgreSQL.
    * **Motor de escaneo:** Playwright empaquetado en contenedor.
  * Configuración de repositorio Git con ramas protegidas, guías de commits y linter común.

---

### Fase 2: Motor de Inspección y Análisis Técnico (Semanas 3–4)
*Objetivo: Construir el servicio automatizado de extracción sin interacción intrusiva.*

* **Módulo de Auditoría de Cookies y Rastreadores**
  * Interceptar tráfico HTTP saliente antes de cualquier interacción del usuario.
  * Contrastar dominios contactados con listas conocidas de rastreo (Google Analytics, Meta Pixel, Hotjar, TikTok Pixel).
  * Registrar cookies depositadas en el almacenamiento local del navegador (`localStorage`, `sessionStorage`, `document.cookie`).
* **Módulo de Análisis de Documentación Pública**
  * Validación del código de estado HTTP de los enlaces de privacidad (descartar errores 404, 403 o redirecciones infinitas).
  * Extracción del contenido textual de la política para verificar presencia de palabras clave esenciales (ej. "titular", "responsable", "derechos", "contacto", "finalidad").
* **Resiliencia, Seguridad y Alcance Legal**
  * Implementar *timeouts* estrictos (máximo 25–30 segundos por escaneo) para evitar bloqueos por sitios lentos.
  * Configurar User-Agents identificables y pausas entre peticiones para prevenir bloqueos por Web Application Firewalls (WAF/Cloudflare).
  * Restricción absoluta a solicitudes `GET` públicas para asegurar cumplimiento de la Ley 21.459 de Delitos Informáticos en Chile.

---

### Fase 3: Motor de Reglas de Cumplimiento y Reportabilidad (Semanas 5–6)
*Objetivo: Evaluar la información técnica extraída, dictaminar el resultado y estructurar la interfaz de usuario.*

* **Lógica del Motor de Decisión (Reglas de Aprobación/Rechazo)**
  * **Aprobado (Conforme):**
    * Política de privacidad disponible y funcional.
    * Mención explícita de derechos ARCO y canales de contacto.
    * Sin rastreadores de terceros activos antes de la interacción con el banner.
  * **Rechazado (No Conforme):**
    * Inyección de cookies de rastreo sin consentimiento previo.
    * Ausencia total o inaccesibilidad (error HTTP) de la política de privacidad.
  * **Con Observaciones (Advertencia):**
    * Política presente pero oculta o con texto genérico que no especifica derechos ni finalidades.
    * Banner de cookies puramente informativo sin opción real de rechazo o configuración.
* **Interfaz de Usuario y Dashboard**
  * Pantalla de ingreso de URL y barra de progreso del análisis en tiempo real.
  * Vista de resultados con semáforo de estado (**Verde / Amarillo / Rojo**), porcentaje de cumplimiento y desglose de evidencias técnicas.
* **Generación de Reportes y Descargo de Responsabilidad**
  * Generación de reportes descargables en PDF con resumen ejecutivo para tomadores de decisiones.
  * Inclusión destacada del *disclaimer* legal: indicación expresa de que la auditoría es una herramienta técnica académica de apoyo y no una certificación legal vinculante.

---

### Fase 4: Integración, Testing, UX y Despliegue (Semanas 7–8)
*Objetivo: Consolidar la plataforma, validar con datos reales y preparar la entrega final.*

* **Persistencia y Gestión de Auditorías**
  * Módulo básico de autenticación de usuarios.
  * Historial de auditorías previas por URL para evaluar mejoras o regresiones en el tiempo.
* **Calibración y Pruebas de Criterio**
  * Ejecutar el escáner sobre una muestra de validación de 30 sitios chilenos reales (e-commerce, banca, medios y sitios gubernamentales).
  * Ajustar reglas para mantener la tasa de falsos positivos por debajo del 15%.
* **Despliegue y Entrega Académica**
  * Orquestación de la plataforma completa mediante `docker-compose`.
  * Despliegue en plataforma en la nube (AWS, GCP, Render o Railway) con certificados HTTPS válidos.
  * Redacción del informe final de software, documentación de API (OpenAPI/Swagger) y preparación de la demostración en vivo.

---

## Matriz de Hitos y Criterios de Aceptación

| Hito | Plazo | Entregable Principal | Criterio de Aceptación |
| :--- | :--- | :--- | :--- |
| **M1: Viabilidad y Reglas** | Fin Semana 2 | PoC en consola + Matriz de reglas normativas documentada. | Script funcional que extrae cookies y enlaces en el 80% de sitios de prueba. |
| **M2: Motor de Inspección** | Fin Semana 4 | Microservicio de escaneo automatizado empaquetado en Docker. | Análisis completo de una URL en $< 30$ s retornando JSON estructurado. |
| **M3: Lógica y Reportes** | Fin Semana 6 | Dashboard web interactivo con dictamen y exportación a PDF. | Clasificación automática (Aprobado/Rechazado) operando sin caídas de servidor. |
| **M4: MVP Desplegado** | Fin Semana 8 | Plataforma en la nube + Documentación de arquitectura. | Menos del 15% de falsos positivos en muestra de 30 sitios reales. |

---

## Matriz de Asignación de Roles (Equipo de 4)

| Integrante | Rol Principal | Focos de Responsabilidad |
| :--- | :--- | :--- |
| **Integrante 1** | Líder Legal & Reglas de Negocio | Interpretación de la ley, motor de decisión, redacción de reportes y disclaimers legales. |
| **Integrante 2** | Ingeniero de Extracción / Scraping | Desarrollo con Playwright/Puppeteer, evasión de bloqueos pasivos, captura de cookies/tráfico. |
| **Integrante 3** | Desarrollador Backend & DevOps | API REST, colas de trabajo para escaneos concurrentes, base de datos y contenedorización Docker. |
| **Integrante 4** | Desarrollador Frontend & UX | Interfaz de usuario, visualización interactiva del reporte, estados del escáner y exportación PDF. |