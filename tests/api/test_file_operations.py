import pytest
import httpx
import io


BASE_URL = "http://localhost:8002"


@pytest.mark.asyncio
async def test_file_upload_success():
    async with httpx.AsyncClient(timeout=30.0) as client:
        test_content = b"This is a test file for upload testing.\n\nIt contains sample content for vector store processing."

        files = {"file": ("test_upload.txt", io.BytesIO(test_content), "text/plain")}
        response = await client.post(
            f"{BASE_URL}/exam-assistant/vector-store/files", files=files
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "File uploaded successfully"
        assert "file" in data
        assert data["file"]["filename"] == "test_upload.txt"
        assert "id" in data["file"]
        assert data["file"]["bytes"] == len(test_content)

        # Store file_id for cleanup in other tests
        return data["file"]["id"]


@pytest.mark.asyncio
async def test_file_upload_invalid_type():
    async with httpx.AsyncClient(timeout=10.0) as client:
        test_content = b"FAKE_EXECUTABLE_FOR_TESTING"

        files = {
            "file": ("test.exe", io.BytesIO(test_content), "application/octet-stream")
        }
        response = await client.post(
            f"{BASE_URL}/exam-assistant/vector-store/files", files=files
        )

        assert response.status_code == 400
        data = response.json()
        assert "not supported" in data["detail"]


@pytest.mark.asyncio
async def test_file_upload_missing_file():
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.post(f"{BASE_URL}/exam-assistant/vector-store/files")

        assert response.status_code == 422  # Validation error


@pytest.mark.asyncio
async def test_get_file_info():
    async with httpx.AsyncClient(timeout=30.0) as client:
        # First upload a file
        test_content = b"Test file for info retrieval."
        files = {"file": ("info_test.txt", io.BytesIO(test_content), "text/plain")}
        upload_response = await client.post(
            f"{BASE_URL}/exam-assistant/vector-store/files", files=files
        )
        assert upload_response.status_code == 200

        file_id = upload_response.json()["file"]["id"]

        # Get file info
        info_response = await client.get(
            f"{BASE_URL}/exam-assistant/vector-store/files/{file_id}"
        )
        assert info_response.status_code == 200

        data = info_response.json()
        assert data["id"] == file_id
        assert data["filename"] == "info_test.txt"
        assert "bytes" in data
        assert "status" in data


@pytest.mark.asyncio
async def test_get_nonexistent_file_info():
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{BASE_URL}/exam-assistant/vector-store/files/file-nonexistent123"
        )
        assert response.status_code == 404


@pytest.mark.asyncio
async def test_delete_file():
    async with httpx.AsyncClient(timeout=30.0) as client:
        # First upload a file
        test_content = b"Test file for deletion."
        files = {"file": ("delete_test.txt", io.BytesIO(test_content), "text/plain")}
        upload_response = await client.post(
            f"{BASE_URL}/exam-assistant/vector-store/files", files=files
        )
        assert upload_response.status_code == 200

        file_id = upload_response.json()["file"]["id"]

        # Delete the file
        delete_response = await client.delete(
            f"{BASE_URL}/exam-assistant/vector-store/files/{file_id}"
        )
        assert delete_response.status_code == 200

        data = delete_response.json()
        assert data["message"] == "File deleted successfully"

        # Verify file is deleted by trying to get info
        info_response = await client.get(
            f"{BASE_URL}/exam-assistant/vector-store/files/{file_id}"
        )
        assert info_response.status_code == 404


@pytest.mark.asyncio
async def test_delete_nonexistent_file():
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{BASE_URL}/exam-assistant/vector-store/files/file-nonexistent123"
        )
        assert response.status_code == 404
