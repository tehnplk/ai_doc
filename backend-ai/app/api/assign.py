"""Document assignment API endpoints."""

import uuid
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db import get_db, Document, DocumentChunk, EmployeeProfile, AssignmentLog
from app.schemas import (
    AssignmentResponse,
    AssignmentRequest,
    CandidateInfo,
    EmployeeCreate,
    EmployeeResponse,
    FeedbackCreate,
    FeedbackResponse,
)
from app.services import get_embedding_service, get_llm_service
from app.services.semantic import SemanticService
from app.config import get_settings

settings = get_settings()
router = APIRouter(tags=["Assignment"])


@router.post("/assign/{doc_id}", response_model=AssignmentResponse)
async def assign_document(
    doc_id: uuid.UUID,
    request: AssignmentRequest = AssignmentRequest(),
    db: AsyncSession = Depends(get_db),
):
    """
    Assign a document to the most appropriate employee.
    
    - Find candidate employees using semantic search
    - Use LLM to reason and decide
    - Log the assignment
    """
    # Get document
    result = await db.execute(
        select(Document).where(Document.doc_id == doc_id)
    )
    doc = result.scalar_one_or_none()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    if doc.status != "ready":
        raise HTTPException(
            status_code=400, 
            detail=f"Document is not ready for assignment (status: {doc.status})"
        )
    
    # Check existing assignment
    if not request.force_reassign:
        existing = await db.execute(
            select(AssignmentLog)
            .where(AssignmentLog.doc_id == doc_id)
            .order_by(AssignmentLog.created_at.desc())
            .limit(1)
        )
        existing_log = existing.scalar_one_or_none()
        if existing_log:
            # Get employee info
            emp_result = await db.execute(
                select(EmployeeProfile)
                .where(EmployeeProfile.employee_id == existing_log.employee_id)
            )
            emp = emp_result.scalar_one_or_none()
            
            return AssignmentResponse(
                doc_id=doc_id,
                employee_id=existing_log.employee_id,
                employee_name=emp.name if emp else None,
                confidence=existing_log.confidence,
                reason=existing_log.reason,
                created_at=existing_log.created_at,
            )
    
    # Get document chunks
    chunks_result = await db.execute(
        select(DocumentChunk)
        .where(DocumentChunk.doc_id == doc_id)
        .order_by(DocumentChunk.chunk_index)
    )
    chunks = chunks_result.scalars().all()
    
    if not chunks:
        raise HTTPException(status_code=422, detail="No document chunks found")
    
    # Get chunk embeddings - convert numpy array to list if needed
    chunk_embeddings = []
    for c in chunks:
        if c.embedding is not None:
            # pgvector returns numpy array, convert to list
            emb = c.embedding
            if hasattr(emb, 'tolist'):
                emb = emb.tolist()
            elif not isinstance(emb, list):
                emb = list(emb)
            chunk_embeddings.append(emb)
    
    if not chunk_embeddings:
        raise HTTPException(status_code=422, detail="No chunk embeddings found")
    
    # Find candidate employees
    semantic_service = SemanticService(db)
    candidates_with_scores = await semantic_service.aggregate_candidates(
        chunk_embeddings,
        top_k=settings.top_k_candidates,
    )
    
    if not candidates_with_scores:
        raise HTTPException(
            status_code=422, 
            detail="No employee candidates found. Please add employee profiles first."
        )
    
    # Check if below threshold - may need manual review
    top_score = candidates_with_scores[0][1] if candidates_with_scores else 0
    if top_score < settings.similarity_threshold:
        # Still proceed but note low confidence
        pass
    
    # Build candidate info for LLM
    candidates = [
        CandidateInfo(
            employee_id=emp.employee_id,
            name=emp.name,
            role=emp.role,
            responsibility_description=emp.responsibility_description,
            similarity_score=score,
        )
        for emp, score in candidates_with_scores
    ]
    
    # Get document text for LLM
    relevant_excerpts = [c.content for c in chunks[:5]]  # Top 5 chunks
    
    # Generate summary
    llm_service = get_llm_service()
    full_text = "\n".join([c.content for c in chunks])
    summary = await llm_service.summarize_document(full_text)
    
    # LLM reasoning
    decision = await llm_service.decide_assignment(
        document_summary=summary,
        relevant_excerpts=relevant_excerpts,
        candidates=candidates,
    )
    
    # Save assignment log
    assignment_log = AssignmentLog(
        doc_id=doc_id,
        employee_id=decision.owner,
        confidence=decision.confidence,
        reason=decision.reason,
    )
    db.add(assignment_log)
    await db.commit()
    await db.refresh(assignment_log)
    
    # Get employee name
    emp_result = await db.execute(
        select(EmployeeProfile)
        .where(EmployeeProfile.employee_id == decision.owner)
    )
    emp = emp_result.scalar_one_or_none()
    
    return AssignmentResponse(
        doc_id=doc_id,
        employee_id=decision.owner,
        employee_name=emp.name if emp else None,
        confidence=decision.confidence,
        reason=decision.reason,
        created_at=assignment_log.created_at,
    )


@router.get("/assignments/{doc_id}", response_model=list[AssignmentResponse])
async def get_assignments(
    doc_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get all assignment logs for a document."""
    result = await db.execute(
        select(AssignmentLog)
        .where(AssignmentLog.doc_id == doc_id)
        .order_by(AssignmentLog.created_at.desc())
    )
    logs = result.scalars().all()
    
    responses = []
    for log in logs:
        emp_result = await db.execute(
            select(EmployeeProfile)
            .where(EmployeeProfile.employee_id == log.employee_id)
        )
        emp = emp_result.scalar_one_or_none()
        
        responses.append(AssignmentResponse(
            doc_id=doc_id,
            employee_id=log.employee_id,
            employee_name=emp.name if emp else None,
            confidence=log.confidence,
            reason=log.reason,
            created_at=log.created_at,
        ))
    
    return responses


@router.post("/employees", response_model=EmployeeResponse)
async def create_employee(
    employee: EmployeeCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Create or update an employee profile.
    
    - Generate embedding from responsibility description
    - Store in database
    """
    # Generate embedding
    embedding_service = get_embedding_service()
    text_to_embed = f"{employee.role}: {employee.responsibility_description}"
    embedding = await embedding_service.embed_text(text_to_embed)
    
    # Save employee
    semantic_service = SemanticService(db)
    emp = await semantic_service.save_employee_embedding(
        employee_id=employee.employee_id,
        name=employee.name,
        role=employee.role,
        responsibility=employee.responsibility_description,
        embedding=embedding,
    )
    
    return emp


@router.get("/employees", response_model=list[EmployeeResponse])
async def list_employees(
    db: AsyncSession = Depends(get_db),
):
    """List all employee profiles."""
    result = await db.execute(
        select(EmployeeProfile).order_by(EmployeeProfile.name)
    )
    return result.scalars().all()


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    feedback: FeedbackCreate,
    db: AsyncSession = Depends(get_db),
):
    """
    Submit manual override feedback.
    
    - Record the correction
    - Optionally update employee embedding (learning loop)
    """
    # Verify document exists
    doc_result = await db.execute(
        select(Document).where(Document.doc_id == feedback.doc_id)
    )
    doc = doc_result.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Verify employee exists
    emp_result = await db.execute(
        select(EmployeeProfile)
        .where(EmployeeProfile.employee_id == feedback.correct_employee_id)
    )
    emp = emp_result.scalar_one_or_none()
    if not emp:
        raise HTTPException(status_code=404, detail="Employee not found")
    
    # Create override log
    override_log = AssignmentLog(
        doc_id=feedback.doc_id,
        employee_id=feedback.correct_employee_id,
        confidence=1.0,  # Manual = 100% confidence
        reason=feedback.reason or "Manual override by administrator",
        is_manual_override=True,
    )
    db.add(override_log)
    await db.commit()
    
    return FeedbackResponse(
        success=True,
        message=f"Document reassigned to {emp.name} ({emp.employee_id})",
    )
