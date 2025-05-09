import logging
from langchain_openai.chat_models import ChatOpenAI
from core.config import APP_CONFIG
import threading

logger = logging.getLogger(__name__)

class AIService:
    """Service for AI model interactions"""
    
    def __init__(self):
        """Initialize AI models"""
        # Model for streaming chat responses
        self.chat_model = ChatOpenAI(
            temperature=APP_CONFIG["temperature"],
            model=APP_CONFIG["default_model"],
            streaming=True
        )
        
        # Non-streaming model for title generation
        self.title_model = ChatOpenAI(
            temperature=APP_CONFIG["title_temperature"],
            model=APP_CONFIG["title_model"],
            streaming=False
        )
        
        logger.info(f"AI service initialized with models: {APP_CONFIG['default_model']} and {APP_CONFIG['title_model']}")
    
    def generate_conversation_title(self, question):
        """Generate a concise and intelligent title for a conversation"""
        prompt = f"""
        Based on the following question, create a concise and relevant title for a conversation.
        The title should have AT MOST 5 words and capture the essence of the question.
        
        Question: "{question}"
        
        Return ONLY the title, without quotes or additional punctuation.
        """
        
        try:
            response = self.title_model.invoke(prompt)
            title = response.content.strip()
            
            # Check if the title is within limits
            words = title.split()
            if len(words) > 5:
                title = " ".join(words[:5])
            
            return title
        except Exception as e:
            logger.error(f"Error generating title: {str(e)}")
            # In case of error, use a simple title
            words = question.split()
            return " ".join(words[:5]) + "..." if len(words) > 5 else question
    
    def process_title_async(self, question, callback):
        """Process the title asynchronously and call the callback when done"""
        
        def worker():
            # Generate the title using the LLM
            title = self.generate_conversation_title(question)
            
            # Call the callback with the generated title
            callback(title)
        
        # Start in a separate thread to avoid blocking the UI
        thread = threading.Thread(target=worker)
        thread.daemon = True
        thread.start()
    
    def create_prompt_with_context(self, question, chat_history, documents):
        """Create a prompt with context from documents and chat history"""
        prompt_template = f"""
        You are an experienced teacher and mentor specializing in the loaded documentation. You are deeply familiar with all the content of the documents and can explain them with clarity and depth.
        
        Your role is to:
        1. Provide complete and accurate explanations based on the documentation
        2. Help the user understand complex concepts with practical examples
        3. Offer step-by-step guidance when requested
        4. Share well-formatted and commented code examples when relevant
        5. Respond in a clear, concise, and friendly manner
        6. Never say "I don't know" or "I can't help" - always seek the best possible answer
        
        When sharing code:
        - Use markdown code blocks (```) with the language specified
        - Comment the code appropriately
        - Explain the logic and purpose of the code
        
        Conversation history:
        """
        
        # Add history pairs
        history_pairs = []
        for i in range(0, len(chat_history), 2):
            if i+1 < len(chat_history):
                user_msg = chat_history[i][1]
                ai_msg = chat_history[i+1][1]
                prompt_template += f"\nUser: {user_msg}\nAssistant: {ai_msg}\n"
        
        # Add current question
        prompt_template += f"\nUser: {question}\n"
        
        # Add context from documents
        prompt_template += "\nHere is relevant information from the documents that may help answer the question:\n"
        for i, doc in enumerate(documents):
            prompt_template += f"Document {i+1}:\n{doc.page_content}\n\n"
        
        prompt_template += "\nAssistant: "
        return prompt_template
    
    def generate_streaming_response(self, prompt):
        """Generate a streaming response from the chat model"""
        return self.chat_model.stream(prompt)