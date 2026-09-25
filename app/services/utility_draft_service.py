from datetime import date, datetime, timezone
from decimal import Decimal

from app.core.db import db
from app.core.errors import DomainValidationError
from app.core.year_month import to_db_year_month
from app.models.billing import MonthlyBill, UtilityCalculationDraft, UtilityCalculationLine, WaterBill
from app.models.electricity import ElectricityBill


class UtilityDraftService:
    WATER = "water"
    ELECTRICITY = "electricity"
    PER_ROOM_CEILING = "per_room_ceiling"
    BILL_RECONCILED = "bill_reconciled"

    ROOM_OCCUPIED = "occupied"
    ROOM_VACANT = "vacant"

    @staticmethod
    def _as_date(value):
        if isinstance(value, date):
            return value
        try:
            return date.fromisoformat(value)
        except (TypeError, ValueError) as exc:
            raise DomainValidationError("帳期必須是有效日期") from exc

    @staticmethod
    def _as_amount(value):
        try:
            amount = Decimal(str(value or 0))
        except Exception as exc:  # Decimal raises several input-specific errors.
            raise DomainValidationError("金額必須是有效數字") from exc
        if amount < 0:
            raise DomainValidationError("金額不可為負值")
        return amount.quantize(Decimal("0.01"))

    @staticmethod
    def _validate_source_bill(
        *,
        utility_type: str,
        property_id: int,
        water_bill_id: int | None,
        electricity_bill_id: int | None,
        billing_start: date,
        billing_end: date,
        billed_total: Decimal,
    ):
        """Keep a draft tied to the exact bill it is intended to reconcile."""
        if utility_type == UtilityDraftService.WATER:
            bill = db.session.get(WaterBill, water_bill_id)
            if bill is None:
                raise DomainValidationError("找不到來源水費單")
            source_total = UtilityDraftService._as_amount(bill.total_amount)
            source_start = bill.billing_start
            source_end = bill.billing_end
        else:
            bill = db.session.get(ElectricityBill, electricity_bill_id)
            if bill is None:
                raise DomainValidationError("找不到來源電費單")
            source_total = UtilityDraftService._as_amount(bill.total_amount)
            source_start = bill.period_start
            source_end = bill.period_end

        if bill.property_id != property_id:
            raise DomainValidationError("草稿物件必須與來源帳單相同")
        if source_start != billing_start or source_end != billing_end:
            raise DomainValidationError("草稿帳期必須與來源帳單相同")
        if source_total != billed_total:
            raise DomainValidationError("草稿總額必須與來源帳單相同")

    @staticmethod
    def create_draft(
        *,
        utility_type: str,
        property_id: int,
        year_month: str,
        billing_start,
        billing_end,
        billed_total,
        policy_code: str,
        rounding_mode: str,
        water_bill_id: int | None = None,
        electricity_bill_id: int | None = None,
        notes: str = "",
    ):
        if utility_type not in {UtilityDraftService.WATER, UtilityDraftService.ELECTRICITY}:
            raise DomainValidationError("水電類型必須是 water 或 electricity")
        if rounding_mode not in {UtilityDraftService.PER_ROOM_CEILING, UtilityDraftService.BILL_RECONCILED}:
            raise DomainValidationError("未知的整數分攤規則")
        if (water_bill_id is None) == (electricity_bill_id is None):
            raise DomainValidationError("草稿必須且只能對應一張水費單或電費單")
        if utility_type == UtilityDraftService.WATER and water_bill_id is None:
            raise DomainValidationError("水費草稿必須對應水費單")
        if utility_type == UtilityDraftService.ELECTRICITY and electricity_bill_id is None:
            raise DomainValidationError("電費草稿必須對應電費單")

        start = UtilityDraftService._as_date(billing_start)
        end = UtilityDraftService._as_date(billing_end)
        if end < start:
            raise DomainValidationError("帳期結束日不可早於開始日")
        try:
            db_year_month = to_db_year_month(year_month)
        except ValueError as exc:
            raise DomainValidationError("入帳月份必須為 YYYYMM 或 YYYY-MM") from exc
        normalized_total = UtilityDraftService._as_amount(billed_total)
        UtilityDraftService._validate_source_bill(
            utility_type=utility_type,
            property_id=property_id,
            water_bill_id=water_bill_id,
            electricity_bill_id=electricity_bill_id,
            billing_start=start,
            billing_end=end,
            billed_total=normalized_total,
        )

        draft = UtilityCalculationDraft(
            utility_type=utility_type,
            property_id=property_id,
            water_bill_id=water_bill_id,
            electricity_bill_id=electricity_bill_id,
            year_month=db_year_month,
            billing_start=start,
            billing_end=end,
            policy_code=policy_code,
            rounding_mode=rounding_mode,
            billed_total=normalized_total,
            allocated_total=Decimal("0.00"),
            reconciliation_difference=Decimal("0.00"),
            status=UtilityCalculationDraft.DRAFT,
            notes=notes or "",
        )
        db.session.add(draft)
        db.session.commit()
        return draft

    @staticmethod
    def replace_lines(draft: UtilityCalculationDraft, lines: list[dict]):
        if draft.status != UtilityCalculationDraft.DRAFT:
            raise DomainValidationError("只有草稿狀態可修改分攤明細")

        valid_statuses = {
            UtilityDraftService.ROOM_OCCUPIED,
            UtilityDraftService.ROOM_VACANT,
        }
        draft.lines.clear()
        allocated_total = Decimal("0.00")
        for item in lines:
            status = item.get("occupancy_status")
            if status not in valid_statuses:
                raise DomainValidationError("房間狀態必須為 occupied 或 vacant")
            stay_days = item.get("stay_days", 0)
            if not isinstance(stay_days, int) or stay_days < 0:
                raise DomainValidationError("住居日數必須為非負整數")
            amount = UtilityDraftService._as_amount(item.get("calculated_amount", 0))
            line = UtilityCalculationLine(
                room_id=item.get("room_id"),
                contract_id=item.get("contract_id"),
                monthly_bill_id=item.get("monthly_bill_id"),
                room_number_snapshot=str(item.get("room_number_snapshot") or ""),
                occupant_name_snapshot=item.get("occupant_name_snapshot"),
                occupancy_status=status,
                exclusion_reason=item.get("exclusion_reason"),
                stay_days=stay_days,
                calculated_amount=amount,
                confirmed_amount=item.get("confirmed_amount"),
            )
            if not line.room_number_snapshot:
                raise DomainValidationError("分攤明細必須保留房號")
            draft.lines.append(line)
            allocated_total += amount

        draft.allocated_total = allocated_total
        draft.reconciliation_difference = allocated_total - Decimal(str(draft.billed_total or 0))
        db.session.commit()
        return draft

    @staticmethod
    def confirmed_line_for_monthly_bill(
        *,
        utility_type: str,
        monthly_bill: MonthlyBill,
        water_bill_id: int | None = None,
        electricity_bill_id: int | None = None,
    ):
        """Return the reviewed line that is allowed to update this monthly bill."""
        if (water_bill_id is None) == (electricity_bill_id is None):
            raise DomainValidationError("入帳必須指定一張來源水費單或電費單")

        drafts = UtilityCalculationDraft.query.filter_by(
            utility_type=utility_type,
            year_month=monthly_bill.year_month,
            status=UtilityCalculationDraft.CONFIRMED,
            water_bill_id=water_bill_id,
            electricity_bill_id=electricity_bill_id,
        ).order_by(UtilityCalculationDraft.id.desc()).all()
        for draft in drafts:
            for line in draft.lines:
                if line.monthly_bill_id == monthly_bill.id:
                    return line
        raise DomainValidationError("此月帳單尚無對應的已確認水電草稿，不能入帳")

    @staticmethod
    def confirm(draft: UtilityCalculationDraft):
        if draft.status != UtilityCalculationDraft.DRAFT:
            raise DomainValidationError("只有草稿狀態可確認")
        draft.status = UtilityCalculationDraft.CONFIRMED
        draft.confirmed_at = datetime.now(timezone.utc)
        db.session.commit()
        return draft

    @staticmethod
    def mark_posted(draft: UtilityCalculationDraft):
        if draft.status != UtilityCalculationDraft.CONFIRMED:
            raise DomainValidationError("草稿必須先確認才能入帳")
        draft.status = UtilityCalculationDraft.POSTED
        draft.posted_at = datetime.now(timezone.utc)
        db.session.commit()
        return draft
