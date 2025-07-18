import pytest
from unittest.mock import patch, AsyncMock
from app.services import chat_service

@pytest.mark.asyncio
async def test_handle_chat_streams_chunks():
    # Mock the graph.astream_events to yield fake streaming events
    fake_events = [
        {"event": "on_chat_model_stream", "data": {"chunk": type("Chunk", (), {"content": "Hello"})()}},
        {"event": "on_chat_model_stream", "data": {"chunk": type("Chunk", (), {"content": " world!"})()}},
    ]
    async def fake_astream_events(*args, **kwargs):
        for event in fake_events:
            yield event

    with patch.object(chat_service, "graph", autospec=True) as mock_graph:
        mock_graph.astream_events = fake_astream_events
        # Run the async generator and collect results
        chunks = []
        async for chunk in chat_service.handle_chat("hi"):
            chunks.append(chunk)
        assert chunks == ["Hello", " world!"] 