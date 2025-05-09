import streamlit as st
from streamlit_js_eval import streamlit_js_eval
import logging

logger = logging.getLogger(__name__)

def render_chat_interface(chat_history, on_message_submit):
    """
    Render the chat interface with messages and input
    
    Args:
        chat_history: List of (role, message) tuples
        on_message_submit: Callback function for new messages
    """
    # Display chat history
    for i, (role, message) in enumerate(chat_history):
        with st.chat_message(role):
            st.markdown(message)
            
            # Add copy button for assistant messages
            if role == "assistant":
                col1, col2 = st.columns([0.95, 0.05])
                with col2:
                    st.button(
                        "📋", 
                        key=f"copy_message_{i}", 
                        help="Copiar resposta completa",
                        on_click=lambda msg=message: streamlit_js_eval(
                            f"navigator.clipboard.writeText('{msg.replace('\'', '\\\'').replace('\"', '\\\"').replace(chr(10), '\\n')}')"
                        )
                    )
    
    # Empty chat message for first visit
    if not chat_history:
        with st.chat_message("assistant"):
            welcome_message = (
                "👋 Olá! Sou seu assistente especializado na documentação carregada. "
                "Estou aqui para ajudar com qualquer dúvida ou explicação que você precise. "
                "Como posso ajudar você hoje?"
            )
            st.write(welcome_message)
    
    # User input
    user_message = st.chat_input("Digite sua pergunta aqui...")
    
    # Process input
    if user_message:
        # Call the callback function with the user message
        on_message_submit(user_message)

def render_streaming_response(ai_service, prompt, callback=None):
    """
    Render a streaming response from the AI service
    
    Args:
        ai_service: The AIService instance
        prompt: The prompt to send to the AI
        callback: Optional callback function to call with the final response
    
    Returns:
        The complete response text
    """
    response_container = st.empty()
    response_text = ""
    
    # Stream response
    for chunk in ai_service.generate_streaming_response(prompt):
        content_chunk = chunk.content
        response_text += content_chunk
        response_container.markdown(response_text)
    
    # Add copy button
    col1, col2 = st.columns([0.95, 0.05])
    with col2:
        st.button(
            "📋", 
            key="copy_current", 
            help="Copiar resposta completa",
            on_click=lambda: streamlit_js_eval(
                f"navigator.clipboard.writeText('{response_text.replace('\'', '\\\'').replace('\"', '\\\"').replace(chr(10), '\\n')}')"
            )
        )
    
    # Call the callback with the final response if provided
    if callback:
        callback(response_text)
    
    return response_text