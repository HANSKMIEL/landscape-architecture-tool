"""Photo model for storing image metadata and organizing visual assets."""

import enum
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from src.models.user import db


class PhotoCategory(enum.Enum):
    """Photo categories for organizing visual assets."""
    PLANT = "plant"
    MATERIAL = "material"
    PROPERTY = "property"
    PROJECT = "project"
    EXAMPLE = "example"
    INSPIRATION = "inspiration"
    REFERENCE = "reference"


class Photo(db.Model):
    """Model for storing photo metadata and file information."""
    
    __tablename__ = "photos"
    
    id = Column(Integer, primary_key=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    thumbnail_path = Column(String(500))
    file_size = Column(Integer)  # Size in bytes
    mime_type = Column(String(100))
    width = Column(Integer)
    height = Column(Integer)
    
    # Categorization
    category = Column(Enum(PhotoCategory), nullable=False)
    title = Column(String(200))
    description = Column(Text)
    alt_text = Column(String(500))  # For accessibility
    
    # Entity relationships (foreign keys)
    plant_id = Column(Integer, ForeignKey("plants.id"), nullable=True)
    material_id = Column(Integer, ForeignKey("products.id"), nullable=True)  # Materials are products
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
    
    # Metadata
    uploaded_by_id = Column(Integer, ForeignKey("user.id"), nullable=False)
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    is_primary = Column(Boolean, default=False)  # Primary photo for entity
    is_public = Column(Boolean, default=True)  # Visible to clients
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    plant = relationship("Plant", back_populates="photos")
    material = relationship("Product", back_populates="photos")
    client = relationship("Client", back_populates="photos") 
    project = relationship("Project", back_populates="photos")
    uploaded_by = relationship("User")
    
    def to_dict(self):
        """Convert photo to dictionary for JSON serialization."""
        return {
            "id": self.id,
            "filename": self.filename,
            "original_filename": self.original_filename,
            "file_path": self.file_path,
            "thumbnail_path": self.thumbnail_path,
            "file_size": self.file_size,
            "mime_type": self.mime_type,
            "width": self.width,
            "height": self.height,
            "category": self.category.value if self.category else None,
            "title": self.title,
            "description": self.description,
            "alt_text": self.alt_text,
            "plant_id": self.plant_id,
            "material_id": self.material_id,
            "client_id": self.client_id,
            "project_id": self.project_id,
            "uploaded_by_id": self.uploaded_by_id,
            "uploaded_at": self.uploaded_at.isoformat() if self.uploaded_at else None,
            "is_primary": self.is_primary,
            "is_public": self.is_public,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }