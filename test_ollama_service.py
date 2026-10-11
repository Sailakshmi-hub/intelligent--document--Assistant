from unittest.mock import patch

import pytest

from src.ollama_service import OllamaServiceError, check_connection, generate_answer, is_model_available, list_available_models


class FakeResponse:
    def __init__(self, payload=None, status_code=200, ok=True):
        self._payload = payload or {}
        self.status_code = status_code
        self.ok = ok

    def json(self):
        return self._payload


def test_missing_model_detected():
    fake_payload = {"models": [{"name": "llama3.2:3b"}]}
    with patch("src.ollama_service.requests.get", return_value=FakeResponse(fake_payload)):
        assert is_model_available("llama3.2:3b") is True
        assert is_model_available("qwen2.5:3b") is False


def test_connection_failure_raises():
    with patch("src.ollama_service.requests.get", side_effect=RuntimeError("offline")):
        assert check_connection() is False

    with patch("src.ollama_service.requests.post", return_value=FakeResponse({"response": "mock answer"})):
        answer = generate_answer("llama3.2:3b", "What is the answer?", ["Context chunk"])
        assert "mock answer" in answer
