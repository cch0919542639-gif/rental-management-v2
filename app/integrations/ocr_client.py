from typing import Protocol


class OCRClientProtocol(Protocol):
    def analyze_receipt(self, image_path: str) -> dict:
        """Return normalized OCR result payload for a receipt image."""
