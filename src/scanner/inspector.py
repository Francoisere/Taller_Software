import asyncio
import re
import urllib.parse
from typing import Dict, List, Any, Optional
from playwright.async_api import async_playwright, Page, BrowserContext
from bs4 import BeautifulSoup

from .trackers_db import (
    KNOWN_TRACKER_DOMAINS,
    KNOWN_TRACKER_COOKIES,
    MANDATORY_LEGAL_KEYWORDS,
    ARCO_KEYWORDS
)

PRIVACY_LINK_PATTERNS = [
    r"privacidad",
    r"privacy",
    r"terminos",
    r"terms",
    r"aviso-legal",
    r"legal",
    r"politica"
]

EMAIL_REGEX = r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}"

class WebInspector:
    def __init__(self, timeout_ms: int = 25000):
        self.timeout_ms = timeout_ms

    async def scan_url(self, target_url: str) -> Dict[str, Any]:
        """
        Escanea de forma pasiva una URL objetivo utilizando Playwright en modo Headless.
        Registra peticiones salientes, cookies, enlaces de privacidad y canales ARCO.
        """
        if not target_url.startswith("http://") and not target_url.startswith("https://"):
            target_url = "https://" + target_url

        captured_requests: List[str] = []
        detected_tracker_domains: List[str] = []

        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=[
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-accelerated-2d-canvas",
                    "--disable-gpu"
                ]
            )
            
            context: BrowserContext = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 (AuditBot/1.0; Legal Compliance Check)"
            )
            
            page: Page = await context.new_page()

            # Escuchar solicitudes de red pasivas antes de cualquier interacción
            def handle_request(request):
                url = request.url
                captured_requests.append(url)
                for domain in KNOWN_TRACKER_DOMAINS:
                    if domain in url and domain not in detected_tracker_domains:
                        detected_tracker_domains.append(domain)

            page.on("request", handle_request)

            page_load_status = 200
            error_message = None

            try:
                response = await page.goto(target_url, timeout=self.timeout_ms, wait_until="networkidle")
                if response:
                    page_load_status = response.status
            except Exception as e:
                # Si falla networkidle, intentamos domcontentloaded
                try:
                    response = await page.goto(target_url, timeout=15000, wait_until="domcontentloaded")
                    if response:
                        page_load_status = response.status
                except Exception as inner_e:
                    error_message = str(inner_e)
                    page_load_status = 0

            # Espera breve para asegurar captura de scripts asíncronos iniciales
            await asyncio.sleep(2)

            # Obtener cookies del almacenamiento
            cookies = await context.cookies()
            raw_cookies = [c["name"] for c in cookies]

            detected_tracker_cookies = [
                name for name in raw_cookies if any(tk in name for tk in KNOWN_TRACKER_COOKIES)
            ]

            # Intentar obtener localStorage y sessionStorage
            local_storage_keys = []
            try:
                local_storage_keys = await page.evaluate("Object.keys(localStorage)")
            except Exception:
                pass

            # Obtener HTML completo para análisis DOM
            html_content = ""
            try:
                html_content = await page.content()
            except Exception:
                pass

            soup = BeautifulSoup(html_content, "html.parser")

            # Buscar enlaces a Políticas de Privacidad
            privacy_links = self._find_privacy_links(soup, target_url)

            # Inspeccionar la mejor coincidencia de Política de Privacidad
            privacy_audit = await self._inspect_privacy_policy(context, privacy_links, target_url)

            # Buscar canales de contacto ARCO
            arco_channels = self._extract_arco_channels(soup, html_content, privacy_audit.get("policy_text", ""))

            await browser.close()

            return {
                "target_url": target_url,
                "page_load_status": page_load_status,
                "error_message": error_message,
                "tracker_audit": {
                    "detected_tracker_domains": detected_tracker_domains,
                    "detected_tracker_cookies": detected_tracker_cookies,
                    "total_cookies": len(raw_cookies),
                    "raw_cookies": raw_cookies,
                    "local_storage_keys_count": len(local_storage_keys),
                    "has_unauthorized_trackers": len(detected_tracker_domains) > 0 or len(detected_tracker_cookies) > 0
                },
                "privacy_policy_audit": privacy_audit,
                "arco_channels_audit": arco_channels
            }

    def _find_privacy_links(self, soup: BeautifulSoup, base_url: str) -> List[Dict[str, str]]:
        """
        Localiza enlaces que contengan palabras clave de privacidad en href o texto del tag <a>.
        """
        found_links = []
        seen_hrefs = set()

        for a in soup.find_all("a", href=True):
            href = a["href"].strip()
            text = a.get_text(strip=True).lower()
            href_lower = href.lower()

            matches = False
            for pattern in PRIVACY_LINK_PATTERNS:
                if re.search(pattern, href_lower) or re.search(pattern, text):
                    matches = True
                    break

            if matches:
                full_url = urllib.parse.urljoin(base_url, href)
                if full_url not in seen_hrefs and (full_url.startswith("http://") or full_url.startswith("https://")):
                    seen_hrefs.add(full_url)
                    found_links.append({
                        "url": full_url,
                        "anchor_text": a.get_text(strip=True)
                    })

        return found_links

    async def _inspect_privacy_policy(self, context: BrowserContext, privacy_links: List[Dict[str, str]], base_url: str) -> Dict[str, Any]:
        """
        Si se encontraron enlaces de privacidad, navega al más relevante y verifica presencia de palabras clave.
        """
        if not privacy_links:
            return {
                "found": False,
                "url": None,
                "http_status": 404,
                "policy_text": "",
                "found_keywords": [],
                "missing_keywords": MANDATORY_LEGAL_KEYWORDS,
                "has_mandatory_keywords": False
            }

        target_policy_url = privacy_links[0]["url"]
        
        # Preferir enlaces que contengan 'privacidad' o 'privacy'
        for link in privacy_links:
            if "privacidad" in link["url"].lower() or "privacy" in link["url"].lower():
                target_policy_url = link["url"]
                break

        page = await context.new_page()
        http_status = 0
        policy_text = ""

        try:
            res = await page.goto(target_policy_url, timeout=15000, wait_until="domcontentloaded")
            if res:
                http_status = res.status
            
            policy_text = await page.evaluate("document.body ? document.body.innerText : ''")
        except Exception:
            http_status = 500
        finally:
            await page.close()

        policy_text_lower = policy_text.lower()
        found_keywords = [kw for kw in MANDATORY_LEGAL_KEYWORDS if kw in policy_text_lower]
        missing_keywords = [kw for kw in MANDATORY_LEGAL_KEYWORDS if kw not in policy_text_lower]

        # Consideramos suficientes las palabras clave si encuentra al menos 4 de las 7 esenciales
        has_mandatory_keywords = len(found_keywords) >= 4

        return {
            "found": True,
            "url": target_policy_url,
            "all_detected_links": [l["url"] for l in privacy_links],
            "http_status": http_status,
            "policy_text_snippet": policy_text[:300] if policy_text else "",
            "policy_text": policy_text,
            "found_keywords": found_keywords,
            "missing_keywords": missing_keywords,
            "has_mandatory_keywords": has_mandatory_keywords
        }

    def _extract_arco_channels(self, soup: BeautifulSoup, main_html: str, policy_text: str) -> Dict[str, Any]:
        """
        Extrae correos electrónicos de contacto y busca evidencias de canal ARCO.
        """
        all_text = soup.get_text() + " " + policy_text
        found_emails = list(set(re.findall(EMAIL_REGEX, all_text)))
        
        # Filtrar correos irrelevantes o de ejemplo
        valid_emails = [
            e for e in found_emails 
            if not e.endswith(".png") and not e.endswith(".jpg") and "example" not in e and "domain" not in e
        ]

        found_arco_terms = [kw for kw in ARCO_KEYWORDS if kw in all_text.lower()]
        
        has_arco_channel = len(valid_emails) > 0 or len(found_arco_terms) > 0

        return {
            "found": has_arco_channel,
            "detected_emails": valid_emails,
            "detected_terms": list(set(found_arco_terms)),
            "has_explicit_arco_mention": any("arco" in term for term in found_arco_terms)
        }
