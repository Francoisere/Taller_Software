"""
Motor de Reglas de Cumplimiento Legal (Ley N° 19.628 y Nueva Ley de Protección de Datos Personales Chile).
Evalúa los hallazgos técnicos recopilados por el inspector pasivo y determina el dictamen.
"""

from typing import Dict, Any, List

class RulesEngine:
    @staticmethod
    def evaluate(scan_raw_data: Dict[str, Any]) -> Dict[str, Any]:
        target_url = scan_raw_data.get("target_url", "")
        page_load_status = scan_raw_data.get("page_load_status", 0)
        error_message = scan_raw_data.get("error_message")

        tracker_audit = scan_raw_data.get("tracker_audit", {})
        privacy_audit = scan_raw_data.get("privacy_policy_audit", {})
        arco_audit = scan_raw_data.get("arco_channels_audit", {})

        score = 0
        findings: List[Dict[str, Any]] = []

        # --- EVALUACIÓN PILAR 1: POLÍTICA DE PRIVACIDAD ---
        pilar_privacy_score = 0
        privacy_status = "FALLA"

        if privacy_audit.get("found") and privacy_audit.get("http_status") == 200:
            pilar_privacy_score += 20
            findings.append({
                "pilar": "Política de Privacidad",
                "status": "OK",
                "title": "Política de Privacidad Accesible",
                "detail": f"Se encontró enlace a la política en: {privacy_audit.get('url')} (HTTP 200)."
            })
            if privacy_audit.get("has_mandatory_keywords"):
                pilar_privacy_score += 15
                findings.append({
                    "pilar": "Política de Privacidad",
                    "status": "OK",
                    "title": "Contenido Normativo Mínimo Presente",
                    "detail": f"Palabras clave esenciales detectadas: {', '.join(privacy_audit.get('found_keywords', []))}."
                })
            else:
                findings.append({
                    "pilar": "Política de Privacidad",
                    "status": "WARNING",
                    "title": "Texto Genérico o Incompleto",
                    "detail": f"Faltan términos clave exigidos por la norma: {', '.join(privacy_audit.get('missing_keywords', []))}."
                })
            privacy_status = "CUMPLE" if pilar_privacy_score >= 35 else "OBSERVACION"
        else:
            findings.append({
                "pilar": "Política de Privacidad",
                "status": "FAIL",
                "title": "Ausencia de Política de Privacidad",
                "detail": "No se detectó un enlace accesible a la política de privacidad o la página retornó error."
            })

        score += pilar_privacy_score

        # --- EVALUACIÓN PILAR 2: CANALES ARCO ---
        pilar_arco_score = 0
        arco_status = "FALLA"

        if arco_audit.get("found"):
            if arco_audit.get("detected_emails"):
                pilar_arco_score += 15
                findings.append({
                    "pilar": "Derechos ARCO",
                    "status": "OK",
                    "title": "Canal de Contacto Directo Detectado",
                    "detail": f"Correos identificados para ejercicio de derechos: {', '.join(arco_audit.get('detected_emails', []))}."
                })
            if arco_audit.get("has_explicit_arco_mention"):
                pilar_arco_score += 15
                findings.append({
                    "pilar": "Derechos ARCO",
                    "status": "OK",
                    "title": "Mención Explícita a Derechos ARCO",
                    "detail": f"Términos de derechos reconocidos: {', '.join(arco_audit.get('detected_terms', []))}."
                })
            elif len(arco_audit.get("detected_terms", [])) > 0:
                pilar_arco_score += 10
                findings.append({
                    "pilar": "Derechos ARCO",
                    "status": "WARNING",
                    "title": "Términos de Contacto Detectados",
                    "detail": f"Coincidencias encontradas: {', '.join(arco_audit.get('detected_terms', []))}."
                })
            
            arco_status = "CUMPLE" if pilar_arco_score >= 25 else "OBSERVACION"
        else:
            findings.append({
                "pilar": "Derechos ARCO",
                "status": "FAIL",
                "title": "Sin Canales Formales para Derechos ARCO",
                "detail": "No se identificaron canales visibles ni correos electrónicos para gestionar solicitudes de acceso, rectificación, cancelación u oposición."
            })

        score += pilar_arco_score

        # --- EVALUACIÓN PILAR 3: CONSENTIMIENTO Y COOKIES ---
        pilar_consent_score = 0
        consent_status = "FALLA"

        has_unauthorized = tracker_audit.get("has_unauthorized_trackers", False)
        detected_domains = tracker_audit.get("detected_tracker_domains", [])
        detected_cookies = tracker_audit.get("detected_tracker_cookies", [])

        if not has_unauthorized:
            pilar_consent_score = 35
            consent_status = "CUMPLE"
            findings.append({
                "pilar": "Cookies y Rastreadores",
                "status": "OK",
                "title": "Navegación Limpia Previa al Consentimiento",
                "detail": "No se depositaron cookies de rastreo de terceros ni se realizaron peticiones a dominios de rastreo publicitario/analítico antes de la interacción del usuario."
            })
        else:
            pilar_consent_score = 0
            consent_status = "FALLA"
            details = []
            if detected_domains:
                details.append(f"Dominios de rastreo activos: {', '.join(detected_domains)}")
            if detected_cookies:
                details.append(f"Cookies de rastreo inyectadas: {', '.join(detected_cookies)}")

            findings.append({
                "pilar": "Cookies y Rastreadores",
                "status": "FAIL",
                "title": "Inyección Pasiva No Autorizada de Rastreadores",
                "detail": " | ".join(details)
            })

        score += pilar_consent_score

        # --- DICTAMEN FINAL ---
        if score >= 80 and not has_unauthorized:
            verdict = "APROBADO"
            verdict_summary = "El sitio cumple con los pilares fundamentales de transparencia, disponibilidad de políticas y respeto al consentimiento previo de rastreo."
        elif score >= 55:
            verdict = "CON_OBSERVACIONES"
            verdict_summary = "El sitio presenta cumplimiento parcial. Existen advertencias en la redacción de la política, canales ARCO o presencia de rastreadores."
        else:
            verdict = "RECHAZADO"
            verdict_summary = "El sitio incumple los estándares mínimos auditados: ausencia/inaccesibilidad de políticas de privacidad o inyección de cookies sin consentimiento explícito."

        return {
            "target_url": target_url,
            "page_load_status": page_load_status,
            "verdict": verdict,
            "score": score,
            "verdict_summary": verdict_summary,
            "pilares": {
                "politica_privacidad": {
                    "status": privacy_status,
                    "score": pilar_privacy_score,
                    "max_score": 35
                },
                "canales_arco": {
                    "status": arco_status,
                    "score": pilar_arco_score,
                    "max_score": 30
                },
                "consentimiento_cookies": {
                    "status": consent_status,
                    "score": pilar_consent_score,
                    "max_score": 35
                }
            },
            "findings": findings,
            "technical_raw": scan_raw_data,
            "legal_disclaimer": "Este diagnóstico es una herramienta técnica de auditoría académica basada en la legislación chilena (Ley N° 19.628). No constituye una certificación ni dictamen jurídico vinculante."
        }
