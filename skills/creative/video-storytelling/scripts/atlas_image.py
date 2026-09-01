#!/usr/bin/env python3
"""Generate a story frame with the optional Atlas Cloud image provider."""

import argparse
import json
import os
import sys
import time
from pathlib import Path

import requests

DEFAULT_BASE_URL = "https://api.atlascloud.ai/api/v1"
DEFAULT_MODEL = "google/nano-banana-2/text-to-image"
TERMINAL_SUCCESS = {"completed", "succeeded", "success"}
TERMINAL_FAILURE = {"failed", "canceled", "cancelled"}


class AtlasImageClient:
    """Small client for one-shot submission and bounded prediction polling."""

    def __init__(
        self,
        api_key=None,
        base_url=None,
        poll_interval=3,
        max_polls=100,
        max_get_retries=3,
    ):
        self.api_key = api_key or os.environ.get("ATLASCLOUD_API_KEY")
        self.base_url = (
            base_url or os.environ.get("ATLAS_MEDIA_API_BASE") or DEFAULT_BASE_URL
        ).rstrip("/")
        self.poll_interval = poll_interval
        self.max_polls = max_polls
        self.max_get_retries = max_get_retries
        if not self.api_key:
            raise ValueError("ATLASCLOUD_API_KEY is required")

    def _headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

    @staticmethod
    def _prediction(response):
        response.raise_for_status()
        body = response.json()
        code = body.get("code")
        if code is not None and str(code) not in {"0", "200"}:
            raise RuntimeError(body.get("message") or f"Atlas API error: {code}")
        prediction = body.get("data", body)
        if not isinstance(prediction, dict):
            raise RuntimeError("Atlas API returned an invalid prediction response")
        return prediction

    def submit(
        self,
        prompt,
        model=DEFAULT_MODEL,
        aspect_ratio="1:1",
        resolution="1k",
        output_format="png",
    ):
        """Submit exactly once. Callers must not retry this billable request."""
        if model != DEFAULT_MODEL:
            raise ValueError(f"Unsupported model: {model}")
        response = requests.post(
            f"{self.base_url}/model/generateImage",
            headers=self._headers(),
            json={
                "model": model,
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "resolution": resolution,
                "output_format": output_format,
            },
            timeout=30,
        )
        prediction = self._prediction(response)
        if not prediction.get("id"):
            raise RuntimeError("Atlas API response did not include a prediction id")
        return prediction

    def poll(self, prediction_id):
        """Poll with bounded retries for transient GET failures only."""
        transient_failures = 0
        for poll_number in range(self.max_polls):
            if poll_number:
                time.sleep(self.poll_interval)
            try:
                response = requests.get(
                    f"{self.base_url}/model/prediction/{prediction_id}",
                    headers=self._headers(),
                    timeout=30,
                )
                if response.status_code in {408, 429} or response.status_code >= 500:
                    transient_failures += 1
                    if transient_failures > self.max_get_retries:
                        response.raise_for_status()
                    continue
                prediction = self._prediction(response)
            except (requests.exceptions.ConnectionError, requests.exceptions.Timeout):
                transient_failures += 1
                if transient_failures > self.max_get_retries:
                    raise
                continue

            status = str(prediction.get("status", "")).lower()
            if status in TERMINAL_SUCCESS:
                return prediction
            if status in TERMINAL_FAILURE:
                raise RuntimeError(f"Atlas prediction {prediction_id} {status}")

        raise TimeoutError(f"Atlas prediction {prediction_id} did not finish in time")

    def generate(self, prompt, **kwargs):
        prediction = self.submit(prompt, **kwargs)
        if str(prediction.get("status", "")).lower() in TERMINAL_SUCCESS:
            return prediction
        return self.poll(prediction["id"])


def download_output(prediction, output_path):
    outputs = prediction.get("outputs") or []
    if not outputs:
        raise RuntimeError("Completed prediction did not include an output URL")
    response = requests.get(outputs[0], timeout=60)
    response.raise_for_status()
    Path(output_path).write_bytes(response.content)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("prompt", help="Story-frame prompt")
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument(
        "--aspect-ratio",
        default="1:1",
        choices=[
            "1:1",
            "3:2",
            "2:3",
            "3:4",
            "4:3",
            "4:5",
            "5:4",
            "9:16",
            "16:9",
            "21:9",
        ],
    )
    parser.add_argument("--resolution", default="1k", choices=["1k", "2k", "4k"])
    parser.add_argument("--format", default="png", choices=["default", "png", "jpeg"])
    parser.add_argument("--output", "-o", help="Download the first output URL")
    args = parser.parse_args()

    try:
        result = AtlasImageClient().generate(
            args.prompt,
            model=args.model,
            aspect_ratio=args.aspect_ratio,
            resolution=args.resolution,
            output_format=args.format,
        )
        if args.output:
            download_output(result, args.output)
        print(json.dumps(result, indent=2))
    except (requests.RequestException, RuntimeError, TimeoutError, ValueError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
