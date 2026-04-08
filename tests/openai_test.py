from fastapi.testclient import TestClient
from openaiInt import app

test_client = TestClient(app)

def test_chat():
    response = test_client.post("/chat", params={"input": "Hello, how are you?"})
    assert response.status_code == 200
    assert "response" in response.json()