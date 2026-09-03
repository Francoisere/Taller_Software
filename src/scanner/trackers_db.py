"""
Base de datos de firmas de dominios y cookies de rastreo no esenciales.
Utilizada para contrastar tráfico saliente y cookies depositadas antes del consentimiento.
"""

KNOWN_TRACKER_DOMAINS = [
    # Google Analytics / Tag Manager / Ads
    "google-analytics.com",
    "googletagmanager.com",
    "doubleclick.net",
    "googleadservices.com",
    "analytics.google.com",

    # Meta / Facebook
    "connect.facebook.net",
    "facebook.com/tr",
    "pixel.facebook.com",

    # Hotjar / UX Tracking
    "hotjar.com",
    "static.hotjar.com",
    "script.hotjar.com",

    # TikTok
    "analytics.tiktok.com",
    "analytics-sg.tiktok.com",

    # Twitter / X
    "static.ads-twitter.com",
    "analytics.twitter.com",

    # LinkedIn
    "snap.licdn.com",
    "px.ads.linkedin.com",

    # Criteo / Taboola / Outbrain / Adroll
    "criteo.com",
    "criteo.net",
    "taboola.com",
    "outbrain.com",
    "adroll.com",

    # Mixpanel / Amplitude / Clarity
    "cdn.mxpnl.com",
    "api.mixpanel.com",
    "amplitude.com",
    "api.amplitude.com",
    "clarity.ms",

    # Yandex / Matomo / Hubspot
    "mc.yandex.ru",
    "hs-scripts.com",
    "js.hs-analytics.net",

    # CrazyEgg / Mouseflow / Inspectlet
    "crazyegg.com",
    "mouseflow.com",
    "inspectlet.com"
]

KNOWN_TRACKER_COOKIES = [
    # Google
    "_ga", "_gid", "_gat", "_gcl_au", "AMP_TOKEN", "_gac_",
    # Meta
    "_fbp", "_fbc", "fr",
    # Hotjar
    "_hjid", "_hjSession_", "_hjAbsoluteSessionInProgress", "_hjFirstSeen",
    # TikTok
    "_tt_enable_cookie", "_ttp",
    # Hubspot
    "hubspotutk", "__hssrc", "__hstc",
    # LinkedIn
    "li_sugr", "bcookie", "bscookie",
    # Clarity
    "_clck", "_clsk"
]

MANDATORY_LEGAL_KEYWORDS = [
    "titular",
    "responsable",
    "derechos",
    "tratamiento",
    "finalidad",
    "contacto",
    "datos personales"
]

ARCO_KEYWORDS = [
    "arco",
    "acceso",
    "rectificacion",
    "rectificación",
    "cancelacion",
    "cancelación",
    "oposicion",
    "oposición",
    "derechos del titular",
    "ejercicio de derechos"
]
