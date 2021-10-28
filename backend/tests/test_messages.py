from fastapi.testclient import TestClient
from main import app
import pytest
from unittest.mock import AsyncMock


client = TestClient(app)


@pytest.fixture()
def mock_read(mocker):    
    async_mock = AsyncMock()
    mocker.patch("backend.endpoints.messages.DataStorage.read", side_effect=async_mock)
    return async_mock
    

@pytest.fixture()
def mock_update(mocker):
    async_mock_update = AsyncMock()
    mocker.patch("backend.endpoints.messages.DataStorage.update", side_effect=async_mock_update)
    return async_mock_update


@pytest.fixture()
def mock_centrifugo(mocker):
    async_mock_centrifugo = AsyncMock()
    mocker.patch("backend.endpoints.messages.centrifugo_client.publish", side_effect=async_mock_centrifugo)
    return async_mock_centrifugo


@pytest.mark.asyncio
async def test_update_message_successful(mock_read, mock_update, mock_centrifugo):
    read_data = {
        "_id": "2222",
        "sender_id": "1313",
        "message": "what's up",
        "room_id": "1111",
        "media": [],
        "read": True
    }
    update_response = {
        "status": 200,
        "message": "success"
    }
    centrifugo_response = {
        "status_code": 200
    }

    mock_read.return_value = read_data
    mock_update.return_value = update_response
    mock_centrifugo.return_value = centrifugo_response
    payload = {
        "message": "How are u doing mate?",
        "sender_id": "1313",
        "message_id": "2222",
        "room_id": "1111"
    }
    response = client.put(
        "/api/v1/org/1234/rooms/1111/messages/2222/update",
        json=payload
        )
    assert response.status_code == 200
    assert response.json() == {
            "status": "success",
            "sender_id": "1313",
            "room_id": "1111",
            "message_id": "2222",
            "message": "How are u doing mate?",
            "event": "message_update",
        }


@pytest.mark.asyncio
async def test_update_message_unsuccessful(mock_read):
    mock_read.return_value = None
    payload = {
        "message": "What's up",
        "sender_id": "1313455",
        "message_id": "22226767",
        "room_id": "11117687"
    }
    response = client.put(
        "/api/v1/org/1234/rooms/11117687/messages/22226767/update",
        json=payload
        )
    assert response.status_code == 404
    assert response.json() == {"detail": "Message not found"}