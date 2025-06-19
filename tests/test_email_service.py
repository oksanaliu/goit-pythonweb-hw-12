import pytest
from unittest.mock import AsyncMock, patch
from app.services.email import send_verification_email, send_reset_email

@pytest.mark.asyncio
@patch("app.services.email.FastMail")
async def test_send_verification_email(mock_fastmail):
    mock_send = AsyncMock()
    mock_fastmail.return_value.send_message = mock_send

    await send_verification_email("test@example.com", "fake-token")

    mock_send.assert_awaited_once()

@pytest.mark.asyncio
@patch("app.services.email.FastMail")
async def test_send_reset_email(mock_fastmail):
    mock_send = AsyncMock()
    mock_fastmail.return_value.send_message = mock_send

    await send_reset_email("test@example.com", "fake-reset-token")

    mock_send.assert_awaited_once()