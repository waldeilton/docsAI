import streamlit as st
import os
import time
from services.scraping_service import ScrapingService
from core.database import ScrapingProjectManager
from core.config import PATHS

# Configuração da página
st.set_page_config(
    page_title="Docstóteles - Scraping",
    page_icon="🔍",
    layout="wide"
)

# Título principal
st.title("Web Scraping 🔍")
st.write("Extraia conteúdo de sites para criar novas coleções de documentos.")

# Inicializar serviços
scraping_service = ScrapingService()
project_manager = ScrapingProjectManager()

# Inicializar estados da sessão
if 'scraping_in_progress' not in st.session_state:
    st.session_state.scraping_in_progress = False
if 'scraping_progress' not in st.session_state:
    st.session_state.scraping_progress = 0.0
if 'scraping_status' not in st.session_state:
    st.session_state.scraping_status = ""
if 'viewing_document' not in st.session_state:
    st.session_state.viewing_document = False
if 'view_collection' not in st.session_state:
    st.session_state.view_collection = None
if 'view_file' not in st.session_state:
    st.session_state.view_file = None

# Tabs para as diferentes seções
tab1, tab2, tab3 = st.tabs(["Nova Coleção", "Coleções Existentes", "Visualizar Documentos"])

# Tab 1: Nova Coleção
with tab1:
    # Formulário de scraping em container para melhor aparência
    with st.container():
        st.subheader("Criar Nova Coleção")
        
        # Formulário de scraping com layout mais limpo
        with st.form("scraping_form"):
            url = st.text_input("URL do site", 
                              help="Coloque a URL completa com http:// ou https://",
                              placeholder="https://exemplo.com/documentacao")
            
            project_name = st.text_input("Nome da coleção", 
                                       help="Nome único para identificar esta coleção",
                                       placeholder="minha-colecao")
            
            # Colocar o checkbox e botão na mesma linha
            cols = st.columns([3, 2])
            with cols[0]:
                overwrite = st.checkbox("Sobrescrever se já existir", 
                                      help="Se marcado, substituirá uma coleção existente com o mesmo nome")
            
            # Botão de envio mais destacado
            submitted = st.form_submit_button("Iniciar Scraping", use_container_width=True)
        
        # Processar formulário
        if submitted and url and project_name:
            # Checar se o projeto existe
            project_path = os.path.join(PATHS["rag_directory"], project_name)
            if os.path.exists(project_path) and not overwrite:
                st.error(f"Uma coleção com o nome '{project_name}' já existe. Marque a opção para sobrescrever ou escolha outro nome.")
            else:
                # Iniciar scraping
                st.session_state.scraping_in_progress = True
                st.session_state.scraping_progress = 0.0
                st.session_state.scraping_status = "Iniciando..."
        
        # Exibir progresso
        if st.session_state.scraping_in_progress:
            st.subheader("Progresso")
            
            progress_bar = st.progress(st.session_state.scraping_progress)
            status_text = st.empty()
            status_text.write(st.session_state.scraping_status)
            
            # Processo de scraping
            try:
                def progress_callback(progress, status):
                    st.session_state.scraping_progress = progress
                    st.session_state.scraping_status = status
                
                # Executar processo de scraping
                result = scraping_service.run_full_scraping_process(
                    url=url,
                    project_name=project_name,
                    progress_callback=progress_callback
                )
                
                # Atualizar UI com resultado
                if result.get("success"):
                    progress_bar.progress(1.0)
                    status_text.success(f"Concluído! 90 arquivos salvos em '{project_name}'")
                    
                    # Adicionar botão para voltar para a página principal e usar coleção
                    if st.button("Usar esta coleção no chat", use_container_width=True):
                        st.session_state.selected_collection = project_name
                        st.switch_page("Home.py")
                else:
                    status_text.error(f"Erro: {result.get('error')}")
                
                # Resetar estado
                st.session_state.scraping_in_progress = False
                
            except Exception as e:
                status_text.error(f"Erro inesperado: {str(e)}")
                st.session_state.scraping_in_progress = False

# Tab 2: Coleções Existentes
with tab2:
    st.subheader("Coleções Disponíveis")
    
    # Obter projetos
    projects = project_manager.get_all_projects()
    
    if not projects:
        st.info("Nenhuma coleção criada ainda. Vá para a aba 'Nova Coleção' para criar uma.")
    else:
        # Lista de coleções com cards
        for i, project in enumerate(projects):
            # Criar card com bordas e background sutis
            with st.container():
                # Adicionar linha divisória, exceto para o primeiro item
                if i > 0:
                    st.divider()
                
                # Cabeçalho do card com título da coleção
                st.subheader(f"📁 {project['name']}")
                
                # Informações da coleção
                st.write(f"**Quantidade de arquivos:** {project['file_count']}")
                st.write(f"**URL Fonte:** {project['source_url']}")
                st.write(f"**Data de criação:** {project['created_at'][:10]}")
                
                # Botões de ação na mesma linha
                col1, col2, col3 = st.columns([1, 1, 1])
                with col1:
                    # Botão para usar coleção
                    if st.button("💬 Usar no chat", key=f"use_{project['id']}", use_container_width=True):
                        st.session_state.selected_collection = project["name"]
                        st.switch_page("Home.py")
                
                with col2:
                    # Botão para visualizar documentos
                    if st.button("👁️ Visualizar", key=f"view_{project['id']}", use_container_width=True):
                        st.session_state.view_collection = project["name"]
                        st.session_state.viewing_document = True
                        st.session_state.view_file = None
                        st.switch_page("pages/1_🔍_Scraping.py")  # Recarrega a página, mas vai para a tab 3
                
                with col3:
                    # Botão para excluir
                    if st.button("🗑️ Excluir", key=f"del_{project['id']}", use_container_width=True):
                        # Excluir diretório
                        project_path = os.path.join(PATHS["rag_directory"], project["name"])
                        if os.path.exists(project_path):
                            import shutil
                            shutil.rmtree(project_path)
                        
                        # Excluir do banco
                        project_manager.delete_project(project["id"])
                        st.success(f"Coleção '{project['name']}' excluída com sucesso.")
                        st.rerun()

# Tab 3: Visualizar Documentos
with tab3:
    st.subheader("Explorar Documentos")
    
    # Carregar automaticamente a tab se estiver visualizando
    if st.session_state.viewing_document:
        tab3.active = True
    
    rag_dir = PATHS["rag_directory"]
    
    if os.path.exists(rag_dir):
        collections = [d for d in os.listdir(rag_dir) 
                     if os.path.isdir(os.path.join(rag_dir, d))]
        
        if collections:
            # Seleção de coleção (use valor de state se disponível)
            selected_collection = st.selectbox(
                "Selecione uma coleção", 
                collections,
                index=collections.index(st.session_state.view_collection) if st.session_state.view_collection in collections else 0
            )
            
            if selected_collection:
                collection_path = os.path.join(rag_dir, selected_collection)
                files = [f for f in os.listdir(collection_path) 
                       if f.endswith('.md') and os.path.isfile(os.path.join(collection_path, f))]
                
                if files:
                    # Exibir arquivos como botões para seleção mais visual
                    st.write("##### Selecione um arquivo para visualizar:")
                    
                    # Organizar arquivos em linhas de 3 botões
                    cols = st.columns(3)
                    for i, file in enumerate(files):
                        with cols[i % 3]:
                            # Verificar se o botão está ativo
                            is_active = st.session_state.view_file == file
                            
                            if st.button(
                                f"📄 {file}", 
                                key=f"file_{file}",
                                use_container_width=True,
                                type="primary" if is_active else "secondary"
                            ):
                                st.session_state.view_file = file
                                st.rerun()
                    
                    # Exibir conteúdo do arquivo selecionado
                    if st.session_state.view_file in files:
                        st.divider()
                        st.subheader(f"📄 {st.session_state.view_file}")
                        
                        file_path = os.path.join(collection_path, st.session_state.view_file)
                        
                        try:
                            with open(file_path, 'r', encoding='utf-8') as f:
                                content = f.read()
                            
                            # Métricas de arquivo
                            col1, col2, col3 = st.columns(3)
                            with col1:
                                st.metric("Tamanho", f"{os.path.getsize(file_path)/1024:.1f} KB")
                            with col2:
                                st.metric("Linhas", len(content.splitlines()))
                            with col3:
                                st.metric("Palavras", len(content.split()))
                            
                            # Exibir conteúdo em guias diferentes
                            content_tab1, content_tab2 = st.tabs(["Texto", "Markdown"])
                            with content_tab1:
                                st.text_area("Conteúdo do arquivo", content, height=400)
                            with content_tab2:
                                st.markdown(content)
                            
                        except Exception as e:
                            st.error(f"Erro ao ler o arquivo: {str(e)}")
                else:
                    st.info(f"Não há arquivos Markdown na coleção '{selected_collection}'.")
        else:
            st.info("Nenhuma coleção disponível para visualização.")
    else:
        st.info("Diretório de documentos não encontrado.")

# Link para voltar à página principal
st.sidebar.write("---")
if st.sidebar.button("← Voltar para Chat", use_container_width=True):
    st.session_state.viewing_document = False
    st.switch_page("Home.py")