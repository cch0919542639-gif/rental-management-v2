from datetime import UTC, datetime
from decimal import Decimal

from app.core.db import db
from app.models.move_out_settlement import MoveOutSettlement, MoveOutSettlementAllocation


class MoveOutSettlementService:
    DRAFT_FIELDS = {"final_monthly_bill_id", "move_out_date", *MoveOutSettlement.CHARGE_FIELDS, "other_desc", "evidence_type", "evidence_reference", "notes"}

    @staticmethod
    def _money(value):
        return Decimal(str(value or 0))

    @classmethod
    def _validate_payload(cls, payload):
        for field in MoveOutSettlement.CHARGE_FIELDS:
            if cls._money(payload.get(field)) < 0:
                raise ValueError(f"{field} cannot be negative")
        if cls._money(payload.get("other_charge")) > 0 and not (payload.get("other_desc") or "").strip():
            raise ValueError("其他費用必須填寫說明")

    @staticmethod
    def _assert_draft(settlement):
        if settlement.status != "draft":
            raise ValueError("只有草稿結清單可以編輯或刪除")

    @classmethod
    def create(cls, *, contract, **payload):
        cls._validate_payload(payload)
        if contract.move_out_settlement:
            raise ValueError("同一合約只能建立一張退租結清單")
        deposit = cls._money(contract.deposit)
        settlement = MoveOutSettlement(
            contract_id=contract.id,
            deposit_held=deposit,
            refund_amount=deposit,
            status="draft",
            **payload,
        )
        db.session.add(settlement)
        db.session.commit()
        return settlement

    @classmethod
    def update(cls, settlement, **payload):
        cls._assert_draft(settlement)
        cls._validate_payload(payload)
        for field, value in payload.items():
            if field in cls.DRAFT_FIELDS:
                setattr(settlement, field, value)
        db.session.commit()
        return settlement

    @classmethod
    def settle(cls, settlement, *, allocations: dict[str, object], confirmed_by=None):
        cls._assert_draft(settlement)
        normalized = {field: cls._money(allocations.get(field)) for field in MoveOutSettlement.CHARGE_FIELDS}
        if any(amount < 0 for amount in normalized.values()):
            raise ValueError("分攤金額不可為負數")
        charges = {field: cls._money(getattr(settlement, field)) for field in MoveOutSettlement.CHARGE_FIELDS}
        if any(normalized[field] > charges[field] for field in normalized):
            raise ValueError("單一費用的分攤金額不可超過應收費用")
        allocated_amount = sum(normalized.values(), Decimal("0"))
        if allocated_amount > cls._money(settlement.refund_amount):
            raise ValueError("退款分攤總額不可超過全額退款")

        for field, amount in normalized.items():
            if amount:
                db.session.add(MoveOutSettlementAllocation(
                    settlement=settlement,
                    charge_type=field,
                    amount=amount,
                    confirmed_by=confirmed_by,
                ))
        settlement.status = "settled"
        settlement.settled_at = datetime.now(UTC).replace(tzinfo=None)
        db.session.commit()
        return settlement

    @staticmethod
    def delete(settlement):
        MoveOutSettlementService._assert_draft(settlement)
        db.session.delete(settlement)
        db.session.commit()

    @staticmethod
    def void(settlement, *, reason: str):
        if settlement.status != "settled":
            raise ValueError("只有已結算結清單可以作廢")
        if not (reason or "").strip():
            raise ValueError("作廢必須填寫原因")
        settlement.status = "voided"
        settlement.void_reason = reason.strip()
        settlement.voided_at = datetime.now(UTC).replace(tzinfo=None)
        db.session.commit()
        return settlement
