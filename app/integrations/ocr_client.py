from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

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


def create_ocr_client() -> OCRClientProtocol:
    provider = (current_app.config.get("OCR_PROVIDER") or "").strip().lower()
    if provider == "text_file":
        return TextFileOCRClient()
    return NoopOCRClient()
