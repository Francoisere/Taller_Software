import pytest
from src.scanner.rules_engine import RulesEngine

def test_evaluate_aprobado():
    mock_scan_data = {
        "target_url": "https://ejemplo.cl",
        "page_load_status": 200,
        "error_message": None,
        "tracker_audit": {
            "detected_tracker_domains": [],
            "detected_tracker_cookies": [],
            "has_unauthorized_trackers": False
        },
        "privacy_policy_audit": {
            "found": True,
            "url": "https://ejemplo.cl/politica-de-privacidad",
            "http_status": 200,
            "has_mandatory_keywords": True,
            "found_keywords": ["titular", "responsable", "derechos", "tratamiento", "finalidad"]
        },
        "arco_channels_audit": {
            "found": True,
            "detected_emails": ["contacto@ejemplo.cl"],
            "detected_terms": ["arco", "derechos del titular"],
            "has_explicit_arco_mention": True
        }
    }

    result = RulesEngine.evaluate(mock_scan_data)
    assert result["verdict"] == "APROBADO"
    assert result["score"] >= 80

def test_evaluate_rechazado_con_trackers():
    mock_scan_data = {
        "target_url": "https://ejemplo-bad.cl",
        "page_load_status": 200,
        "error_message": None,
        "tracker_audit": {
            "detected_tracker_domains": ["google-analytics.com", "connect.facebook.net"],
            "detected_tracker_cookies": ["_ga", "_fbp"],
            "has_unauthorized_trackers": True
        },
        "privacy_policy_audit": {
            "found": False,
            "url": None,
            "http_status": 404,
            "has_mandatory_keywords": False,
            "found_keywords": []
        },
        "arco_channels_audit": {
            "found": False,
            "detected_emails": [],
            "detected_terms": [],
            "has_explicit_arco_mention": False
        }
    }

    result = RulesEngine.evaluate(mock_scan_data)
    assert result["verdict"] == "RECHAZADO"
    assert result["score"] < 50
