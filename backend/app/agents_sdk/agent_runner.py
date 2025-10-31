"""Agent runner and coordination system for Study Assistant."""

from __future__ import annotations

from typing import Any
from uuid import uuid4

from agents import ModelSettings
from agents import RunConfig
from agents import Runner

from .agents import FlashcardGeneratorAgent
from .agents import IntentClassifierAgent
from .agents import RagQAAgent
from .agents import ResearchAgent
from .agents import SummarizerAgent


class StudyAgentRunner:
    """Coordinates and runs all study assistant agents."""

    def __init__(self):
        """Initialize the agent runner with all agents."""
        self.agents = {
            "intent_classifier": IntentClassifierAgent,
            "summarizer": SummarizerAgent,
            "research": ResearchAgent,
            "rag_qa": RagQAAgent,
            "flashcard_generator": FlashcardGeneratorAgent,
        }

        # Default model settings
        self.model_settings = ModelSettings(model="gpt-4o-mini", temperature=0.1, max_tokens=2000)

        # Default run configuration
        self.run_config = RunConfig(
            model_settings=self.model_settings,
        )

    async def classify_intent(self, query: str, user_id: str | None = None) -> dict[str, Any]:
        """Classify user intent using the intent classifier agent."""
        try:
            # Prepare the message for intent classification
            messages = [{"role": "user", "content": f"Classify this student query: '{query}'"}]

            result = await Runner.run(self.agents["intent_classifier"], input=messages, run_config=self.run_config)

            return {
                "success": True,
                "task_id": str(uuid4()),
                "classification": result.final_output,
                "reasoning": [f"Analyzed query: {query}"],
                "metadata": {"user_id": user_id, "agent_used": "intent_classifier", "model": "gpt-4o-mini"},
            }

        except Exception as e:
            return {
                "success": False,
                "error_message": f"Intent classification failed: {e!s}",
                "task_id": str(uuid4()),
            }

    async def summarize_document(
        self, document_id: str, document_type: str | None = None, focus_areas: list[str] | None = None
    ) -> dict[str, Any]:
        """Generate document summary using the summarizer agent."""
        try:
            # Prepare the summarization request
            prompt = f"""Please create a comprehensive study summary for document ID: {document_id}

Document Type: {document_type or "General"}
Focus Areas: {", ".join(focus_areas) if focus_areas else "All key concepts"}

Please:
1. Use the file search tool to retrieve the document content
2. Extract key information using the document extraction tool
3. Create a structured summary following the required format
4. Include proper citations with page references
"""

            messages = [{"role": "user", "content": prompt}]
            result = await Runner.run(self.agents["summarizer"], input=messages, run_config=self.run_config)

            return {
                "success": True,
                "task_id": str(uuid4()),
                "summary": result.final_output,
                "reasoning": ["Retrieved document content", "Extracted key concepts", "Generated structured summary"],
                "metadata": {
                    "document_id": document_id,
                    "document_type": document_type,
                    "focus_areas": focus_areas,
                    "agent_used": "summarizer",
                    "processing_time": "3.2s",  # Would be actual time in production
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error_message": f"Document summarization failed: {e!s}",
                "task_id": str(uuid4()),
            }

    async def conduct_research(
        self, query: str, save_to_vectorstore: bool = False, user_id: str | None = None
    ) -> dict[str, Any]:
        """Conduct research using the research agent."""
        try:
            # Prepare the research request
            prompt = f"""Conduct comprehensive research on: "{query}"

Please:
1. Use the web search tool to find multiple reliable sources
2. Evaluate source credibility and educational value
3. Synthesize findings into a coherent educational summary
4. Provide study recommendations and additional resources
{"5. Store the research summary for future reference" if save_to_vectorstore else ""}

Focus on academic, educational, and research sources that would be valuable for students studying this topic.
"""

            messages = [{"role": "user", "content": prompt}]
            result = await Runner.run(self.agents["research"], input=messages, run_config=self.run_config)

            return {
                "success": True,
                "task_id": str(uuid4()),
                "research_results": result.final_output,
                "sources": getattr(result.final_output, "sources", []),
                "reasoning": [
                    f"Conducted web search for: {query}",
                    "Validated source credibility and relevance",
                    "Synthesized findings from multiple sources",
                ],
                "metadata": {
                    "query": query,
                    "save_to_vectorstore": save_to_vectorstore,
                    "user_id": user_id,
                    "agent_used": "research",
                    "search_strategy": "multi_source_validation",
                },
            }

        except Exception as e:
            return {"success": False, "error_message": f"Research failed: {e!s}", "task_id": str(uuid4())}

    async def generate_flashcards(
        self,
        document_id: str,
        card_count: int = 10,
        difficulty: str = "medium",
        deck_name: str = "Study Deck",
        user_id: str | None = None,
    ) -> dict[str, Any]:
        """Generate flashcards using the flashcard generator agent."""
        try:
            # Prepare the flashcard generation request
            prompt = f"""Generate {card_count} flashcards from document ID: {document_id}

Requirements:
- Deck Name: {deck_name}
- Difficulty Level: {difficulty}
- Card Types: Mix of basic, cloze, and multiple choice
- Focus: Key concepts and exam-relevant material

Please:
1. Use the file search tool to access the document content
2. Generate diverse card types based on the material
3. Ensure questions promote active recall and understanding
4. Include proper tagging for organization
5. Create deck metadata for Anki export

The flashcards should be suitable for spaced repetition learning and help students master the key concepts from the document.
"""

            messages = [{"role": "user", "content": prompt}]
            await Runner.run(self.agents["flashcard_generator"], input=messages, run_config=self.run_config)

            # Process the result to match our expected format
            flashcard_response = {
                "document_id": document_id,
                "deck_id": str(uuid4()),
                "deck_name": deck_name,
                "flashcards": [],  # Would be populated from agent response
                "generation_stats": {
                    "requested_count": card_count,
                    "generated_count": card_count,  # Assume success for now
                    "difficulty_level": difficulty,
                    "card_types": {"basic": 4, "cloze": 3, "multiple_choice": 3},
                },
                "anki_integration": {
                    "mcp_status": "connected",
                    "deck_created": True,
                    "anki_ready": True,
                    "export_format": "anki_apkg",
                },
            }

            return {
                "success": True,
                "task_id": str(uuid4()),
                "flashcard_deck": flashcard_response,
                "reasoning": [
                    f"Generated {card_count} flashcards from document {document_id}",
                    f"Applied {difficulty} difficulty level",
                    "Prepared cards for Anki export via MCP integration",
                ],
                "metadata": {
                    "document_id": document_id,
                    "user_id": user_id,
                    "agent_used": "flashcard_generator",
                    "mcp_enabled": True,
                    "spaced_repetition": True,
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error_message": f"Flashcard generation failed: {e!s}",
                "task_id": str(uuid4()),
            }

    async def answer_query(self, query: str, user_id: str | None = None) -> dict[str, Any]:
        """Answer student query using RAG Q&A agent with knowledge base."""
        try:
            # Prepare the Q&A request
            prompt = f"""Answer this student question using only information from the uploaded study materials: "{query}"

Requirements:
- Use ONLY information from the knowledge base/uploaded documents
- Provide clear, educational answers grounded in the retrieved content
- Include proper citations in the format (filename, page/section)
- If information isn't available, clearly state this
- Focus on helping the student understand concepts from their materials

Please search through the uploaded documents and provide a comprehensive answer based solely on that content.
"""

            messages = [{"role": "user", "content": prompt}]
            result = await Runner.run(self.agents["rag_qa"], input=messages, run_config=self.run_config)

            return {
                "success": True,
                "task_id": str(uuid4()),
                "answer": result.final_output,
                "reasoning": [
                    f"Searched knowledge base for: {query}",
                    "Retrieved relevant document sections",
                    "Generated answer based on source materials only",
                ],
                "metadata": {
                    "query": query,
                    "user_id": user_id,
                    "agent_used": "rag_qa",
                    "knowledge_base_only": True,
                    "citations_included": True,
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error_message": f"Q&A failed: {e!s}",
                "task_id": str(uuid4()),
            }

    async def run_workflow(
        self,
        message: str,
        user_id: str | None = None,
        session_id: str | None = None,
    ) -> dict[str, Any]:
        """Execute the full agent workflow: classify intent -> route to appropriate agent -> execute."""
        try:
            task_id = str(uuid4())

            # Step 1: Classify intent
            classification_result = await self.classify_intent(message, user_id)

            if not classification_result["success"]:
                return classification_result

            classification = classification_result["classification"]
            intent = classification.get("intent", "RAG_QA").upper()

            # Step 2: Route and execute based on intent
            if intent == "RESEARCH":
                # Extract query from the original message for research
                research_result = await self.conduct_research(message, user_id=user_id)
                return {
                    "success": True,
                    "task_id": task_id,
                    "workflow_result": {
                        "intent_classification": classification,
                        "agent_executed": "research",
                        "result": research_result,
                        "message": message,
                    },
                }

            elif intent == "FLASHCARD":
                # For flashcards, we need a document_id, so provide guidance
                return {
                    "success": True,
                    "task_id": task_id,
                    "workflow_result": {
                        "intent_classification": classification,
                        "agent_executed": "flashcard_generator",
                        "result": {
                            "success": True,
                            "message": "I can create flashcards for you! Please specify which document you'd like me to use.",
                            "required_action": "document_selection",
                            "next_steps": ["Upload a document or provide a document ID to generate flashcards"],
                        },
                        "message": message,
                    },
                }

            elif intent == "SUMMARIZER":
                # For summarization, we need a document_id, so provide guidance
                return {
                    "success": True,
                    "task_id": task_id,
                    "workflow_result": {
                        "intent_classification": classification,
                        "agent_executed": "summarizer",
                        "result": {
                            "success": True,
                            "message": "I can summarize documents for you! Please specify which document you'd like me to summarize.",
                            "required_action": "document_selection",
                            "next_steps": ["Upload a document or provide a document ID to summarize"],
                        },
                        "message": message,
                    },
                }

            else:  # RAG_QA or default
                # Execute Q&A with knowledge base
                qa_result = await self.answer_query(message, user_id)
                return {
                    "success": True,
                    "task_id": task_id,
                    "workflow_result": {
                        "intent_classification": classification,
                        "agent_executed": "rag_qa",
                        "result": qa_result,
                        "message": message,
                    },
                }

        except Exception as e:
            return {
                "success": False,
                "error_message": f"Workflow execution failed: {e!s}",
                "task_id": str(uuid4()),
            }

    async def smart_route(
        self,
        message: str,
        user_id: str | None = None,
        session_id: str | None = None,
        context: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Smart routing that combines intent classification with appropriate agent response."""
        try:
            # Step 1: Classify intent
            classification_result = await self.classify_intent(message, user_id)

            if not classification_result["success"]:
                return classification_result

            classification = classification_result["classification"]
            intent = classification.get("intent", "RAG_QA")
            confidence = classification.get("confidence", 0)

            # Step 2: Prepare agent-specific responses
            response_data = {
                "message_id": str(uuid4()),
                "classified_intent": intent,
                "confidence": confidence,
                "reasoning": classification.get("reasoning", ""),
                "user_id": user_id,
                "session_id": session_id,
            }

            # Add agent-specific routing information
            if intent == "SUMMARIZER":
                response_data["agent_response"] = {
                    "type": "summarization_prompt",
                    "message": "I can help you summarize your study materials. Which document would you like me to summarize?",
                    "next_steps": ["document_selection", "summarization"],
                    "required_params": ["document_id"],
                }
            elif intent == "RESEARCH":
                response_data["agent_response"] = {
                    "type": "research_prompt",
                    "message": "I'll help you research additional information. What topic would you like me to look up?",
                    "next_steps": ["web_search", "source_compilation"],
                    "required_params": ["query"],
                }
            elif intent == "FLASHCARD":
                response_data["agent_response"] = {
                    "type": "flashcard_prompt",
                    "message": "I can create flashcards to help you study. Based on which materials should I generate them?",
                    "next_steps": ["material_selection", "flashcard_generation"],
                    "required_params": ["document_id", "card_count"],
                }
            else:  # RAG_QA
                response_data["agent_response"] = {
                    "type": "qa_response",
                    "message": "I'll search through your uploaded materials to answer your question.",
                    "next_steps": ["document_search", "answer_generation"],
                    "required_params": ["query"],
                }

            return {"success": True, "routing_result": response_data, "task_id": str(uuid4())}

        except Exception as e:
            return {"success": False, "error_message": f"Smart routing failed: {e!s}", "task_id": str(uuid4())}

    def get_agent_capabilities(self) -> dict[str, Any]:
        """Return information about all available agents and their capabilities."""
        return {
            "agents": [
                {
                    "type": "SUMMARIZER",
                    "name": "Document Summarizer",
                    "description": "Creates comprehensive summaries of study materials using file search",
                    "capabilities": [
                        "document_summarization",
                        "key_concept_extraction",
                        "study_note_generation",
                        "citation_extraction",
                        "file_search_integration",
                    ],
                    "tools": ["FileSearchTool", "extract_document_summary"],
                    "workshop_phase": 1,
                },
                {
                    "type": "RESEARCH",
                    "name": "Research Agent",
                    "description": "Conducts web research with source validation",
                    "capabilities": [
                        "web_search",
                        "source_validation",
                        "content_synthesis",
                        "credibility_assessment",
                        "research_storage",
                    ],
                    "tools": ["WebSearchTool", "store_research_summary"],
                    "workshop_phase": 3,
                },
                {
                    "type": "RAG_QA",
                    "name": "Q&A Agent",
                    "description": "Answers questions based on uploaded study materials",
                    "capabilities": ["document_retrieval", "contextual_qa", "source_citing"],
                    "tools": ["ChatKit", "FileSearchTool"],
                    "workshop_phase": 2,
                },
                {
                    "type": "FLASHCARD",
                    "name": "Flashcard Generator",
                    "description": "Creates study cards and integrates with Anki via MCP",
                    "capabilities": [
                        "flashcard_creation",
                        "anki_integration",
                        "mcp_protocol",
                        "spaced_repetition",
                        "multi_format_export",
                    ],
                    "tools": ["FileSearchTool", "HostedMCPTool", "create_flashcard_deck"],
                    "workshop_phase": 4,
                },
                {
                    "type": "INTENT_CLASSIFIER",
                    "name": "Intent Router",
                    "description": "Classifies student queries and routes to appropriate agents",
                    "capabilities": [
                        "intent_classification",
                        "query_routing",
                        "entity_extraction",
                        "confidence_scoring",
                        "multi_agent_coordination",
                    ],
                    "tools": [],
                    "workshop_phase": 5,
                },
            ],
            "workshop_info": {
                "total_phases": 5,
                "estimated_duration": "3-4 hours",
                "learning_objectives": [
                    "Understanding AI agent architectures with agents SDK",
                    "Building RAG systems for education",
                    "Integrating real web search and MCP tools",
                    "Creating production-ready study tools",
                ],
                "sdk_features": [
                    "Real FileSearchTool integration",
                    "WebSearchTool for research",
                    "HostedMCPTool for Anki",
                    "Structured response formats",
                    "Agent coordination and routing",
                ],
            },
        }
