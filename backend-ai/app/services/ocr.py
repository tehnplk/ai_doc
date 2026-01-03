"""OCR service using Gemini Vision for image text extraction."""

import base64
from dataclasses import dataclass

from google import genai
from google.genai import types

from app.config import get_settings

settings = get_settings()


@dataclass
class ExtractedPage:
    """Represents extracted text from an image."""
    page_number: int
    text: str
    is_scanned: bool = True


class OCRService:
    """Service for extracting text from files (images/PDFs) using Gemini Vision."""

    def __init__(self):
        """Initialize Gemini client."""
        self.client = genai.Client(api_key=settings.google_api_key)
        self.model = settings.llm_model  # gemini-2.5-flash

    async def extract_text_from_image(
        self, 
        image_bytes: bytes, 
        mime_type: str,
        page_number: int = 1,
    ) -> ExtractedPage:
        """
        Extract text from a single file using Gemini Vision.
        
        Args:
            image_bytes: Image file bytes
            mime_type: MIME type (image/jpeg, image/png, etc.)
            page_number: Page number for metadata
            
        Returns:
            ExtractedPage with extracted text
        """
        prompt = """You are an Expert Document Parser. Extract ALL text from this document accurately.
        
Rules:
- Extract text exactly as shown, maintaining structure
- Include all Thai and English text
- Preserve paragraph breaks with double newlines
- If no text found, return "NO_TEXT_FOUND"
- Do NOT add any commentary, just the extracted text

Extracted text:"""

        response = self.client.models.generate_content(
            model=self.model,
            contents=[
                types.Part.from_bytes(
                    data=image_bytes,
                    mime_type=mime_type,
                ),
                prompt,
            ],
        )
        
        text = response.text.strip()
        if text == "NO_TEXT_FOUND":
            text = ""
        
        return ExtractedPage(
            page_number=page_number,
            text=text,
            is_scanned=True,
        )

    async def extract_text_from_images(
        self,
        images: list[tuple[bytes, str]],
    ) -> list[ExtractedPage]:
        """
        Extract text from multiple images.
        
        Args:
            images: List of (image_bytes, mime_type) tuples
            
        Returns:
            List of ExtractedPage objects
        """
        pages = []
        for i, (image_bytes, mime_type) in enumerate(images, start=1):
            page = await self.extract_text_from_image(
                image_bytes=image_bytes,
                mime_type=mime_type,
                page_number=i,
            )
            pages.append(page)
        return pages

    def get_full_text(self, pages: list[ExtractedPage]) -> str:
        """
        Combine all pages into a single text.
        
        Args:
            pages: List of ExtractedPage objects
            
        Returns:
            Combined text
        """
        return "\n\n".join(page.text for page in pages if page.text)


# Singleton instance
_ocr_service: OCRService | None = None


def get_ocr_service() -> OCRService:
    """Get or create OCR service instance."""
    global _ocr_service
    if _ocr_service is None:
        _ocr_service = OCRService()
    return _ocr_service
