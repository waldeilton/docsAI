import streamlit as st
import os
import logging
from core.config import PATHS

logger = logging.getLogger(__name__)

def render_document_viewer(collection_name=None):
    """
    Render a document viewer for exploring collected documents
    
    Args:
        collection_name: Optional name of collection to open initially
    """
    st.subheader("📄 Visualizador de documentos")
    
    # Get all directories in the RAG folder
    rag_dir = PATHS["rag_directory"]
    if not os.path.exists(rag_dir):
        st.info("Diretório RAG não encontrado.")
        return
    
    collections = [d for d in os.listdir(rag_dir) 
                 if os.path.isdir(os.path.join(rag_dir, d))]
    
    if not collections:
        st.info("Nenhuma coleção disponível para visualização.")
        return
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        selected_collection = st.selectbox(
            "Selecione uma coleção", 
            options=collections,
            index=collections.index(collection_name) if collection_name in collections else 0
        )
        
        if selected_collection:
            collection_path = os.path.join(rag_dir, selected_collection)
            files = [f for f in os.listdir(collection_path) 
                   if f.endswith('.md') and os.path.isfile(os.path.join(collection_path, f))]
            
            if not files:
                st.info(f"Nenhum arquivo encontrado na coleção '{selected_collection}'.")
                return
            
            selected_file = st.selectbox("Selecione um arquivo", files)
    
    with col2:
        if selected_collection and selected_file:
            file_path = os.path.join(rag_dir, selected_collection, selected_file)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Add copy button for the document content
                copy_col1, copy_col2 = st.columns([0.9, 0.1])
                
                with copy_col1:
                    st.markdown("### Conteúdo do documento")
                
                with copy_col2:
                    st.button(
                        "📋", 
                        key="copy_document", 
                        help="Copiar conteúdo do documento"
                    )
                
                # Display document content
                st.markdown(content)
                
                # Show stats about the document
                st.divider()
                word_count = len(content.split())
                char_count = len(content)
                st.caption(f"Estatísticas: {word_count} palavras, {char_count} caracteres")
                
            except Exception as e:
                st.error(f"Erro ao ler o arquivo: {str(e)}")
                logger.error(f"Error reading file {file_path}: {str(e)}")

def render_document_list(document_service, on_selection=None):
    """
    Render a list of available document collections
    
    Args:
        document_service: DocumentService instance
        on_selection: Optional callback for when a collection is selected
    """
    st.subheader("📚 Coleções disponíveis")
    
    collections = document_service.get_available_rag_collections()
    
    if not collections:
        st.info("Nenhuma coleção disponível.")
        return
    
    for collection in collections:
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.write(f"**{collection['name']}**")
        
        with col2:
            st.write(f"{collection['file_count']} arquivos")
        
        with col3:
            if st.button("Selecionar", key=f"select_{collection['name']}"):
                if on_selection:
                    on_selection(collection['name'])