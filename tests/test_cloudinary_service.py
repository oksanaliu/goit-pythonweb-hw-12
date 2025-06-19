import pytest
from unittest.mock import patch, MagicMock
from fastapi import UploadFile, HTTPException
from app.services.cloudinary_service import upload_avatar

class DummyUploadFile:
    def __init__(self, content_type, content):
        self.content_type = content_type
        self._content = content

    async def read(self):
        return self._content

@pytest.mark.asyncio
async def test_upload_avatar_success():
    dummy_file = DummyUploadFile("image/jpeg", b"dummy_image_data")
    
    with patch("app.services.cloudinary_service.cloudinary.uploader.upload") as mock_upload:
        mock_upload.return_value = {"secure_url": "https://fake.cloudinary.com/image.jpg"}
        result = await upload_avatar(dummy_file)
        assert result == "https://fake.cloudinary.com/image.jpg"

@pytest.mark.asyncio
async def test_upload_avatar_invalid_type():
    dummy_file = DummyUploadFile("text/plain", b"some_text")

    with pytest.raises(HTTPException) as exc_info:
        await upload_avatar(dummy_file)

    assert exc_info.value.status_code == 400
    assert "Only image files are allowed" in exc_info.value.detail

@pytest.mark.asyncio
async def test_upload_avatar_failure():
    dummy_file = DummyUploadFile("image/png", b"broken_image")

    with patch("app.services.cloudinary_service.cloudinary.uploader.upload") as mock_upload:
        mock_upload.side_effect = Exception("Upload failed")

        with pytest.raises(HTTPException) as exc_info:
            await upload_avatar(dummy_file)

        assert exc_info.value.status_code == 502
        assert "Cloudinary upload failed" in exc_info.value.detail