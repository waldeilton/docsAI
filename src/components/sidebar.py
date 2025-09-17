import streamlit as st
import logging

logger = logging.getLogger(__name__)

def render_conversation_sidebar(conversation_manager, collections=None):
    """
    Render the sidebar with conversation history and document collections
    
    Args:
        conversation_manager: The ConversationManager instance
        collections: Optional list of document collections
    """
    with st.sidebar:
        # Collections section
        st.subheader("📚 Coleções de documentos")
        
        if collections:
            for collection in collections:
                if st.button(f"📂 {collection['name']} ({collection['file_count']} arquivos)", 
                          key=f"collection_{collection['name']}",
                          help=f"Usar coleção {collection['name']}",
                          use_container_width=True):
                    st.session_state.selected_collection = collection['name']
                    # Keep conversation but switch collection
                    st.rerun()
        else:
            st.info("Nenhuma coleção disponível. Use a página de Scraping para criar.")
        
        st.divider()
        
        # Conversation history section
        st.subheader("💬 Histórico de conversas")
        
        # Button for new conversation
        if st.button("+ Nova conversa", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.current_conversation_id = conversation_manager.generate_conversation_id()
            st.session_state.conversation_title = "Nova conversa"
            st.session_state.first_message = True
            st.rerun()
        
        # Load conversations
        conversations = conversation_manager.load_all_conversations()
        
        if not conversations:
            st.info("Nenhuma conversa salva.")
        else:
            for conversation in conversations:
                # Create columns for conversation button and delete button
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    if st.button(f"💬 {conversation['title']}", 
                               key=f"load_{conversation['id']}", 
                               use_container_width=True):
                        st.session_state.current_conversation_id = conversation['id']
                        st.session_state.conversation_title = conversation['title']
                        st.session_state.chat_history = conversation['chat_history']
                        st.session_state.first_message = False
                        st.rerun()
                
                with col2:
                    if st.button("🗑️", key=f"delete_{conversation['id']}", help="Excluir conversa"):
                        conversation_manager.delete_conversation(conversation['id'])
                        
                        # If the deleted conversation is the current one, reset the state
                        if conversation['id'] == st.session_state.current_conversation_id:
                            st.session_state.chat_history = []
                            st.session_state.current_conversation_id = conversation_manager.generate_conversation_id()
                            st.session_state.conversation_title = "Nova conversa"
                            st.session_state.first_message = True
                        
                        st.rerun()