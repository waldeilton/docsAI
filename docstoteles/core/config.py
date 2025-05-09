import os
from dotenv import load_dotenv
import logging
from pathlib import Path

# Carregar variáveis de ambiente
load_dotenv()

# Criar diretórios necessários
def create_directories():
    """Criar todos os diretórios necessários para a aplicação"""
    directories = [
        Path("data/conversations"),
        Path("data/rag")
    ]
    
    for directory in directories:
        directory.mkdir(parents=True, exist_ok=True)

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("app.log")
    ]
)

logger = logging.getLogger(__name__)

# Configurações da aplicação
APP_CONFIG = {
    "app_name": "Docstóteles",
    "app_icon": "📚",
    "openai_api_key": os.getenv("OPENAI_API_KEY", ""),
    "default_model": os.getenv("DEFAULT_MODEL", "gpt-4o-mini"),
    "title_model": os.getenv("TITLE_MODEL", "gpt-4o-mini"),
    "temperature": float(os.getenv("TEMPERATURE", "0.4")),
    "title_temperature": float(os.getenv("TITLE_TEMPERATURE", "0.2")),
    "retriever_k": int(os.getenv("RETRIEVER_K", "5")),
    "firecrawl_api_key": os.getenv("FIRECRAWL_API_KEY", ""),
    "firecrawl_api_url": os.getenv("FIRECRAWL_API_URL", "http://localhost:3002")
}

# Caminhos
PATHS = {
    "conversations_db": "data/conversations/conversations.json",
    "rag_directory": "data/rag"
}

# Criar diretórios necessários ao importar o módulo
create_directories()