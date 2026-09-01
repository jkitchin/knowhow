import importlib.util
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

SCRIPT = Path(__file__).parents[1] / "scripts" / "atlas_image.py"
SPEC = importlib.util.spec_from_file_location("atlas_image", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def response(payload, status_code=200, error=None):
    result = Mock()
    result.status_code = status_code
    result.json.return_value = payload
    result.raise_for_status.side_effect = error
    return result


@patch.object(MODULE.time, "sleep")
@patch.object(MODULE.requests, "get")
@patch.object(MODULE.requests, "post")
def test_generate_posts_once_and_returns_completed_prediction(post, get, sleep):
    post.return_value = response(
        {"code": "200", "data": {"id": "pred-1", "status": "created"}}
    )
    get.side_effect = [
        response({"code": 200, "data": {"id": "pred-1", "status": "processing"}}),
        response(
            {
                "code": 200,
                "data": {
                    "id": "pred-1",
                    "status": "completed",
                    "outputs": ["https://example.com/frame.png"],
                },
            }
        ),
    ]

    client = MODULE.AtlasImageClient(api_key="test-key", poll_interval=0)
    result = client.generate("a consistent story frame")

    assert result["status"] == "completed"
    assert result["outputs"] == ["https://example.com/frame.png"]
    post.assert_called_once_with(
        "https://api.atlascloud.ai/api/v1/model/generateImage",
        headers={
            "Authorization": "Bearer test-key",
            "Content-Type": "application/json",
        },
        json={
            "model": "google/nano-banana-2/text-to-image",
            "prompt": "a consistent story frame",
            "aspect_ratio": "1:1",
            "resolution": "1k",
            "output_format": "png",
        },
        timeout=30,
    )
    assert get.call_count == 2
    sleep.assert_called_once_with(0)


@patch.object(MODULE.time, "sleep")
@patch.object(MODULE.requests, "get")
@patch.object(MODULE.requests, "post")
def test_prediction_get_retries_are_bounded(post, get, sleep):
    post.return_value = response(
        {"code": 200, "data": {"id": "pred-2", "status": "created"}}
    )
    get.return_value = response({}, status_code=503, error=RuntimeError("503"))

    client = MODULE.AtlasImageClient(
        api_key="test-key",
        poll_interval=0,
        max_polls=10,
        max_get_retries=3,
    )
    with pytest.raises(RuntimeError, match="503"):
        client.generate("a frame")

    post.assert_called_once()
    assert get.call_count == 4


def test_requires_key_and_rejects_unverified_model(monkeypatch):
    monkeypatch.delenv("ATLASCLOUD_API_KEY", raising=False)
    with pytest.raises(ValueError, match="ATLASCLOUD_API_KEY"):
        MODULE.AtlasImageClient()

    client = MODULE.AtlasImageClient(api_key="test-key")
    with pytest.raises(ValueError, match="Unsupported model"):
        client.submit("a frame", model="unverified/model")
