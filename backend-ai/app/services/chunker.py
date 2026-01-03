"""Text chunking service."""

import re
from dataclasses import dataclass

from app.config import get_settings

settings = get_settings()


@dataclass
class TextChunk:
    """Represents a chunk of text with metadata."""
    content: str
    page: int
    chunk_index: int


class ChunkerService:
    """Service for chunking text into smaller pieces."""

    def __init__(
        self,
        chunk_size: int = settings.chunk_size,
        chunk_overlap: int = settings.chunk_overlap,
    ):
        """
        Initialize chunker.
        
        Args:
            chunk_size: Target number of tokens per chunk
            chunk_overlap: Number of overlapping tokens between chunks
        """
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def _estimate_tokens(self, text: str) -> int:
        """
        Estimate token count (rough approximation).
        Thai text: ~1.5 chars per token
        English text: ~4 chars per token
        """
        # Count Thai characters
        thai_chars = len(re.findall(r'[\u0E00-\u0E7F]', text))
        other_chars = len(text) - thai_chars
        
        thai_tokens = thai_chars / 1.5
        other_tokens = other_chars / 4
        
        return int(thai_tokens + other_tokens)

    def _split_by_sentences(self, text: str) -> list[str]:
        """Split text into sentences."""
        # Handle Thai and English sentence endings
        pattern = r'(?<=[.!?။。\n])\s+'
        sentences = re.split(pattern, text)
        return [s.strip() for s in sentences if s.strip()]

    def chunk_text(self, text: str, page: int = 1) -> list[TextChunk]:
        """
        Split text into chunks with overlap.
        
        Args:
            text: Text to chunk
            page: Page number for metadata
            
        Returns:
            List of TextChunk objects
        """
        sentences = self._split_by_sentences(text)
        chunks = []
        current_chunk = []
        current_tokens = 0
        chunk_index = 0

        for sentence in sentences:
            sentence_tokens = self._estimate_tokens(sentence)
            
            if current_tokens + sentence_tokens > self.chunk_size and current_chunk:
                # Save current chunk
                chunk_text = " ".join(current_chunk)
                chunks.append(TextChunk(
                    content=chunk_text,
                    page=page,
                    chunk_index=chunk_index,
                ))
                chunk_index += 1
                
                # Keep overlap
                overlap_tokens = 0
                overlap_sentences = []
                for s in reversed(current_chunk):
                    s_tokens = self._estimate_tokens(s)
                    if overlap_tokens + s_tokens <= self.chunk_overlap:
                        overlap_sentences.insert(0, s)
                        overlap_tokens += s_tokens
                    else:
                        break
                
                current_chunk = overlap_sentences
                current_tokens = overlap_tokens
            
            current_chunk.append(sentence)
            current_tokens += sentence_tokens

        # Add remaining content
        if current_chunk:
            chunk_text = " ".join(current_chunk)
            chunks.append(TextChunk(
                content=chunk_text,
                page=page,
                chunk_index=chunk_index,
            ))

        return chunks

    def chunk_pages(self, pages: list[tuple[int, str]]) -> list[TextChunk]:
        """
        Chunk multiple pages of text.
        
        Args:
            pages: List of (page_number, text) tuples
            
        Returns:
            List of all chunks across pages
        """
        all_chunks = []
        for page_num, text in pages:
            chunks = self.chunk_text(text, page=page_num)
            all_chunks.extend(chunks)
        return all_chunks


# Singleton instance
_chunker_service: ChunkerService | None = None


def get_chunker_service() -> ChunkerService:
    """Get or create chunker service instance."""
    global _chunker_service
    if _chunker_service is None:
        _chunker_service = ChunkerService()
    return _chunker_service
