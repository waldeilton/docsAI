from dataclasses import dataclass, field
from typing import List, Tuple, Optional
from datetime import datetime

@dataclass
class Message:
    """
    Represents a single message in a conversation
    """
    role: str  # "user" or "assistant"
    content: str
    timestamp: datetime = field(default_factory=datetime.now)
    
    def to_tuple(self) -> Tuple[str, str]:
        """Convert to a simple (role, content) tuple format"""
        return (self.role, self.content)
    
    @staticmethod
    def from_tuple(data: Tuple[str, str]) -> 'Message':
        """Create a Message from a (role, content) tuple"""
        role, content = data
        return Message(role=role, content=content)


@dataclass
class Conversation:
    """
    Represents a complete conversation with multiple messages
    """
    id: str
    title: str
    messages: List[Message] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    collection_name: Optional[str] = None
    
    def add_message(self, role: str, content: str) -> Message:
        """Add a new message to the conversation"""
        message = Message(role=role, content=content)
        self.messages.append(message)
        self.updated_at = datetime.now()
        return message
    
    def to_dict(self) -> dict:
        """Convert to a dictionary for storage"""
        return {
            "id": self.id,
            "title": self.title,
            "chat_history": [(msg.role, msg.content) for msg in self.messages],
            "timestamp": self.updated_at.isoformat(),
            "collection_name": self.collection_name
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Conversation':
        """Create a Conversation from a dictionary"""
        conversation = Conversation(
            id=data["id"],
            title=data["title"],
            created_at=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
            updated_at=datetime.fromisoformat(data.get("timestamp", datetime.now().isoformat())),
            collection_name=data.get("collection_name")
        )
        
        # Add messages
        for role, content in data.get("chat_history", []):
            conversation.add_message(role, content)
        
        return conversation