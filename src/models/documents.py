from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
import os
from core.config import PATHS

@dataclass
class DocumentCollection:
    """
    Represents a collection of documents from a single source
    """
    name: str
    source_url: str
    file_count: int
    id: str
    created_at: datetime = field(default_factory=datetime.now)
    status: str = "completed"
    
    @property
    def directory_path(self) -> str:
        """Get the directory path for this collection"""
        return os.path.join(PATHS["rag_directory"], self.name)
    
    def to_dict(self) -> dict:
        """Convert to a dictionary for storage"""
        return {
            "id": self.id,
            "name": self.name,
            "source_url": self.source_url,
            "file_count": self.file_count,
            "created_at": self.created_at.isoformat(),
            "status": self.status
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'DocumentCollection':
        """Create a DocumentCollection from a dictionary"""
        return DocumentCollection(
            id=data["id"],
            name=data["name"],
            source_url=data["source_url"],
            file_count=data["file_count"],
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            status=data.get("status", "completed")
        )


@dataclass
class Document:
    """
    Represents a single document within a collection
    """
    filename: str
    collection_name: str
    content: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def file_path(self) -> str:
        """Get the full file path for this document"""
        return os.path.join(PATHS["rag_directory"], self.collection_name, self.filename)
    
    def load_content(self) -> str:
        """Load the document content from file if not already loaded"""
        if self.content is None:
            try:
                with open(self.file_path, 'r', encoding='utf-8') as f:
                    self.content = f.read()
            except Exception as e:
                self.content = f"Error loading document: {str(e)}"
        
        return self.content
    
    @property
    def word_count(self) -> int:
        """Count the number of words in the document content"""
        content = self.load_content()
        return len(content.split())
    
    @property
    def character_count(self) -> int:
        """Count the number of characters in the document content"""
        content = self.load_content()
        return len(content)
    
    def to_dict(self) -> dict:
        """Convert to a dictionary for storage"""
        return {
            "filename": self.filename,
            "collection_name": self.collection_name,
            "metadata": self.metadata
        }
    
    @staticmethod
    def from_dict(data: dict) -> 'Document':
        """Create a Document from a dictionary"""
        return Document(
            filename=data["filename"],
            collection_name=data["collection_name"],
            metadata=data.get("metadata", {})
        )


@dataclass
class ScrapingJob:
    """
    Represents a web scraping job
    """
    url: str
    project_name: str
    id: str
    status: str = "pending"
    progress: float = 0.0
    message: str = "Initializing..."
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    file_count: int = 0
    
    def to_dict(self) -> dict:
        """Convert to a dictionary for storage"""
        data = {
            "id": self.id,
            "url": self.url,
            "project_name": self.project_name,
            "status": self.status,
            "progress": self.progress,
            "message": self.message,
            "created_at": self.created_at.isoformat(),
            "file_count": self.file_count
        }
        
        if self.completed_at:
            data["completed_at"] = self.completed_at.isoformat()
            
        return data
    
    @staticmethod
    def from_dict(data: dict) -> 'ScrapingJob':
        """Create a ScrapingJob from a dictionary"""
        job = ScrapingJob(
            id=data["id"],
            url=data["url"],
            project_name=data["project_name"],
            status=data.get("status", "pending"),
            progress=data.get("progress", 0.0),
            message=data.get("message", ""),
            created_at=datetime.fromisoformat(data.get("created_at", datetime.now().isoformat())),
            file_count=data.get("file_count", 0)
        )
        
        if "completed_at" in data and data["completed_at"]:
            job.completed_at = datetime.fromisoformat(data["completed_at"])
            
        return job