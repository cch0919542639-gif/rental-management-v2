from __future__ import annotations

from datetime import date
from decimal import Decimal, InvalidOperation

from flask import Blueprint, jsonify, request, url_for
from flask_login import login_required

from app.core.errors import DomainValidationError
from app.core.security import admin_required
from app.repositories import PaymentRepository
from app.services import PaymentOCRService, PaymentService

payments_api_bp = Blueprint("payments_api", __name__, url_prefix="/api/payment-records")


def _decimal_to_str(value):
    if value is None:
        return None
    return str(Decimal(str(value)).quantize(Decimal("0.01")))


def _date_to_iso(value):
    if value is None:
        return None
    return value.isoformat()


def _serialize_payment(record):
    return {
        "id": record.id,
        "contract_id": record.contract_id,
        "monthly_bill_id": record.monthly_bill_id,
        "amount": _decimal_to_str(record.amount),
        "bank_name": record.bank_name,
        "account_number": record.account_number,
        "account_holder": record.account_holder,
        "transaction_date": _date_to_iso(record.transaction_date),
        "payer_name": record.payer_name,
        "transaction_id": record.transaction_id,
        "status_text": record.status_text,
        "record_status": record.record_status,
        "raw_ocr_text": record.raw_ocr_text,
        "raw_llm_response": record.raw_llm_response,
        "image_path": record.image_path,
        "ocr_engine": record.ocr_engine,
        "verified_by_id": record.verified_by_id,
        "verified_at": record.verified_at.isoformat() if record.verified_at else None,
        "notes": record.notes,
        "links": {
            "self": url_for("payments_api.payment_detail", payment_id=record.id),
        },
    }


def _parse_optional_int(raw, field_name: str):
    if raw in (None, ""):
        return None
    try:
        return int(raw)
    except (TypeError, ValueError) as exc:
        raise DomainValidationError("請求資料格式錯誤", details={field_name: [f"{field_name} 必須是整數"]}) from exc


def _parse_optional_date(raw, field_name: str):
    if raw in (None, ""):
        return None
    try:
        return date.fromisoformat(str(raw))
    except ValueError as exc:
        raise DomainValidationError("請求資料格式錯誤", details={field_name: [f"{field_name} 必須是 YYYY-MM-DD"]}) from exc


def _normalize_create_payload(data: dict):
    details = {}
    raw_amount = data.get("amount")
    if raw_amount in (None, ""):
        details["amount"] = ["amount 為必填"]
    else:
        try:
            Decimal(str(raw_amount))
        except (InvalidOperation, ValueError):
            details["amount"] = ["amount 必須是數字"]

    if details:
        raise DomainValidationError("請求資料格式錯誤", details=details)

    return {
        "contract_id": _parse_optional_int(data.get("contract_id"), "contract_id"),
        "monthly_bill_id": _parse_optional_int(data.get("monthly_bill_id"), "monthly_bill_id"),
        "amount": data.get("amount"),
        "bank_name": data.get("bank_name"),
        "account_number": data.get("account_number"),
        "account_holder": data.get("account_holder"),
        "transaction_date": _parse_optional_date(data.get("transaction_date"), "transaction_date"),
        "payer_name": data.get("payer_name"),
        "transaction_id": data.get("transaction_id"),
        "status_text": data.get("status_text"),
        "raw_ocr_text": data.get("raw_ocr_text"),
        "raw_llm_response": data.get("raw_llm_response"),
        "image_path": data.get("image_path"),
        "ocr_engine": data.get("ocr_engine"),
        "notes": data.get("notes"),
    }


@payments_api_bp.get("/")
@login_required
def payment_list_api():
    limit = request.args.get("limit", default=50, type=int) or 50
    limit = max(1, min(limit, 200))
    offset = request.args.get("offset", default=0, type=int) or 0
    records = PaymentRepository.list_filtered(
        record_status=(request.args.get("record_status") or "").strip() or None,
        contract_id=request.args.get("contract_id", type=int) or None,
        monthly_bill_id=request.args.get("monthly_bill_id", type=int) or None,
        transaction_id=(request.args.get("transaction_id") or "").strip() or None,
        payer_name=(request.args.get("payer_name") or "").strip() or None,
        date_from=(request.args.get("date_from") or "").strip() or None,
        date_to=(request.args.get("date_to") or "").strip() or None,
        limit=limit,
        offset=offset,
    )
    return jsonify(
        {
            "items": [_serialize_payment(item) for item in records],
            "count": len(records),
            "limit": limit,
            "offset": offset,
        }
    )


@payments_api_bp.get("/<int:payment_id>")
@login_required
def payment_detail(payment_id: int):
    record = PaymentRepository.get_or_404(payment_id)
    return jsonify(_serialize_payment(record))


@payments_api_bp.post("/")
@login_required
@admin_required
def payment_create_api():
    payload = _normalize_create_payload(request.get_json(silent=True) or {})
    record = PaymentService.create_payment_record(**payload)
    return jsonify(_serialize_payment(record)), 201


@payments_api_bp.post("/<int:payment_id>/analyze")
@login_required
@admin_required
def payment_analyze_api(payment_id: int):
    record = PaymentRepository.get_or_404(payment_id)
    result = PaymentOCRService.analyze_record(record)
    return jsonify({"payment_record": _serialize_payment(record), "analysis": result.to_dict()})
