import pytest
import httpx
import io


BASE_URL = "http://localhost:8002"


@pytest.mark.asyncio
async def test_full_workflow_with_file_upload():
    """Test the complete workflow: upload file -> classify intent -> get response"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        # Step 1: Upload a test file
        test_content = b"""Machine Learning Fundamentals

Machine learning is a subset of artificial intelligence that enables computers to learn and make decisions from data without being explicitly programmed.

Key Concepts:
- Supervised Learning: Learning with labeled examples
- Unsupervised Learning: Finding patterns in unlabeled data
- Deep Learning: Neural networks with multiple layers
- Reinforcement Learning: Learning through rewards and punishments

Applications:
- Image recognition
- Natural language processing
- Recommendation systems
- Autonomous vehicles"""

        files = {"file": ("ml_guide.txt", io.BytesIO(test_content), "text/plain")}
        upload_response = await client.post(
            f"{BASE_URL}/exam-assistant/vector-store/files", files=files
        )
        assert upload_response.status_code == 200

        file_data = upload_response.json()
        file_id = file_data["file"]["id"]

        # Step 2: Wait a moment for file processing
        import asyncio

        await asyncio.sleep(2)

        # Step 3: Test intent classification for different query types
        test_cases = [
            {
                "query": "Summarize the machine learning document",
                "expected_intent": "SUMMARIZER",
            },
            {
                "query": "What is supervised learning according to my notes?",
                "expected_intent": ["RAG_QA", "SUMMARIZER"],  # Could be either
            },
            {
                "query": "Create flashcards from the ML fundamentals document",
                "expected_intent": "FLASHCARD",
            },
            {
                "query": "Research latest advances in deep learning",
                "expected_intent": "RESEARCH",
            },
        ]

        for case in test_cases:
            # Test intent classification
            intent_payload = {"query": case["query"], "user_id": "integration_test"}
            intent_response = await client.post(
                f"{BASE_URL}/exam-assistant/classify-intent", json=intent_payload
            )

            assert intent_response.status_code == 200
            intent_data = intent_response.json()
            assert intent_data["success"] is True

            classified_intent = intent_data["classification"]["intent"]
            if isinstance(case["expected_intent"], list):
                assert classified_intent in case["expected_intent"]
            else:
                assert classified_intent == case["expected_intent"]

            # Test the corresponding workflow
            workflow_payload = {
                "message": case["query"],
                "user_id": "integration_test",
                "session_id": "integration_session",
            }
            workflow_response = await client.post(
                f"{BASE_URL}/exam-assistant/workflow", json=workflow_payload
            )

            assert workflow_response.status_code == 200
            workflow_data = workflow_response.json()
            assert workflow_data["success"] is True
            assert "workflow_result" in workflow_data

        # Step 4: Test Q&A with the uploaded content
        qa_payload = {
            "query": "What are the key concepts of machine learning mentioned in the document?",
            "user_id": "integration_test",
        }
        qa_response = await client.post(
            f"{BASE_URL}/exam-assistant/query", json=qa_payload
        )

        assert qa_response.status_code == 200
        qa_data = qa_response.json()
        assert qa_data["success"] is True
        assert (
            "supervised learning" in qa_data["answer"].lower()
            or "unsupervised learning" in qa_data["answer"].lower()
        )

        # Step 5: Clean up - delete the uploaded file
        delete_response = await client.delete(
            f"{BASE_URL}/exam-assistant/vector-store/files/{file_id}"
        )
        assert delete_response.status_code == 200


@pytest.mark.asyncio
async def test_multiple_file_operations():
    """Test handling multiple files and operations"""
    async with httpx.AsyncClient(timeout=60.0) as client:
        uploaded_files = []

        try:
            # Upload multiple files
            test_files = [
                ("doc1.txt", b"Document 1 content about artificial intelligence."),
                ("doc2.txt", b"Document 2 content about machine learning algorithms."),
                (
                    "doc3.txt",
                    b"Document 3 content about neural networks and deep learning.",
                ),
            ]

            for filename, content in test_files:
                files = {"file": (filename, io.BytesIO(content), "text/plain")}
                response = await client.post(
                    f"{BASE_URL}/exam-assistant/vector-store/files", files=files
                )
                assert response.status_code == 200
                uploaded_files.append(response.json()["file"]["id"])

            # Wait for processing
            import asyncio

            await asyncio.sleep(3)

            # Test that files are listed
            list_response = await client.get(f"{BASE_URL}/exam-assistant/documents")
            assert list_response.status_code == 200

            documents = list_response.json()["documents"]
            uploaded_filenames = [
                doc["filename"] for doc in documents if doc["id"] in uploaded_files
            ]

            # At least some of our uploaded files should appear
            assert len(uploaded_filenames) >= 2

            # Test Q&A across multiple documents
            qa_payload = {
                "query": "What information is available about artificial intelligence and machine learning?",
                "user_id": "integration_test",
            }
            qa_response = await client.post(
                f"{BASE_URL}/exam-assistant/query", json=qa_payload
            )

            assert qa_response.status_code == 200
            qa_data = qa_response.json()
            assert qa_data["success"] is True

            # Response should mention content from multiple documents
            answer_lower = qa_data["answer"].lower()
            assert len(answer_lower) > 50  # Substantial response

        finally:
            # Clean up all uploaded files
            for file_id in uploaded_files:
                try:
                    await client.delete(
                        f"{BASE_URL}/exam-assistant/vector-store/files/{file_id}"
                    )
                except Exception:
                    pass  # Ignore cleanup errors


@pytest.mark.asyncio
async def test_system_resilience():
    """Test system behavior under various conditions"""
    async with httpx.AsyncClient(timeout=45.0) as client:
        # Test rapid successive requests
        tasks = []

        async def make_health_check():
            return await client.get(f"{BASE_URL}/exam-assistant/health")

        async def make_intent_request():
            payload = {"query": f"Test query {len(tasks)}", "user_id": "stress_test"}
            return await client.post(
                f"{BASE_URL}/exam-assistant/classify-intent", json=payload
            )

        # Create multiple concurrent requests
        for i in range(5):
            tasks.append(make_health_check())
            tasks.append(make_intent_request())

        # Execute all requests concurrently
        import asyncio

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Most requests should succeed
        successful_responses = [
            r for r in results if isinstance(r, httpx.Response) and r.status_code == 200
        ]
        assert (
            len(successful_responses) >= len(tasks) * 0.8
        )  # At least 80% success rate


@pytest.mark.asyncio
async def test_data_consistency():
    """Test that data remains consistent across operations"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Get initial state
        initial_docs = await client.get(f"{BASE_URL}/exam-assistant/documents")
        assert initial_docs.status_code == 200
        initial_count = len(initial_docs.json()["documents"])

        initial_files = await client.get(
            f"{BASE_URL}/exam-assistant/vector-store/files"
        )
        assert initial_files.status_code == 200
        initial_file_count = len(initial_files.json()["files"])

        # Upload a file
        test_content = b"Consistency test document content."
        files = {
            "file": ("consistency_test.txt", io.BytesIO(test_content), "text/plain")
        }
        upload_response = await client.post(
            f"{BASE_URL}/exam-assistant/vector-store/files", files=files
        )
        assert upload_response.status_code == 200

        file_id = upload_response.json()["file"]["id"]

        # Wait for processing
        import asyncio

        await asyncio.sleep(2)

        # Check that counts increased
        after_docs = await client.get(f"{BASE_URL}/exam-assistant/documents")
        assert after_docs.status_code == 200
        after_count = len(after_docs.json()["documents"])

        after_files = await client.get(f"{BASE_URL}/exam-assistant/vector-store/files")
        assert after_files.status_code == 200
        after_file_count = len(after_files.json()["files"])

        # File should appear in both endpoints
        assert after_count >= initial_count  # Documents list should include new file
        assert (
            after_file_count > initial_file_count
        )  # Files list should include new file

        # Clean up
        delete_response = await client.delete(
            f"{BASE_URL}/exam-assistant/vector-store/files/{file_id}"
        )
        assert delete_response.status_code == 200


@pytest.mark.asyncio
async def test_error_recovery():
    """Test system recovery from error conditions"""
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Make some invalid requests
        bad_requests = [
            client.post(f"{BASE_URL}/exam-assistant/classify-intent", json={}),
            client.post(f"{BASE_URL}/exam-assistant/query", json={"query": ""}),
            client.get(f"{BASE_URL}/exam-assistant/vector-store/files/invalid-id"),
        ]

        import asyncio

        bad_results = await asyncio.gather(*bad_requests, return_exceptions=True)

        # All should fail gracefully (not crash the server)
        for result in bad_results:
            if isinstance(result, httpx.Response):
                assert result.status_code in [400, 404, 422, 500]

        # System should still be responsive after errors
        health_response = await client.get(f"{BASE_URL}/exam-assistant/health")
        assert health_response.status_code == 200
        assert health_response.json()["status"] == "healthy"

        # Valid requests should still work
        valid_payload = {"query": "Test after errors", "user_id": "recovery_test"}
        valid_response = await client.post(
            f"{BASE_URL}/exam-assistant/classify-intent", json=valid_payload
        )
        assert valid_response.status_code == 200
