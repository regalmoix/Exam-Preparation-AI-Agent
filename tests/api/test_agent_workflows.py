import pytest
import httpx


BASE_URL = "http://localhost:8002"


@pytest.mark.asyncio
async def test_intent_classification_summarizer():
    async with httpx.AsyncClient(timeout=30.0) as client:
        payload = {
            "query": "Can you summarize the document I uploaded?",
            "user_id": "test_user",
        }
        response = await client.post(
            f"{BASE_URL}/exam-assistant/classify-intent", json=payload
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "classification" in data
        assert data["classification"]["intent"] == "SUMMARIZER"
        assert data["classification"]["confidence"] > 80
        assert "task_id" in data


@pytest.mark.asyncio
async def test_intent_classification_research():
    async with httpx.AsyncClient(timeout=30.0) as client:
        payload = {
            "query": "Research information about machine learning algorithms",
            "user_id": "test_user",
        }
        response = await client.post(
            f"{BASE_URL}/exam-assistant/classify-intent", json=payload
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["classification"]["intent"] == "RESEARCH"
        assert data["classification"]["confidence"] > 70


@pytest.mark.asyncio
async def test_intent_classification_flashcard():
    async with httpx.AsyncClient(timeout=30.0) as client:
        payload = {"query": "Create flashcards for this topic", "user_id": "test_user"}
        response = await client.post(
            f"{BASE_URL}/exam-assistant/classify-intent", json=payload
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["classification"]["intent"] == "FLASHCARD"


@pytest.mark.asyncio
async def test_intent_classification_qa():
    async with httpx.AsyncClient(timeout=30.0) as client:
        payload = {
            "query": "What does the document say about neural networks?",
            "user_id": "test_user",
        }
        response = await client.post(
            f"{BASE_URL}/exam-assistant/classify-intent", json=payload
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        # Should default to RAG_QA for specific questions about documents
        assert data["classification"]["intent"] in ["RAG_QA", "SUMMARIZER"]


@pytest.mark.asyncio
async def test_intent_classification_invalid_request():
    async with httpx.AsyncClient() as client:
        payload = {}  # Missing required fields
        response = await client.post(
            f"{BASE_URL}/exam-assistant/classify-intent", json=payload
        )
        assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_qa_query():
    async with httpx.AsyncClient(timeout=30.0) as client:
        payload = {"query": "What is machine learning?", "user_id": "test_user"}
        response = await client.post(f"{BASE_URL}/exam-assistant/query", json=payload)

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "answer" in data
        assert len(data["answer"]) > 20  # Should provide a substantial response
        assert "reasoning" in data
        assert "metadata" in data
        assert data["metadata"]["knowledge_base_only"] is True


@pytest.mark.asyncio
async def test_research_query():
    async with httpx.AsyncClient(timeout=60.0) as client:  # Longer timeout for research
        payload = {
            "query": "artificial intelligence trends 2024",
            "user_id": "test_user",
            "save_to_vectorstore": False,
        }
        response = await client.post(
            f"{BASE_URL}/exam-assistant/research", json=payload
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "research_results" in data
        assert "reasoning" in data
        assert "metadata" in data
        assert data["metadata"]["agent_used"] == "research"


@pytest.mark.asyncio
async def test_workflow_execution_research():
    async with httpx.AsyncClient(timeout=60.0) as client:
        payload = {
            "message": "Research the latest developments in quantum computing",
            "user_id": "test_user",
            "session_id": "test_session",
        }
        response = await client.post(
            f"{BASE_URL}/exam-assistant/workflow", json=payload
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "workflow_result" in data
        assert data["workflow_result"]["agent_executed"] == "research"
        assert "intent_classification" in data["workflow_result"]


@pytest.mark.asyncio
async def test_workflow_execution_qa():
    async with httpx.AsyncClient(timeout=30.0) as client:
        payload = {
            "message": "What information do you have about deep learning?",
            "user_id": "test_user",
            "session_id": "test_session",
        }
        response = await client.post(
            f"{BASE_URL}/exam-assistant/workflow", json=payload
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert "workflow_result" in data
        assert data["workflow_result"]["agent_executed"] == "rag_qa"


@pytest.mark.asyncio
async def test_workflow_execution_summarizer_guidance():
    async with httpx.AsyncClient(timeout=30.0) as client:
        payload = {"message": "Summarize my documents", "user_id": "test_user"}
        response = await client.post(
            f"{BASE_URL}/exam-assistant/workflow", json=payload
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["workflow_result"]["agent_executed"] == "summarizer"
        # Should provide guidance since no document_id specified
        assert (
            "document_selection" in data["workflow_result"]["result"]["required_action"]
        )


@pytest.mark.asyncio
async def test_workflow_execution_flashcard_guidance():
    async with httpx.AsyncClient(timeout=30.0) as client:
        payload = {"message": "Create flashcards for me", "user_id": "test_user"}
        response = await client.post(
            f"{BASE_URL}/exam-assistant/workflow", json=payload
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
        assert data["workflow_result"]["agent_executed"] == "flashcard_generator"
        # Should provide guidance since no document_id specified
        assert (
            "document_selection" in data["workflow_result"]["result"]["required_action"]
        )


@pytest.mark.asyncio
async def test_empty_query_handling():
    async with httpx.AsyncClient() as client:
        payload = {"query": "", "user_id": "test_user"}
        response = await client.post(
            f"{BASE_URL}/exam-assistant/classify-intent", json=payload
        )

        # Should handle gracefully (either validation error or classification response)
        assert response.status_code in [200, 422]


@pytest.mark.asyncio
async def test_long_query_handling():
    async with httpx.AsyncClient(timeout=30.0) as client:
        long_query = (
            "This is a very long query that tests how the system handles extensive input. "
            * 50
        )
        payload = {"query": long_query, "user_id": "test_user"}
        response = await client.post(
            f"{BASE_URL}/exam-assistant/classify-intent", json=payload
        )

        assert response.status_code == 200
        data = response.json()
        assert data["success"] is True
