import pytest
from fastapi.testclient import TestClient
from fastapi import WebSocket
from unittest.mock import patch, AsyncMock
from app.main import app

client = TestClient(app)

@pytest.mark.asyncio
async def test_websocket_chat_stream(monkeypatch):
    # Mock handle_chat to yield fake streaming chunks
    async def fake_handle_chat(message):
        yield "Hello"
        yield " world!"

    with patch("app.services.chat_service.handle_chat", new=fake_handle_chat):
        with client.websocket_connect("/ws/chat") as websocket:
            websocket.send_text("hi")
            # Receive the streaming chunks
            chunk1 = websocket.receive_text()
            chunk2 = websocket.receive_text()
            assert chunk1 == "Hello"
            assert chunk2 == " world!" 