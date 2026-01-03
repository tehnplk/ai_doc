"""Document ingestion API endpoints."""

import uuid
from pathlib import Path
from typing import List
from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db import get_db, Document, DocumentChunk
from app.schemas import DocumentResponse, DocumentListResponse
from app.services import (
    get_ocr_service,
    get_chunker_service,
    get_embedding_service,
)
from app.services.semantic import SemanticService

router = APIRouter(prefix="/ingest", tags=["Document Ingestion"])

# Document storage path
DOC_STORAGE_PATH = Path(__file__).parent.parent.parent / "doc"
DOC_STORAGE_PATH.mkdir(exist_ok=True)

# Supported image types
ALLOWED_FILE_TYPES = {
    "image/jpeg": [".jpg", ".jpeg"],
    "image/png": [".png"],
    "image/webp": [".webp"],
    "image/gif": [".gif"],
    "application/pdf": [".pdf"],
}

ALLOWED_EXTENSIONS = [ext for exts in ALLOWED_FILE_TYPES.values() for ext in exts]


def get_mime_type(filename: str) -> str | None:
    """Get MIME type from filename extension."""
    lower = filename.lower()
    for mime, exts in ALLOWED_FILE_TYPES.items():
        if any(lower.endswith(ext) for ext in exts):
            return mime
    return None


@router.post("", response_model=DocumentResponse)
async def ingest_document(
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload and process image document(s).
    
    - Accept single or multiple files (images or PDFs)
    - Extract text using Gemini Vision OCR
    - Chunk the text
    - Generate embeddings
    - Store in database
    
    Supported formats: JPEG, PNG, WebP, GIF
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")
    
    # Validate all files are allowed
    for file in files:
        mime_type = get_mime_type(file.filename)
        if not mime_type:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file.filename}. Allowed: {', '.join(ALLOWED_EXTENSIONS)}"
            )
    
    # Use first filename for document name
    doc_name = files[0].filename
    if len(files) > 1:
        doc_name = f"{files[0].filename} (+{len(files)-1} pages)"
    
    # Generate timestamp for filenames
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
    
    # Create document record
    doc = Document(
        filename=doc_name,
        document_type=get_mime_type(files[0].filename) or "unknown",
        status="processing",
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    
    try:
        # Read all images and save raw files
        images = []
        stored_filenames = []
        
        for idx, file in enumerate(files):
            content = await file.read()
            
            # Check file size (10MB per image)
            if len(content) > 10 * 1024 * 1024:
                raise HTTPException(
                    status_code=400, 
                    detail=f"File {file.filename} exceeds 10MB limit"
                )
            
            # Save raw file to /doc directory with format: originalname_yyyymmddhhmmss.ext
            original_path = Path(file.filename)
            original_stem = original_path.stem  # filename without extension
            original_ext = original_path.suffix.lower()
            
            if len(files) > 1:
                # Multiple files: originalname_yyyymmddhhmmss_page1.ext
                raw_filename = f"{original_stem}_{timestamp}_page{idx + 1}{original_ext}"
            else:
                # Single file: originalname_yyyymmddhhmmss.ext
                raw_filename = f"{original_stem}_{timestamp}{original_ext}"
            
            raw_file_path = DOC_STORAGE_PATH / raw_filename
            raw_file_path.write_bytes(content)
            stored_filenames.append(raw_filename)
            
            mime_type = get_mime_type(file.filename)
            images.append((content, mime_type))
        
        # Update document with stored filename(s)
        doc.stored_filename = ",".join(stored_filenames)
        await db.commit()
        
        # Extract text using Gemini Vision
        ocr_service = get_ocr_service()
        pages = await ocr_service.extract_text_from_images(images)
        
        if not pages or not any(p.text for p in pages):
            doc.status = "failed"
            await db.commit()
            raise HTTPException(status_code=422, detail="Could not extract text from images")
        
        # Chunk text
        chunker = get_chunker_service()
        page_tuples = [(p.page_number, p.text) for p in pages if p.text]
        chunks = chunker.chunk_pages(page_tuples)
        
        if not chunks:
            doc.status = "failed"
            await db.commit()
            raise HTTPException(status_code=422, detail="No text chunks created")
        
        # Generate embeddings
        embedding_service = get_embedding_service()
        semantic_service = SemanticService(db)
        
        for chunk in chunks:
            embedding = await embedding_service.embed_text(chunk.content)
            await semantic_service.save_chunk_embedding(
                doc_id=doc.doc_id,
                page=chunk.page,
                chunk_index=chunk.chunk_index,
                content=chunk.content,
                embedding=embedding,
            )
        
        # Update status
        doc.status = "ready"
        await db.commit()
        await db.refresh(doc)
        
        return doc
        
    except HTTPException:
        raise
    except Exception as e:
        doc.status = "failed"
        await db.commit()
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    skip: int = 0,
    limit: int = 20,
    db: AsyncSession = Depends(get_db),
):
    """List all uploaded documents."""
    result = await db.execute(
        select(Document)
        .order_by(Document.upload_date.desc())
        .offset(skip)
        .limit(limit)
    )
    documents = result.scalars().all()
    
    count_result = await db.execute(select(Document))
    total = len(count_result.scalars().all())
    
    return DocumentListResponse(
        documents=[DocumentResponse.model_validate(d) for d in documents],
        total=total,
    )


@router.get("/{doc_id}", response_model=DocumentResponse)
async def get_document(
    doc_id: uuid.UUID,
    db: AsyncSession = Depends(get_db),
):
    """Get document by ID."""
    result = await db.execute(
        select(Document).where(Document.doc_id == doc_id)
    )
    doc = result.scalar_one_or_none()
    
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return doc
