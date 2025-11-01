import pytest
import httpx


BASE_URL = "http://localhost:8002"


@pytest.mark.asyncio
async def test_health_endpoint():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/exam-assistant/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_vector_store_info():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/exam-assistant/vector-store")
        assert response.status_code == 200
        data = response.json()
        assert "id" in data
        assert "name" in data
        assert "file_counts" in data
        assert "status" in data


@pytest.mark.asyncio
async def test_agent_capabilities():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/exam-assistant/agents/capabilities")
        assert response.status_code == 200
        data = response.json()
        assert "agents" in data
        assert len(data["agents"]) == 5

        agent_types = [agent["type"] for agent in data["agents"]]
        expected_types = [
            "SUMMARIZER",
            "RESEARCH",
            "RAG_QA",
            "FLASHCARD",
            "INTENT_CLASSIFIER",
        ]
        for expected_type in expected_types:
            assert expected_type in agent_types


@pytest.mark.asyncio
async def test_documents_list():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/exam-assistant/documents")
        assert response.status_code == 200
        data = response.json()
        assert "documents" in data
        assert isinstance(data["documents"], list)


@pytest.mark.asyncio
async def test_vector_store_files_list():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/exam-assistant/vector-store/files")
        assert response.status_code == 200
        data = response.json()
        assert "files" in data
        assert "has_more" in data
        assert isinstance(data["files"], list)
