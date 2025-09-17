import streamlit as st
import os
from core.config import APP_CONFIG, PATHS
from core.database import ConversationManager
from services.ai_service import AIService
from services.document_service import DocumentService

# Configuração da página
st.set_page_config(
    page_title="Docstóteles - Chat",
    page_icon="📚",
    layout="wide"
)

# Inicializar serviços
conversation_manager = ConversationManager()
ai_service = AIService()
document_service = DocumentService()

# Inicializar estados da sessão
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []
if 'current_conversation_id' not in st.session_state:
    st.session_state.current_conversation_id = conversation_manager.generate_conversation_id()
if 'conversation_title' not in st.session_state:
    st.session_state.conversation_title = "Nova conversa"
if 'first_message' not in st.session_state:
    st.session_state.first_message = True
if 'selected_collection' not in st.session_state:
    st.session_state.selected_collection = None

# Verificar chave da API
openai_api_key = os.getenv("OPENAI_API_KEY")
if not openai_api_key:
    st.warning("⚠️ Chave API OpenAI não encontrada")
    openai_api_key = st.text_input("Chave da API OpenAI:", type="password")
    if openai_api_key:
        os.environ["OPENAI_API_KEY"] = openai_api_key
        st.rerun()

# Sidebar - Histórico e seleção de coleção
with st.sidebar:
    # Logo e título do app
    st.title("Docstóteles 📚")
    
    # Se não houver coleção selecionada, mostrar seletor de coleção
    if not st.session_state.selected_collection:
        # Obter coleções disponíveis
        collections = document_service.get_available_rag_collections()
        
        if collections:
            st.write("### Selecione uma coleção")
            for collection in collections:
                if st.button(f"📁 {collection['name']}", key=f"select_{collection['name']}", use_container_width=True):
                    st.session_state.selected_collection = collection['name']
                    st.rerun()
        else:
            st.info("Nenhuma coleção disponível.")
            st.page_link("pages/1_🔍_Scraping.py", label="Criar nova coleção", icon="🔍")
    
    else:
        # Exibir coleção atual e botão para trocar
        st.write(f"### 📁 {st.session_state.selected_collection}")
        if st.button("Trocar coleção", use_container_width=True):
            st.session_state.selected_collection = None
            st.rerun()
        
        st.divider()
        
        # Histórico de conversas
        st.write("### 💬 Histórico")
        
        # Botão para nova conversa
        if st.button("+ Nova conversa", use_container_width=True):
            st.session_state.chat_history = []
            st.session_state.current_conversation_id = conversation_manager.generate_conversation_id()
            st.session_state.conversation_title = "Nova conversa"
            st.session_state.first_message = True
            st.rerun()
        
        # Filtrar conversas por coleção
        conversations = conversation_manager.load_all_conversations()
        collection_conversations = [c for c in conversations if c.get('collection_name') == st.session_state.selected_collection]
        
        if not collection_conversations:
            st.info("Nenhuma conversa salva")
        else:
            for conversation in collection_conversations:
                cols = st.columns([5, 1])
                with cols[0]:
                    if st.button(f"💬 {conversation['title']}", key=f"load_{conversation['id']}", use_container_width=True):
                        st.session_state.current_conversation_id = conversation['id']
                        st.session_state.conversation_title = conversation['title']
                        st.session_state.chat_history = conversation['chat_history']
                        st.session_state.first_message = False
                        st.rerun()
                
                with cols[1]:
                    if st.button("🗑️", key=f"delete_{conversation['id']}"):
                        conversation_manager.delete_conversation(conversation['id'])
                        if conversation['id'] == st.session_state.current_conversation_id:
                            st.session_state.chat_history = []
                            st.session_state.current_conversation_id = conversation_manager.generate_conversation_id()
                            st.session_state.conversation_title = "Nova conversa"
                            st.session_state.first_message = True
                        st.rerun()

# Conteúdo principal
if not st.session_state.selected_collection:
    # Tela de boas-vindas quando nenhuma coleção está selecionada
    st.markdown("""
    <div style="display: flex; justify-content: center; align-items: center; height: 70vh; flex-direction: column; text-align: center;">
        <h1>Docstóteles 📚</h1>
        <p style="font-size: 1.2em; margin: 20px 0;">Selecione uma coleção na barra lateral para começar ou crie uma nova.</p>
        <div>
            <a href="1_🔍_Scraping" target="_self" style="text-decoration: none;">
                <button style="background-color: #4CAF50; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; font-size: 1em;">
                    🔍 Criar Nova Coleção
                </button>
            </a>
        </div>
    </div>
    """, unsafe_allow_html=True)
else:
    # Interface de chat quando uma coleção está selecionada
    
    # Título da conversa
    st.header(st.session_state.conversation_title)
    
    # Encontrar a coleção selecionada
    collections = document_service.get_available_rag_collections()
    collection = next((c for c in collections if c["name"] == st.session_state.selected_collection), None)
    
    if collection:
        # Carregar documentos e criar vector store
        docs = document_service.load_documents_from_directory(collection["path"])
        vector_store = document_service.create_vector_store(docs)
        retriever = document_service.get_retriever(vector_store)
        
        # Container para mensagens do chat
        chat_container = st.container()
        
        with chat_container:
            # Exibir mensagens do histórico
            for role, message in st.session_state.chat_history:
                with st.chat_message(role):
                    st.markdown(message)
            
            # Mensagem inicial se não houver histórico
            if not st.session_state.chat_history:
                with st.chat_message("assistant"):
                    st.markdown(f"👋 Olá! Sou seu assistente especializado na coleção **{st.session_state.selected_collection}**. Como posso ajudar?")
        
        # Campo de entrada de mensagem
        user_message = st.chat_input("Digite sua pergunta aqui...")
        
        if user_message:
            # Se for a primeira mensagem, iniciar processo de geração de título
            if st.session_state.first_message:
                st.session_state.first_message = False
                
                # Salvar temporariamente
                conversation_manager.save_conversation(
                    st.session_state.current_conversation_id,
                    "Nova conversa",
                    [],
                    st.session_state.selected_collection
                )
                
                # Função de callback para atualizar o título
                def update_title(title):
                    conversation_manager.update_conversation_title(
                        st.session_state.current_conversation_id,
                        title
                    )
                    st.session_state.conversation_title = title
                
                # Iniciar processamento assíncrono do título
                ai_service.process_title_async(user_message, update_title)
            
            # Adicionar mensagem do usuário ao histórico
            st.session_state.chat_history.append(("user", user_message))
            
            # Exibir mensagem do usuário na interface
            with st.chat_message("user"):
                st.markdown(user_message)
            
            # Gerar resposta
            with st.chat_message("assistant"):
                # Buscar documentos relevantes
                relevant_docs = document_service.retrieve_relevant_documents(retriever, user_message)
                
                # Criar prompt com contexto
                prompt = ai_service.create_prompt_with_context(
                    user_message, 
                    st.session_state.chat_history[:-1],
                    relevant_docs
                )
                
                # Gerar resposta em stream
                response_placeholder = st.empty()
                response_text = ""
                
                for chunk in ai_service.generate_streaming_response(prompt):
                    response_text += chunk.content
                    response_placeholder.markdown(response_text)
                
                # Adicionar resposta ao histórico
                st.session_state.chat_history.append(("assistant", response_text))
            
            # Salvar conversa
            conversation_manager.save_conversation(
                st.session_state.current_conversation_id,
                st.session_state.conversation_title,
                st.session_state.chat_history,
                st.session_state.selected_collection
            )
            
            # Forçar rerun para atualizar a interface
            st.rerun()
    else:
        st.error(f"Erro: A coleção '{st.session_state.selected_collection}' não foi encontrada.")
        if st.button("Voltar para seleção de coleção"):
            st.session_state.selected_collection = None
            st.rerun()