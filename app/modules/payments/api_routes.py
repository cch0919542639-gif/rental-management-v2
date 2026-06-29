from datetime import date
from decimal import Decimal

from flask import Blueprint, jsonify, request, url_for
from flask_login import login_required

from app.repositories import PaymentRepository
from app.services import PaymentService

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


def _parse_optional_date(value):
    if not value:
        return None
    return date.fromisoformat(value)


@payments_api_bp.get("/")
@login_required
def payment_list_api():
    limit = request.args.get("limit", default=50, type=int) or 50
    limit = max(1, min(limit, 200))
    records = PaymentRepository.list_filtered(
        record_status=(request.args.get("record_status") or "").strip() or None,
        contract_id=request.args.get("contract_id", type=int) or None,
        monthly_bill_id=request.args.get("monthly_bill_id", type=int) or None,
        limit=limit,
    )
    return jsonify(
        {
            "items": [_serialize_payment(item) for item in records],
            "count": len(records),
            "limit": limit,
        }
    )


@payments_api_bp.get("/<int:payment_id>")
@login_required
def payment_detail(payment_id: int):
    record = PaymentRepository.get_or_404(payment_id)
    return jsonify(_serialize_payment(record))


@payments_api_bp.post("/")
@login_required
def payment_create_api():
    payload = request.get_json(silent=True) or {}
    record = PaymentService.create_payment_record(
        contract_id=payload.get("contract_id"),
        monthly_bill_id=payload.get("monthly_bill_id"),
        amount=payload.get("amount"),
        bank_name=payload.get("bank_name"),
        account_number=payload.get("account_number"),
        account_holder=payload.get("account_holder"),
        transaction_date=_parse_optional_date(payload.get("transaction_date")),
        payer_name=payload.get("payer_name"),
        transaction_id=payload.get("transaction_id"),
        status_text=payload.get("status_text"),
        raw_ocr_text=payload.get("raw_ocr_text"),
        raw_llm_response=payload.get("raw_llm_response"),
        image_path=payload.get("image_path"),
        ocr_engine=payload.get("ocr_engine"),
        notes=payload.get("notes"),
    )
    return jsonify(_serialize_payment(record)), 201
