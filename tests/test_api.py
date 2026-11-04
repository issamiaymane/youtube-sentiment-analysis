import pytest

from src.api.schemas import MAX_BATCH_SIZE, MAX_COMMENT_LENGTH


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"
    assert response.json()["model_loaded"] is True


@pytest.mark.parametrize("size", [1, 10, 50, MAX_BATCH_SIZE])
def test_batch_sizes(client, size):
    response = client.post("/predict_batch", json={"comments": ["great video"] * size})
    assert response.status_code == 200
    body = response.json()
    assert len(body["predictions"]) == size
    assert body["statistics"]["total"] == size
    assert sum(body["statistics"]["counts"].values()) == size


def test_response_shape_and_order(client):
    comments = ["I love this video", "This is terrible", "What camera is this?"]
    body = client.post("/predict_batch", json={"comments": comments}).json()
    assert [p["text"] for p in body["predictions"]] == comments
    assert [p["sentiment"] for p in body["predictions"]] == ["positif", "negatif", "neutre"]
    assert body["processing_time_ms"] >= 0
    assert sum(body["statistics"]["percentages"].values()) == pytest.approx(100, abs=0.2)


@pytest.mark.parametrize("payload", [
    {"comments": []},
    {"comments": "pas une liste"},
    {"comments": [1, 2]},
    {"comments": [None]},
    {"wrong": ["a"]},
    {"comments": ["a"] * (MAX_BATCH_SIZE + 1)},
    {"comments": ["a" * (MAX_COMMENT_LENGTH + 1)]},
])
def test_invalid_payloads_are_rejected(client, payload):
    assert client.post("/predict_batch", json=payload).status_code == 422


def test_malformed_json(client):
    response = client.post(
        "/predict_batch", content="{oops", headers={"Content-Type": "application/json"}
    )
    assert response.status_code == 422


def test_unavailable_model_returns_503(client):
    predictor = client.app.state.predictor
    client.app.state.predictor = None
    try:
        assert client.get("/health").status_code == 503
        assert client.post("/predict_batch", json={"comments": ["a"]}).status_code == 503
    finally:
        client.app.state.predictor = predictor


def test_cors_allows_extension_only(client):
    headers = {"Access-Control-Request-Method": "POST"}
    allowed = client.options(
        "/predict_batch",
        headers={**headers, "Origin": "chrome-extension://abcdefghijklmnopabcdefghijklmnop"},
    )
    refused = client.options("/predict_batch", headers={**headers, "Origin": "https://evil.example"})
    assert "access-control-allow-origin" in allowed.headers
    assert "access-control-allow-origin" not in refused.headers
