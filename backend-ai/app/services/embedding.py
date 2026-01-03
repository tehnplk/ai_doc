"""Embedding service using Google Gemini."""

from google import genai
from google.genai import types

from app.config import get_settings

settings = get_settings()


class EmbeddingService:
    """Service for generating embeddings using Gemini."""

    def __init__(self):
        """Initialize the Gemini client."""
        self.client = genai.Client(api_key=settings.google_api_key)
        self.model = settings.embedding_model

    async def embed_text(self, text: str) -> list[float]:
        """
        Generate embedding for a single text.
        
        Args:
            text: Text to embed
            
        Returns:
            List of floats representing the embedding vector
        """
        response = self.client.models.embed_content(
            model=self.model,
            contents=text,
        )
        return response.embeddings[0].values

    async def embed_texts(self, texts: list[str]) -> list[list[float]]:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            List of embedding vectors
        """
        embeddings = []
        for text in texts:
            embedding = await self.embed_text(text)
            embeddings.append(embedding)
        return embeddings


# Singleton instance
_embedding_service: EmbeddingService | None = None


def get_embedding_service() -> EmbeddingService:
    """Get or create embedding service instance."""
    global _embedding_service
    if _embedding_service is None:
        _embedding_service = EmbeddingService()
    return _embedding_service
