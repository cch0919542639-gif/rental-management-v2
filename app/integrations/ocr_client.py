from __future__ import annotations

import base64
import json
import mimetypes
import time
import uuid
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol
from urllib.error import HTTPError, URLError
from urllib.parse import quote
from urllib.request import Request, urlopen

from flask import current_app


@dataclass
class OCRResult:
    provider: str
    status: str
    text: str | None = None
    message: str | None = None


class OCRClientProtocol(Protocol):
    def extract_text(self, image_path: str) -> OCRResult: ...


class NoopOCRClient:
    def extract_text(self, image_path: str) -> OCRResult:
        return OCRResult(
            provider="noop",
            status="not_configured",
            message="OCR provider is not configured.",
        )


class TextFileOCRClient:
    def extract_text(self, image_path: str) -> OCRResult:
        path = Path(image_path)
        if not path.exists():
            return OCRResult(provider="text_file", status="missing_file", message="Image file not found.")
        text = path.read_text(encoding="utf-8")
        return OCRResult(provider="text_file", status="ok", text=text)


class GoogleVisionOCRClient:
    """Cloud Vision adapter using the VM service account; no key file is stored."""

    _METADATA_URL = "http://metadata.google.internal/computeMetadata/v1/instance/service-accounts/default/token"
    _VISION_URL = "https://vision.googleapis.com/v1"
    _STORAGE_URL = "https://storage.googleapis.com/storage/v1"

    @staticmethod
    def _request_json(url: str, *, token: str, method: str = "GET", payload=None):
        body = None if payload is None else json.dumps(payload).encode("utf-8")
        request = Request(
            url,
            data=body,
            method=method,
            headers={
                "Authorization": f"Bearer {token}",
                "Content-Type": "application/json; charset=utf-8",
            },
        )
        with urlopen(request, timeout=30) as response:  # nosec B310: URLs are fixed Google endpoints.
            return json.loads(response.read().decode("utf-8"))

    @classmethod
    def _access_token(cls) -> str:
        request = Request(cls._METADATA_URL, headers={"Metadata-Flavor": "Google"})
        with urlopen(request, timeout=5) as response:  # nosec B310: fixed metadata endpoint.
            return json.loads(response.read().decode("utf-8"))["access_token"]

    def _extract_image(self, path: Path, token: str) -> OCRResult:
        payload = {
            "requests": [
                {
                    "image": {"content": base64.b64encode(path.read_bytes()).decode("ascii")},
                    "features": [{"type": "DOCUMENT_TEXT_DETECTION"}],
                }
            ]
        }
        response = self._request_json(f"{self._VISION_URL}/images:annotate", token=token, method="POST", payload=payload)
        item = (response.get("responses") or [{}])[0]
        if item.get("error"):
            return OCRResult(provider="google_vision", status="failed", message=item["error"].get("message", "Vision OCR failed."))
        text = (item.get("fullTextAnnotation") or {}).get("text")
        return OCRResult(provider="google_vision", status="ok", text=text or "")

    def _extract_pdf(self, path: Path, token: str) -> OCRResult:
        bucket = (current_app.config.get("OCR_GCS_BUCKET") or "").strip()
        if not bucket:
            return OCRResult(provider="google_vision", status="not_configured", message="PDF OCR storage is not configured.")

        request_id = uuid.uuid4().hex
        source_name = f"utility-ocr/input/{request_id}/{path.name}"
        output_prefix = f"gs://{bucket}/utility-ocr/output/{request_id}/"
        upload_url = f"https://storage.googleapis.com/upload/storage/v1/b/{quote(bucket, safe='')}/o?uploadType=media&name={quote(source_name, safe='')}"
        upload = Request(
            upload_url,
            data=path.read_bytes(),
            method="POST",
            headers={"Authorization": f"Bearer {token}", "Content-Type": "application/pdf"},
        )
        with urlopen(upload, timeout=60):  # nosec B310: fixed Google Storage endpoint.
            pass

        response = self._request_json(
            f"{self._VISION_URL}/files:asyncBatchAnnotate",
            token=token,
            method="POST",
            payload={
                "requests": [{
                    "inputConfig": {"gcsSource": {"uri": f"gs://{bucket}/{source_name}"}, "mimeType": "application/pdf"},
                    "features": [{"type": "DOCUMENT_TEXT_DETECTION"}],
                    "outputConfig": {"gcsDestination": {"uri": output_prefix}, "batchSize": 1},
                }]
            },
        )
        operation = response.get("name")
        if not operation:
            return OCRResult(provider="google_vision", status="failed", message="Vision did not return an operation ID.")
        for _ in range(18):
            time.sleep(1)
            result = self._request_json(f"{self._VISION_URL}/{operation}", token=token)
            if result.get("done"):
                if result.get("error"):
                    return OCRResult(provider="google_vision", status="failed", message=result["error"].get("message", "Vision OCR failed."))
                listing = self._request_json(
                    f"{self._STORAGE_URL}/b/{quote(bucket, safe='')}/o?prefix={quote('utility-ocr/output/' + request_id + '/', safe='')}",
                    token=token,
                )
                texts = []
                for item in listing.get("items", []):
                    object_name = item["name"]
                    download = Request(
                        f"{self._STORAGE_URL}/b/{quote(bucket, safe='')}/o/{quote(object_name, safe='')}?alt=media",
                        headers={"Authorization": f"Bearer {token}"},
                    )
                    with urlopen(download, timeout=30) as output:  # nosec B310: fixed Google Storage endpoint.
                        payload = json.loads(output.read().decode("utf-8"))
                    for page in payload.get("responses", []):
                        text = (page.get("fullTextAnnotation") or {}).get("text")
                        if text:
                            texts.append(text)
                return OCRResult(provider="google_vision", status="ok", text="\n\n".join(texts))
        return OCRResult(provider="google_vision", status="processing", message="PDF 已送交辨識，請稍後重新上傳或改以照片辨識。")

    def extract_text(self, image_path: str) -> OCRResult:
        path = Path(image_path)
        if not path.exists():
            return OCRResult(provider="google_vision", status="missing_file", message="Uploaded file not found.")
        try:
            token = self._access_token()
            if path.suffix.lower() == ".pdf":
                return self._extract_pdf(path, token)
            mime_type, _ = mimetypes.guess_type(path.name)
            if not mime_type or not mime_type.startswith("image/"):
                return OCRResult(provider="google_vision", status="unsupported_file", message="Only PDF and image files are supported.")
            return self._extract_image(path, token)
        except (HTTPError, URLError, KeyError, OSError, ValueError) as exc:
            return OCRResult(provider="google_vision", status="failed", message=f"OCR request failed: {exc}")


def create_ocr_client() -> OCRClientProtocol:
    provider = (current_app.config.get("OCR_PROVIDER") or "").strip().lower()
    if provider == "text_file":
        return TextFileOCRClient()
    if provider == "google_vision":
        return GoogleVisionOCRClient()
    return NoopOCRClient()
