from __future__ import annotations

from pydantic import BaseModel
from pydantic import Field


class EntitySchema(BaseModel):
    """Schema for extracted entities."""

    action: str


class IntentClassificationSchema(BaseModel):
    """Schema for intent classification responses."""

    intent: str
    confidence: float
    entities: EntitySchema
    reasoning: str


class CitationSchema(BaseModel):
    """Schema for citations."""

    text: str
    page: int
    section: str


class SummarySchema(BaseModel):
    """Schema for document summaries."""

    main_topic: str
    key_concepts: list[str]
    study_notes: list[str]
    citations: list[CitationSchema]
    summary: str


class SourceSchema(BaseModel):
    """Schema for research sources."""

    title: str
    url: str
    credibility_score: int
    relevance_score: int
    excerpt: str
    publication_date: str
    source_type: str


class ResearchResultSchema(BaseModel):
    """Schema for research results."""

    research_query: str
    synthesis: str
    key_findings: list[str]
    sources: list[SourceSchema]
    recommendations: list[str]


class FlashcardSchema(BaseModel):
    """Schema for individual flashcards."""

    id: str
    type: str  # basic, cloze, multiple_choice
    front: str = Field(default="")
    back: str = Field(default="")
    text: str = Field(default="")  # For cloze cards
    question: str = Field(default="")  # For multiple choice
    choices: list[str] = Field(default_factory=list)
    correct_answer: int = Field(default=0)
    tags: list[str]
    difficulty: str
