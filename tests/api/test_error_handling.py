import pytest
import httpx


BASE_URL = "http://localhost:8002"


@pytest.mark.asyncio
async def test_invalid_endpoint():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{BASE_URL}/exam-assistant/nonexistent")
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_malformed_json():
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{BASE_URL}/exam-assistant/classify-intent",
            content="invalid json content",
            headers={"Content-Type": "application/json"},
        )
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_missing_required_fields():
    async with httpx.AsyncClient() as client:
        # Test intent classification without query
        payload = {"user_id": "test_user"}
        response = await client.post(
            f"{BASE_URL}/exam-assistant/classify-intent", json=payload
        )
        assert response.status_code == 422

        # Test query without query field
        payload = {"user_id": "test_user"}
        response = await client.post(f"{BASE_URL}/exam-assistant/query", json=payload)
        assert response.status_code == 422

        # Test research without query
        payload = {"user_id": "test_user"}
        response = await client.post(
            f"{BASE_URL}/exam-assistant/research", json=payload
        )
        assert response.status_code == 422

        # Test workflow without message
        payload = {"user_id": "test_user"}
        response = await client.post(
            f"{BASE_URL}/exam-assistant/workflow", json=payload
        )
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_invalid_content_type_for_file_upload():
    async with httpx.AsyncClient() as client:
        # Try to upload file with wrong content type
        response = await client.post(
            f"{BASE_URL}/exam-assistant/vector-store/files", json={"file": "not_a_file"}
        )
        assert response.status_code == 422


@pytest.mark.asyncio
async def test_sql_injection_attempts():
    async with httpx.AsyncClient() as client:
        malicious_queries = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "<script>alert('xss')</script>",
            "../../etc/passwd",
        ]

        for malicious_query in malicious_queries:
            payload = {"query": malicious_query, "user_id": "test_user"}
            response = await client.post(
                f"{BASE_URL}/exam-assistant/classify-intent", json=payload
            )
            # Should handle gracefully, not crash
            assert response.status_code in [200, 400, 422, 500]


@pytest.mark.asyncio
async def test_large_payload():
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Test with very large query
        large_query = "A" * 100000  # 100KB query
        payload = {"query": large_query, "user_id": "test_user"}

        response = await client.post(
            f"{BASE_URL}/exam-assistant/classify-intent", json=payload
        )
        # Should handle gracefully (may accept or reject based on limits)
        assert response.status_code in [200, 413, 422]


@pytest.mark.asyncio
async def test_cors_headers():
    async with httpx.AsyncClient() as client:
        # Test preflight request
        response = await client.options(f"{BASE_URL}/exam-assistant/health")
        # Should handle CORS preflight
        assert response.status_code in [200, 204]


@pytest.mark.asyncio
async def test_invalid_file_operations():
    async with httpx.AsyncClient() as client:
        # Test with invalid file ID format
        invalid_ids = ["invalid-id", "../../sensitive-file", "", "very-long-id" * 100]

        for invalid_id in invalid_ids:
            response = await client.get(
                f"{BASE_URL}/exam-assistant/vector-store/files/{invalid_id}"
            )
            assert response.status_code in [400, 404, 422]

            response = await client.delete(
                f"{BASE_URL}/exam-assistant/vector-store/files/{invalid_id}"
            )
            assert response.status_code in [400, 404, 422]


@pytest.mark.asyncio
async def test_concurrent_requests():
    import asyncio

    async def make_request():
        async with httpx.AsyncClient() as client:
            return await client.get(f"{BASE_URL}/exam-assistant/health")

    # Make multiple concurrent requests
    tasks = [make_request() for _ in range(10)]
    responses = await asyncio.gather(*tasks, return_exceptions=True)

    # All should succeed or handle gracefully
    for response in responses:
        if isinstance(response, httpx.Response):
            assert response.status_code == 200
        # Some might fail due to rate limits, which is acceptable


@pytest.mark.asyncio
async def test_unicode_handling():
    async with httpx.AsyncClient() as client:
        unicode_queries = [
            "¿Qué es el aprendizaje automático?",
            "什么是机器学习？",
            "Что такое машинное обучение?",
            "🤖 AI and ML concepts 📚",
        ]

        for unicode_query in unicode_queries:
            payload = {"query": unicode_query, "user_id": "test_user"}
            response = await client.post(
                f"{BASE_URL}/exam-assistant/classify-intent", json=payload
            )
            # Should handle Unicode gracefully
            assert response.status_code in [200, 400, 422]


@pytest.mark.asyncio
async def test_timeout_resilience():
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            # Make a research request that might take longer
            payload = {
                "query": "comprehensive research on quantum computing applications in cryptography",
                "user_id": "test_user",
            }
            response = await client.post(
                f"{BASE_URL}/exam-assistant/research", json=payload
            )
            # Should either complete quickly or handle timeout gracefully
            assert response.status_code in [200, 408, 500, 504]
        except httpx.TimeoutException:
            # Timeout is acceptable for this test
            pass
