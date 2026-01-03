"""Semantic search service using pgvector."""

from uuid import UUID
from sqlalchemy import text, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import DocumentChunk, EmployeeProfile
from app.config import get_settings

settings = get_settings()


class SemanticService:
    """Service for semantic similarity search using pgvector."""

    def __init__(self, db: AsyncSession):
        """
        Initialize with database session.
        
        Args:
            db: Async database session
        """
        self.db = db
        self.top_k = settings.top_k_candidates
        self.threshold = settings.similarity_threshold

    async def find_similar_employees(
        self,
        embedding: list[float],
        top_k: int | None = None,
    ) -> list[tuple[EmployeeProfile, float]]:
        """
        Find employees with similar responsibility embeddings.
        
        Args:
            embedding: Query embedding vector
            top_k: Number of results to return
            
        Returns:
            List of (EmployeeProfile, similarity_score) tuples
        """
        k = top_k or self.top_k
        
        # Convert embedding to string format for pgvector
        embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"
        
        # Use raw SQL with proper text binding
        query = text("""
            SELECT 
                id, employee_id, name, role, responsibility_description,
                created_at, updated_at,
                1 - (embedding <=> cast(:embedding as vector)) as similarity
            FROM employee_profiles
            WHERE embedding IS NOT NULL
            ORDER BY embedding <=> cast(:embedding as vector)
            LIMIT :limit
        """)
        
        result = await self.db.execute(
            query,
            {"embedding": embedding_str, "limit": k}
        )
        rows = result.fetchall()
        
        employees = []
        for row in rows:
            # Build EmployeeProfile from row (embedding not selected for performance)
            employee = EmployeeProfile(
                id=row.id,
                employee_id=row.employee_id,
                name=row.name,
                role=row.role,
                responsibility_description=row.responsibility_description,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            similarity = row.similarity
            employees.append((employee, similarity))
        
        return employees

    async def aggregate_candidates(
        self,
        chunk_embeddings: list[list[float]],
        top_k: int | None = None,
    ) -> list[tuple[EmployeeProfile, float]]:
        """
        Find top candidates by aggregating similarity across all chunks.
        
        Args:
            chunk_embeddings: List of chunk embedding vectors
            top_k: Number of final candidates to return
            
        Returns:
            List of (EmployeeProfile, avg_similarity) tuples
        """
        k = top_k or self.top_k
        
        # Collect all employees and their scores
        employee_scores: dict[str, tuple[EmployeeProfile, list[float]]] = {}
        
        for embedding in chunk_embeddings:
            results = await self.find_similar_employees(embedding, top_k=k * 2)
            for employee, score in results:
                if employee.employee_id not in employee_scores:
                    employee_scores[employee.employee_id] = (employee, [])
                employee_scores[employee.employee_id][1].append(score)
        
        # Calculate average scores
        averaged = []
        for employee_id, (employee, scores) in employee_scores.items():
            avg_score = sum(scores) / len(scores)
            averaged.append((employee, avg_score))
        
        # Sort by average score and return top-k
        averaged.sort(key=lambda x: x[1], reverse=True)
        return averaged[:k]

    async def save_chunk_embedding(
        self,
        doc_id: UUID,
        page: int,
        chunk_index: int,
        content: str,
        embedding: list[float],
    ) -> DocumentChunk:
        """
        Save a document chunk with its embedding.
        
        Args:
            doc_id: Document UUID
            page: Page number
            chunk_index: Chunk index
            content: Chunk text content
            embedding: Embedding vector
            
        Returns:
            Created DocumentChunk
        """
        chunk = DocumentChunk(
            doc_id=doc_id,
            page=page,
            chunk_index=chunk_index,
            content=content,
            embedding=embedding,
        )
        self.db.add(chunk)
        await self.db.commit()
        await self.db.refresh(chunk)
        return chunk

    async def save_employee_embedding(
        self,
        employee_id: str,
        name: str,
        role: str,
        responsibility: str,
        embedding: list[float],
    ) -> EmployeeProfile:
        """
        Save or update employee profile with embedding.
        
        Args:
            employee_id: Unique employee ID
            name: Employee name
            role: Job role/title
            responsibility: Responsibility description
            embedding: Embedding vector
            
        Returns:
            Created/updated EmployeeProfile
        """
        # Check if exists
        result = await self.db.execute(
            select(EmployeeProfile).where(
                EmployeeProfile.employee_id == employee_id
            )
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            existing.name = name
            existing.role = role
            existing.responsibility_description = responsibility
            existing.embedding = embedding
            await self.db.commit()
            await self.db.refresh(existing)
            return existing
        else:
            employee = EmployeeProfile(
                employee_id=employee_id,
                name=name,
                role=role,
                responsibility_description=responsibility,
                embedding=embedding,
            )
            self.db.add(employee)
            await self.db.commit()
            await self.db.refresh(employee)
            return employee
