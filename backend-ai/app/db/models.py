"""SQLAlchemy models for document assignment system."""

import uuid
from datetime import datetime
from sqlalchemy import Column, String, Text, Integer, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from pgvector.sqlalchemy import Vector

from app.db.database import Base


class Document(Base):
    """Document metadata table."""

    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(UUID(as_uuid=True), default=uuid.uuid4, unique=True, nullable=False)
    filename = Column(String(255), nullable=False)
    stored_filename = Column(String(500))  # Filename on disk: original_yyyymmddhhmmss.ext
    document_type = Column(String(100))
    status = Column(String(50), default="pending")
    upload_date = Column(DateTime, default=datetime.utcnow)


class DocumentChunk(Base):
    """Document chunks with embeddings."""

    __tablename__ = "document_chunks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(UUID(as_uuid=True), ForeignKey("documents.doc_id"), nullable=False)
    page = Column(Integer)
    chunk_index = Column(Integer)
    content = Column(Text)
    embedding = Column(Vector(3072))  # Gemini embedding dimension
    created_at = Column(DateTime, default=datetime.utcnow)


class EmployeeProfile(Base):
    """Employee profiles with responsibility embeddings."""

    __tablename__ = "employee_profiles"

    id = Column(Integer, primary_key=True, autoincrement=True)
    employee_id = Column(String(100), unique=True, nullable=False)
    name = Column(String(255))
    role = Column(String(100))
    responsibility_description = Column(Text)
    embedding = Column(Vector(3072))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


class AssignmentLog(Base):
    """Assignment audit log."""

    __tablename__ = "assignment_logs"

    id = Column(Integer, primary_key=True, autoincrement=True)
    doc_id = Column(UUID(as_uuid=True), ForeignKey("documents.doc_id"), nullable=False)
    employee_id = Column(String(100), ForeignKey("employee_profiles.employee_id"))
    confidence = Column(Float)
    reason = Column(Text)
    is_manual_override = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
