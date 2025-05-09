from tinydb import TinyDB, Query
from tinydb.operations import set as tinydb_set
import logging
from core.config import PATHS
from datetime import datetime
import uuid

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gerenciador de banco de dados para operações TinyDB"""
    
    def __init__(self, db_path=PATHS["conversations_db"]):
        """Inicializar banco de dados com o caminho especificado"""
        self.db_path = db_path
        self.db = TinyDB(db_path, ensure_ascii=False)
        logger.info(f"Banco de dados inicializado em {db_path}")
    
    def get_table(self, table_name):
        """Obter uma tabela específica do banco de dados"""
        return self.db.table(table_name)

class ConversationManager:
    """Gerenciador para operações de conversas"""
    
    def __init__(self, db_manager=None):
        """Inicializar com um gerenciador de banco de dados"""
        if db_manager is None:
            db_manager = DatabaseManager()
        self.db_manager = db_manager
        self.conversations = self.db_manager.get_table("conversations")
        self.Query = Query()
    
    def load_all_conversations(self):
        """Carregar todas as conversas ordenadas por timestamp (mais recentes primeiro)"""
        conversations = self.conversations.all()
        return sorted(conversations, key=lambda x: x.get("timestamp", ""), reverse=True)
    
    def load_conversations_by_collection(self, collection_name):
        """Carregar conversas filtradas por coleção"""
        conversations = self.conversations.search(self.Query.collection_name == collection_name)
        return sorted(conversations, key=lambda x: x.get("timestamp", ""), reverse=True)
    
    def load_conversation(self, conversation_id):
        """Carregar uma conversa específica por ID"""
        return self.conversations.get(self.Query.id == conversation_id)
    
    def save_conversation(self, conversation_id, title, chat_history, collection_name=None):
        """Salvar ou atualizar uma conversa"""
        conversation = {
            "id": conversation_id,
            "title": title,
            "chat_history": chat_history,
            "timestamp": datetime.now().isoformat(),
            "collection_name": collection_name
        }
        
        # Verificar se a conversa existe
        existing = self.conversations.get(self.Query.id == conversation_id)
        if existing:
            self.conversations.update(conversation, self.Query.id == conversation_id)
            logger.debug(f"Conversa atualizada: {conversation_id}")
        else:
            self.conversations.insert(conversation)
            logger.debug(f"Nova conversa inserida: {conversation_id}")
        
        return conversation
    
    def update_conversation_title(self, conversation_id, title):
        """Atualizar apenas o título de uma conversa"""
        self.conversations.update(
            tinydb_set("title", title),
            self.Query.id == conversation_id
        )
        logger.debug(f"Título atualizado para conversa: {conversation_id}")
    
    def delete_conversation(self, conversation_id):
        """Excluir uma conversa por ID"""
        self.conversations.remove(self.Query.id == conversation_id)
        logger.debug(f"Conversa excluída: {conversation_id}")
        return True
    
    def generate_conversation_id(self):
        """Gerar um ID único para conversa"""
        return str(uuid.uuid4())


class ScrapingProjectManager:
    """Gerenciador para operações de projetos de scraping"""
    
    def __init__(self, db_manager=None):
        """Inicializar com um gerenciador de banco de dados"""
        if db_manager is None:
            db_manager = DatabaseManager()
        self.db_manager = db_manager
        self.projects = self.db_manager.get_table("scraping_projects")
        self.Query = Query()
    
    def save_project(self, project_name, source_url, file_count, status="completed"):
        """Salvar um projeto de scraping"""
        project = {
            "id": str(uuid.uuid4()),
            "name": project_name,
            "source_url": source_url,
            "file_count": file_count,
            "created_at": datetime.now().isoformat(),
            "status": status
        }
        
        self.projects.insert(project)
        logger.info(f"Projeto de scraping salvo: {project_name}")
        return project
    
    def get_all_projects(self):
        """Obter todos os projetos de scraping"""
        projects = self.projects.all()
        return sorted(projects, key=lambda x: x.get("created_at", ""), reverse=True)
    
    def delete_project(self, project_id):
        """Excluir um projeto de scraping"""
        self.projects.remove(self.Query.id == project_id)
        logger.info(f"Projeto de scraping excluído: {project_id}")
        return True