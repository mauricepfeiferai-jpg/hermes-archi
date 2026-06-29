import os

# Telegram
BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"]
ADMIN_CHAT_ID = int(os.environ.get("TELEGRAM_ADMIN_CHAT_ID", "0"))

# Ollama (free LLM)
OLLAMA_HOST = os.environ.get("OLLAMA_HOST", "http://ollama:11434")
OLLAMA_MODEL = os.environ.get("OLLAMA_MODEL", "llama3.1:8b")

# Redis
REDIS_URL = os.environ.get("REDIS_URL", "redis://localhost:6379/0")

# ChromaDB
CHROMADB_HOST = os.environ.get("CHROMADB_HOST", "localhost")
CHROMADB_PORT = int(os.environ.get("CHROMADB_PORT", "8000"))

# Empire paths (env-overridable for local dev)
EMPIRE_DIR = os.environ.get("EMPIRE_DIR", "/tmp/empire")
RESULTS_DIR = os.environ.get("RESULTS_DIR", f"{EMPIRE_DIR}/results")
TASKS_DIR = os.environ.get("TASKS_DIR", f"{EMPIRE_DIR}/tasks")
KB_DIR = os.environ.get("KB_DIR", f"{EMPIRE_DIR}/shared-kb")

# Timezone
TIMEZONE = os.environ.get("SERVER_TIMEZONE", "Europe/Berlin")
