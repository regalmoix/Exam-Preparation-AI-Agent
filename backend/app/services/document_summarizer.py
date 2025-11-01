"""Document summarization service for generating intelligent descriptions."""

from __future__ import annotations

from pathlib import Path

from openai import AsyncOpenAI

from .config import config


class DocumentSummarizer:
    """Service for generating intelligent summaries and descriptions of uploaded documents."""

    def __init__(self):
        """Initialize the document summarizer."""
        self.client = AsyncOpenAI(api_key=config.openai_api_key)

    async def generate_description(self, file_content: bytes, filename: str) -> str:
        """Generate a concise 1-2 line description of the document content."""
        try:
            # Try to decode the content as text
            try:
                text_content = file_content.decode("utf-8")
            except UnicodeDecodeError:
                # For non-text files, use filename-based description
                return self._generate_fallback_description(filename)

            # Limit content size for API efficiency
            max_content_size = 4000  # Conservative limit for API calls
            if len(text_content) > max_content_size:
                text_content = text_content[:max_content_size] + "..."

            # Generate description using OpenAI
            response = await self.client.chat.completions.create(
                model=config.openai_model,
                messages=[
                    {
                        "role": "system",
                        "content": """You are a document analyzer. Create a concise, informative 1-2 line description of the document content that would help students understand what this study material contains.

Focus on:
- Main topic or subject area
- Type of content (notes, textbook, slides, research paper, etc.)
- Key concepts or themes

Keep it under 100 characters and make it useful for study organization.""",
                    },
                    {
                        "role": "user",
                        "content": f"Analyze this document and provide a brief description:\n\nFilename: {filename}\n\nContent:\n{text_content}",
                    },
                ],
                max_tokens=150,
                temperature=0.3,  # Low temperature for consistent, factual descriptions
            )

            description = response.choices[0].message.content or ""

            # Clean and validate the description
            description = description.strip().strip('"').strip("'")
            if len(description) > 200:  # Ensure reasonable length
                description = description[:197] + "..."

            return description or self._generate_fallback_description(filename)

        except Exception as e:
            print(f"Error generating description for {filename}: {e}")
            return self._generate_fallback_description(filename)

    def _generate_fallback_description(self, filename: str) -> str:
        """Generate a fallback description based on filename and extension."""

        file_path = Path(filename)
        extension = file_path.suffix.lower()
        name_part = file_path.stem

        # Generate description based on file type
        type_descriptions = {
            ".pdf": "PDF document",
            ".txt": "Text document",
            ".md": "Markdown document",
            ".html": "Web document",
            ".docx": "Word document",
            ".json": "JSON data file",
        }

        type_desc = type_descriptions.get(extension, "Document")

        # Try to extract meaningful info from filename
        if any(keyword in name_part.lower() for keyword in ["notes", "note"]):
            return f"Study notes - {type_desc}"
        elif any(keyword in name_part.lower() for keyword in ["lecture", "slides"]):
            return f"Lecture material - {type_desc}"
        elif any(keyword in name_part.lower() for keyword in ["textbook", "book", "chapter"]):
            return f"Textbook content - {type_desc}"
        elif any(keyword in name_part.lower() for keyword in ["assignment", "homework", "hw"]):
            return f"Assignment material - {type_desc}"
        elif any(keyword in name_part.lower() for keyword in ["exam", "test", "quiz"]):
            return f"Exam preparation - {type_desc}"
        else:
            return f"{type_desc} for study reference"


# Global instance
document_summarizer = DocumentSummarizer()

__all__ = ["DocumentSummarizer", "document_summarizer"]
