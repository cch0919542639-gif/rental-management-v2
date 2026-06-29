"""
Integration boundary package.

Phase 2 rule:
  - interface / skeleton only
  - no external network call implementation
  - no API keys in source
"""

from app.integrations.ocr_client import OCRClientProtocol
from app.integrations.sheets_client import SheetsClientProtocol

__all__ = ["OCRClientProtocol", "SheetsClientProtocol"]
