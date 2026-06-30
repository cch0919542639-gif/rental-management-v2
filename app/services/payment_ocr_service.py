from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import date
import json
import re

from app.core.db import db
from app.core.errors import DomainValidationError
from app.integrations import create_ocr_client
from app.models import PaymentRecord

ALLOWED_IMAGE_SUFFIXES = {".jpg", ".jpeg", ".png", ".webp", ".txt"}


@dataclass
class OCRAnalysisResult:
    source: str
    provider: str
    status: str
    raw_text_present: bool
    extracted_candidates: dict
    manual_review_required: bool
    auto_apply: bool
    message: str | None = None

    def to_dict(self):
        return asdict(self)


class PaymentOCRService:
    @staticmethod
    def _validate_image_path(image_path: str | None):
        if not image_path:
            raise DomainValidationError("缺少 OCR 輸入來源", details={"image_path": ["image_path 為必填或需先提供 raw_ocr_text"]})

        suffix = image_path.lower().rsplit(".", 1)
        ext = f".{suffix[-1]}" if len(suffix) > 1 else ""
        if ext not in ALLOWED_IMAGE_SUFFIXES:
            raise DomainValidationError("不支援的影像格式", details={"image_path": ["僅支援 .jpg, .jpeg, .png, .webp, .txt"]})

    @staticmethod
    def _extract_candidates(text: str) -> dict:
        compact = " ".join(text.split())
        amount_match = re.search(r"(\d{3,}(?:\.\d{1,2})?)", compact)
        date_match = re.search(r"(\d{4}[-/]\d{2}[-/]\d{2})", compact)
        transaction_match = re.search(r"(TXN[-A-Z0-9_]+)", compact, re.IGNORECASE)

        candidates = {
            "amount": amount_match.group(1) if amount_match else None,
            "transaction_date": None,
            "transaction_id": transaction_match.group(1) if transaction_match else None,
        }
        if date_match:
            candidates["transaction_date"] = date.fromisoformat(date_match.group(1).replace("/", "-")).isoformat()
        return candidates

    @staticmethod
    def analyze_record(record: PaymentRecord) -> OCRAnalysisResult:
        if record.raw_ocr_text:
            text = record.raw_ocr_text
            provider = record.ocr_engine or "stored_raw_text"
            source = "stored_raw_ocr_text"
            status = "ok"
            message = None
        else:
            PaymentOCRService._validate_image_path(record.image_path)
            client = create_ocr_client()
            ocr_result = client.extract_text(record.image_path)
            provider = ocr_result.provider
            source = "image_path"
            status = ocr_result.status
            message = ocr_result.message

            if ocr_result.status != "ok":
                return OCRAnalysisResult(
                    source=source,
                    provider=provider,
                    status=ocr_result.status,
                    raw_text_present=False,
                    extracted_candidates={},
                    manual_review_required=True,
                    auto_apply=False,
                    message=message,
                )

            text = ocr_result.text or ""
            record.raw_ocr_text = text
            record.ocr_engine = provider

        candidates = PaymentOCRService._extract_candidates(text)
        result = OCRAnalysisResult(
            source=source,
            provider=provider,
            status=status,
            raw_text_present=bool(text.strip()),
            extracted_candidates=candidates,
            manual_review_required=True,
            auto_apply=False,
            message=message,
        )
        record.raw_llm_response = json.dumps(result.to_dict(), ensure_ascii=False)
        db.session.commit()
        return result
