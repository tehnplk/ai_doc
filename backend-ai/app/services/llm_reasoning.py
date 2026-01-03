"""LLM reasoning service using Google Gemini."""

from pydantic import BaseModel, Field
from google import genai
from google.genai import types

from app.config import get_settings
from app.schemas.document import AssignmentDecision, CandidateInfo

settings = get_settings()


class LLMReasoningService:
    """Service for LLM-based document assignment reasoning."""

    def __init__(self):
        """Initialize Gemini client."""
        self.client = genai.Client(api_key=settings.google_api_key)
        self.model = settings.llm_model

    def _build_prompt(
        self,
        document_summary: str,
        relevant_excerpts: list[str],
        candidates: list[CandidateInfo],
    ) -> str:
        """
        Build the reasoning prompt for the LLM.
        
        Args:
            document_summary: Summary of the document
            relevant_excerpts: Key excerpts from the document
            candidates: List of candidate employees
            
        Returns:
            Formatted prompt string
        """
        candidates_text = "\n".join([
            f"- **{c.employee_id}** ({c.name})\n"
            f"  - Role: {c.role}\n"
            f"  - Responsibility: {c.responsibility_description}"
            for c in candidates
        ])
        
        excerpts_text = "\n---\n".join(relevant_excerpts[:5])  # Limit to 5 excerpts
        
        prompt = f"""คุณเป็นผู้เชี่ยวชาญในการมอบหมายเอกสารให้พนักงานที่รับผิดชอบ

## เอกสาร
**สรุป:** {document_summary}

**เนื้อหาสำคัญ:**
{excerpts_text}

## พนักงานที่เกี่ยวข้อง
{candidates_text}

## คำสั่ง
วิเคราะห์เอกสารและเลือกพนักงาน **1 คน** ที่เหมาะสมที่สุดในการรับผิดชอบเอกสารนี้

พิจารณาจาก:
1. ความรับผิดชอบ (responsibility) ที่ตรงกับเนื้อหาเอกสาร
2. บทบาท (role) ที่เกี่ยวข้อง
3. ความเหมาะสมโดยรวม

ให้ผลลัพธ์เป็น JSON ที่มี:
- owner: employee_id ของพนักงานที่เลือก
- confidence: ความมั่นใจ 0.0-1.0
- reason: เหตุผลในการเลือก (ภาษาไทย)
"""
        return prompt

    async def decide_assignment(
        self,
        document_summary: str,
        relevant_excerpts: list[str],
        candidates: list[CandidateInfo],
    ) -> AssignmentDecision:
        """
        Use LLM to decide document assignment.
        
        Args:
            document_summary: Summary of the document
            relevant_excerpts: Key excerpts from the document
            candidates: List of candidate employees
            
        Returns:
            AssignmentDecision with owner, confidence, and reason
        """
        prompt = self._build_prompt(document_summary, relevant_excerpts, candidates)
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=AssignmentDecision,
            ),
        )
        
        # Parse response
        decision = response.parsed
        
        # Validate owner is in candidates
        valid_ids = [c.employee_id for c in candidates]
        if decision.owner not in valid_ids:
            # Fallback to highest similarity candidate
            decision.owner = candidates[0].employee_id
            decision.confidence = 0.5
            decision.reason = f"LLM เลือกพนักงานที่ไม่อยู่ในรายการ กลับไปใช้ {candidates[0].name} ตาม semantic similarity"
        
        return decision

    async def summarize_document(self, text: str) -> str:
        """
        Generate a summary of the document.
        
        Args:
            text: Full document text
            
        Returns:
            Summary string
        """
        # Limit text length for context
        max_chars = 8000
        truncated = text[:max_chars] if len(text) > max_chars else text
        
        prompt = f"""สรุปเอกสารต่อไปนี้ให้กระชับ ครอบคลุมประเด็นสำคัญ (ไม่เกิน 200 คำ):

{truncated}

สรุป:"""
        
        response = self.client.models.generate_content(
            model=self.model,
            contents=prompt,
        )
        
        return response.text.strip()


# Singleton instance
_llm_service: LLMReasoningService | None = None


def get_llm_service() -> LLMReasoningService:
    """Get or create LLM reasoning service instance."""
    global _llm_service
    if _llm_service is None:
        _llm_service = LLMReasoningService()
    return _llm_service
