import os
from dotenv import load_dotenv
load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
PRIMARY_MODEL = os.getenv("PRIMARY_MODEL", "gpt-4o")
FALLBACK_MODEL = os.getenv("FALLBACK_MODEL", "gpt-4o")
MAX_COMPLETION_TOKENS = int(os.getenv("MAX_COMPLETION_TOKENS", "2000"))

if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY missing. Put it in .env")
