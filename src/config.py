"""
Application Configuration.
Loads settings from environment variables or .env file with defaults.
Supports switching between Mock LLM, Gemini, OpenAI, Claude, and Ollama.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load .env file from project root
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

# LLM Configuration
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock").lower()
LLM_MODEL = os.getenv("LLM_MODEL", "gemini-2.5-flash")
MOCK_LLM = os.getenv("MOCK_LLM", "true").lower() in ("true", "1", "yes")

# API Keys
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

# Storage & Database
DATA_DIR = ROOT_DIR / "data"
DB_PATH = Path(os.getenv("DB_PATH", str(DATA_DIR / "energy.duckdb")))

# Server
API_HOST = os.getenv("API_HOST", "0.0.0.0")
API_PORT = int(os.getenv("API_PORT", "8000"))
UI_PORT = int(os.getenv("UI_PORT", "8501"))

# Industrial & Environmental Parameters
EMISSION_FACTOR_KG_PER_KWH = float(os.getenv("EMISSION_FACTOR_KG_PER_KWH", "0.4"))
TOLERANCE_PCT = float(os.getenv("TOLERANCE_PCT", "7.0"))
