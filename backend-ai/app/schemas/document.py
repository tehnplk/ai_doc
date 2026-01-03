"""Pydantic schemas for API request/response."""

from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, Field


# === Document Schemas ===

class DocumentCreate(BaseModel):
    """Schema for document creation."""
    filename: str
    document_type: Optional[str] = None


class DocumentResponse(BaseModel):
    """Schema for document response."""
    doc_id: UUID
    filename: str
    stored_filename: Optional[str]
    document_type: Optional[str]
    status: str
    upload_date: datetime

    class Config:
        from_attributes = True


class DocumentListResponse(BaseModel):
    """Schema for list of documents."""
    documents: list[DocumentResponse]
    total: int


# === Employee Schemas ===

class EmployeeCreate(BaseModel):
    """Schema for employee creation."""
    employee_id: str
    name: str
    role: str
    responsibility_description: str


class EmployeeResponse(BaseModel):
    """Schema for employee response."""
    employee_id: str
    name: str
    role: str
    responsibility_description: str
    created_at: datetime

    class Config:
        from_attributes = True


# === Assignment Schemas ===

class AssignmentDecision(BaseModel):
    """Schema for LLM assignment decision."""
    owner: str = Field(..., description="Employee ID of the document owner")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")
    reason: str = Field(..., description="Reasoning for the decision")


class AssignmentResponse(BaseModel):
    """Schema for assignment response."""
    doc_id: UUID
    employee_id: str
    employee_name: Optional[str]
    confidence: float
    reason: str
    created_at: datetime

    class Config:
        from_attributes = True


class CandidateInfo(BaseModel):
    """Schema for candidate employee info."""
    employee_id: str
    name: str
    role: str
    responsibility_description: str
    similarity_score: float


class AssignmentRequest(BaseModel):
    """Schema for assignment request."""
    force_reassign: bool = False


# === Feedback Schemas ===

class FeedbackCreate(BaseModel):
    """Schema for manual override feedback."""
    doc_id: UUID
    correct_employee_id: str
    reason: Optional[str] = None


class FeedbackResponse(BaseModel):
    """Schema for feedback response."""
    success: bool
    message: str
