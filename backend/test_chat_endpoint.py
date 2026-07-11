from fastapi.testclient import TestClient
from app.main import app


def test_chat_uses_knowledge_base_response(monkeypatch):
    def fake_ask_ai(question: str) -> str:
        return "FINANCIAL FRAUD MANAGEMENT POLICY"

    class FakeGraph:
        def invoke(self, state, config=None):
            return {"messages": [type("Msg", (), {"content": "generic fallback"})()]}

    monkeypatch.setattr("app.main.ask_ai", fake_ask_ai)
    monkeypatch.setattr("app.main.graph", FakeGraph())

    client = TestClient(app)
    response = client.post("/chat", json={"user_query": "What is the title of the policy document?"})

    assert response.status_code == 200
    assert response.json()["response"] == "FINANCIAL FRAUD MANAGEMENT POLICY"


def test_chat_returns_title_for_policy_name_question(monkeypatch):
    def fake_ask_ai(question: str) -> str:
        return "I don't know. You just asked me to answer a question."

    class FakeGraph:
        def invoke(self, state, config=None):
            return {"messages": [type("Msg", (), {"content": "generic fallback"})()]}

    class FakeKnowledgeTool:
        def invoke(self, question: str) -> str:
            return "FINANCIAL FRAUD MANAGEMENT POLICY\n1. PURPOSE This policy establishes a zero-tolerance approach."

    monkeypatch.setattr("app.main.ask_ai", fake_ask_ai)
    monkeypatch.setattr("app.main.graph", FakeGraph())
    monkeypatch.setattr("app.tools.order_tool.search_knowledge_base", FakeKnowledgeTool())

    client = TestClient(app)
    response = client.post("/chat", json={"user_query": "what is my policy name?"})

    assert response.status_code == 200
    assert response.json()["response"] == "FINANCIAL FRAUD MANAGEMENT POLICY"
