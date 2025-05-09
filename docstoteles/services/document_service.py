import logging
import os
from langchain_community.document_loaders import DirectoryLoader, UnstructuredMarkdownLoader
from langchain_openai.embeddings import OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from core.config import APP_CONFIG, PATHS
import streamlit as st

logger = logging.getLogger(__name__)

class DocumentService:
    """Service for document loading and vector store operations"""
    
    def __init__(self):
        """Initialize document service"""
        self.embeddings = OpenAIEmbeddings()
        logger.info("Document service initialized")
    
    @st.cache_resource
    def load_documents_from_directory(_self, directory_path):
        """Load all markdown documents from a directory and return them"""
        try:
            loader = DirectoryLoader(
                directory_path,
                glob="**/*.md",
                loader_cls=UnstructuredMarkdownLoader
            )
            
            docs = loader.load()
            logger.info(f"Loaded {len(docs)} documents from {directory_path}")
            return docs
        except Exception as e:
            logger.error(f"Error loading documents: {str(e)}")
            raise
    
    def create_vector_store(self, documents):
        """Create a vector store from documents"""
        try:
            # Remove o cache para evitar problemas com o parâmetro 'documents'
            vector_store = FAISS.from_documents(documents, self.embeddings)
            logger.info(f"Created vector store with {len(documents)} documents")
            return vector_store
        except Exception as e:
            logger.error(f"Error creating vector store: {str(e)}")
            raise
    
    def get_retriever(self, vector_store, k=None):
        """Get a retriever from a vector store"""
        if k is None:
            k = APP_CONFIG["retriever_k"]
        
        return vector_store.as_retriever(search_kwargs={"k": k})
    
    def retrieve_relevant_documents(self, retriever, query):
        """Retrieve relevant documents for a query"""
        try:
            docs = retriever.get_relevant_documents(query)
            logger.info(f"Retrieved {len(docs)} relevant documents for query")
            return docs
        except Exception as e:
            logger.error(f"Error retrieving documents: {str(e)}")
            raise
    
    def get_available_rag_collections(self):
        """Get all available RAG collections"""
        rag_dir = PATHS["rag_directory"]
        collections = []
        
        try:
            if not os.path.exists(rag_dir):
                os.makedirs(rag_dir, exist_ok=True)
                logger.info(f"Created RAG directory: {rag_dir}")
                return []
                
            for item in os.listdir(rag_dir):
                item_path = os.path.join(rag_dir, item)
                if os.path.isdir(item_path):
                    # Check if directory contains markdown files
                    try:
                        md_files = [f for f in os.listdir(item_path) 
                                  if f.endswith('.md') and os.path.isfile(os.path.join(item_path, f))]
                        
                        if md_files:
                            collections.append({
                                "name": item,
                                "path": item_path,
                                "file_count": len(md_files)
                            })
                    except Exception as e:
                        logger.error(f"Error processing directory {item_path}: {str(e)}")
            
            return collections
        except Exception as e:
            logger.error(f"Error getting RAG collections: {str(e)}")
            return []
    
    def get_document_content(self, file_path):
        """Get the content of a document"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
            return content
        except Exception as e:
            logger.error(f"Error reading document: {str(e)}")
            return None