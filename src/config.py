"""
Configuración centralizada del proyecto Alpha Agent Terminal.
Todas las constantes, rutas y variables de entorno se gestionan desde aquí.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ─── Rutas del Proyecto ──────────────────────────────────────────────
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.normpath(os.path.join(BASE_DIR, ".."))

DATA_DIR = os.path.join(PROJECT_ROOT, "tvdatafeed-skill", "data")
BRIDGE_DIR = os.path.join(PROJECT_ROOT, "bridge")
FRONTEND_DIR = os.path.join(PROJECT_ROOT, "frontend")

# ─── Archivos del Bridge ─────────────────────────────────────────────
ESTADO_DASHBOARD_PATH = os.path.join(BRIDGE_DIR, "estado_dashboard.json")
BRIDGE_REQUEST_PATH = os.path.join(BRIDGE_DIR, "antigravity_bridge_request.json")
BRIDGE_RESPONSE_PATH = os.path.join(BRIDGE_DIR, "antigravity_bridge_response.json")

# ─── Servidor HTTP ────────────────────────────────────────────────────
SERVER_PORT = int(os.getenv("SERVER_PORT", "8050"))

# ─── Gemini AI ────────────────────────────────────────────────────────
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
