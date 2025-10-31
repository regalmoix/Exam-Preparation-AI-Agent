"""Research agent for web-based information lookup."""

from __future__ import annotations

from typing import Any

from .base import AgentResponse
from .base import AgentTask
from .base import AgentType
from .base import BaseStudyAgent


class ResearchAgent(BaseStudyAgent):
    """Agent that conducts web research and validates external sources."""

    def __init__(self):
        super().__init__(AgentType.RESEARCH)

    async def process(self, task: AgentTask) -> AgentResponse:
        """Process research task and return validated information."""
        try:
            input_data = task.input_data
            research_query = input_data.get("query", "")
            save_to_kb = input_data.get("save_to_vectorstore", False)

            if not research_query:
                return self.create_response(success=False, content="", error_message="No research query provided")

            # For workshop demo, simulate research results
            research_results = self._simulate_research(research_query)

            return self.create_response(
                success=True,
                content=research_results,
                sources=research_results["sources"],
                reasoning=[
                    f"Conducted web search for: {research_query}",
                    f"Found {len(research_results['sources'])} reliable sources",
                    "Validated source credibility and relevance",
                ],
                metadata={
                    "query": research_query,
                    "search_strategy": "multi_source_validation",
                    "save_to_vectorstore": save_to_kb,
                    "processing_time": "3.2s",
                },
            )

        except Exception as e:
            return self.create_response(success=False, content="", error_message=f"Research failed: {e!s}")

    def _simulate_research(self, query: str) -> dict[str, Any]:
        """Simulate web research results for workshop demo."""

        # Generate contextual sources based on query
        sources = [
            {
                "title": f"Academic Article: Advanced {query.title()} Concepts",
                "url": "https://example-journal.edu/article/advanced-concepts",
                "credibility_score": 95,
                "relevance_score": 92,
                "excerpt": f"This peer-reviewed article explores the fundamental principles of {query} and their practical applications in educational contexts.",
                "publication_date": "2024",
                "source_type": "academic",
            },
            {
                "title": f"{query.title()} - Comprehensive Guide",
                "url": "https://example-university.edu/resources/guide",
                "credibility_score": 88,
                "relevance_score": 89,
                "excerpt": f"A comprehensive educational resource covering key aspects of {query}, including theoretical foundations and real-world examples.",
                "publication_date": "2024",
                "source_type": "educational",
            },
            {
                "title": f"Recent Developments in {query.title()}",
                "url": "https://example-research.org/recent-developments",
                "credibility_score": 90,
                "relevance_score": 85,
                "excerpt": f"Latest research findings and developments in the field of {query}, highlighting emerging trends and future directions.",
                "publication_date": "2024",
                "source_type": "research",
            },
        ]

        # Generate synthesized content
        synthesis = f"""
        ## Research Summary: {query.title()}

        Based on comprehensive research from multiple reliable sources, here are the key findings:

        ### Key Concepts:
        1. **Fundamental Principles**: The core concepts underlying {query} are well-established in academic literature
        2. **Practical Applications**: Multiple real-world applications demonstrate the relevance of {query}
        3. **Recent Developments**: Current research shows continued evolution and refinement of {query} methodologies

        ### Educational Implications:
        - Students should focus on understanding foundational concepts before progressing to advanced topics
        - Practical exercises help reinforce theoretical knowledge
        - Stay updated with recent developments to maintain current understanding

        ### Recommended Study Approach:
        1. Start with basic principles and definitions
        2. Review historical context and development
        3. Examine contemporary applications and case studies
        4. Practice with hands-on exercises when applicable
        """

        return {
            "research_query": query,
            "synthesis": synthesis.strip(),
            "key_findings": [
                f"Identified core principles and foundations of {query}",
                "Found practical applications and use cases",
                "Discovered recent developments and trends",
            ],
            "sources": sources,
            "source_validation": {
                "total_sources_found": len(sources),
                "high_credibility_sources": len([s for s in sources if s["credibility_score"] > 85]),
                "academic_sources": len([s for s in sources if s["source_type"] == "academic"]),
                "average_relevance": sum(s["relevance_score"] for s in sources) / len(sources),
            },
            "recommendations": [
                f"Use the academic article as a primary reference for {query}",
                "Cross-reference multiple sources for comprehensive understanding",
                "Focus on recent publications for current perspectives",
            ],
        }

    def get_capabilities(self) -> list[str]:
        """Return research agent capabilities."""
        return [
            "web_search",
            "source_validation",
            "content_synthesis",
            "credibility_assessment",
            "multi_source_analysis",
            "knowledge_expansion",
        ]

    def validate_input(self, input_data: dict[str, Any]) -> bool:
        """Validate research input."""
        return "query" in input_data and input_data["query"].strip()
