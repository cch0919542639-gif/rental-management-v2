from app.core.db import db
from app.core.errors import ConflictError, DomainValidationError
from app.core.year_month import to_db_year_month
from app.models import Contract, MonthlyBill, Room, WaterBill
from app.repositories import BillingRepository, ContractRepository
from app.services.billing_service import BillingService
from app.services.rate_policy_service import RatePolicyService
from app.services.utility_draft_service import UtilityDraftService
from app.services.utility_policy_resolver import UtilityPolicyResolver
from app.services.water_allocation_service import WaterAllocationService
from sqlalchemy.exc import IntegrityError


class WaterService:
    ROOM_STATUS_LABELS = {
        "occupied": "居住中",
        "vacant": "空房",
    }

    @staticmethod
    def _resolve_contract_for_monthly_bill(monthly_bill_id: int):
        monthly_bill = BillingRepository.get_or_404(monthly_bill_id)
        contract = ContractRepository.get_or_404(monthly_bill.contract_id)
        return monthly_bill, contract

    @staticmethod
    def create_water_bill(**payload):
        if payload["billing_end"] <= payload["billing_start"]:
            raise DomainValidationError("水費帳期結束日必須晚於開始日")
        if (payload.get("total_amount") or 0) < 0:
            raise DomainValidationError("水費總額不可小於 0")

        water_bill = WaterBill(**payload)
        db.session.add(water_bill)
        db.session.commit()
        return water_bill

    @staticmethod
    def update_water_bill(water_bill: WaterBill, **payload):
        if payload["billing_end"] <= payload["billing_start"]:
            raise DomainValidationError("水費帳期結束日必須晚於開始日")
        if (payload.get("total_amount") or 0) < 0:
            raise DomainValidationError("水費總額不可小於 0")

        for key, value in payload.items():
            setattr(water_bill, key, value)
        db.session.commit()
        return water_bill

    @staticmethod
    def post_shared_to_monthly_bill(*, monthly_bill_id: int, water_bill: WaterBill):
        monthly_bill = BillingRepository.get_or_404(monthly_bill_id)
        line = UtilityDraftService.confirmed_line_for_monthly_bill(
            utility_type=UtilityDraftService.WATER,
            monthly_bill=monthly_bill,
            water_bill_id=water_bill.id,
        )
        preview = WaterService.preview_shared_to_monthly_bill(monthly_bill_id=monthly_bill_id, water_bill=water_bill)
        monthly_bill.water_amount = line.confirmed_amount if line.confirmed_amount is not None else line.calculated_amount
        monthly_bill.water_usage = preview["preview_water_usage"]
        BillingService.calculate_total(monthly_bill)
        db.session.commit()
        return monthly_bill

    @staticmethod
    def post_independent_to_monthly_bill(*, monthly_bill_id: int, water_bill: WaterBill, amount):
        monthly_bill = BillingRepository.get_or_404(monthly_bill_id)
        line = UtilityDraftService.confirmed_line_for_monthly_bill(
            utility_type=UtilityDraftService.WATER,
            monthly_bill=monthly_bill,
            water_bill_id=water_bill.id,
        )
        monthly_bill.water_amount = line.confirmed_amount if line.confirmed_amount is not None else line.calculated_amount
        BillingService.calculate_total(monthly_bill)
        db.session.commit()
        return monthly_bill

    @staticmethod
    def preview_shared_to_monthly_bill(*, monthly_bill_id: int, water_bill: WaterBill):
        monthly_bill = BillingRepository.get_or_404(monthly_bill_id)
        contract = ContractRepository.get_or_404(monthly_bill.contract_id)
        active_contracts = [
            item
            for item in ContractRepository.list_active()
            if item.room.property_id == water_bill.property_id
        ]

        contract_days = WaterAllocationService.overlap_days(
            contract=contract,
            billing_start=water_bill.billing_start,
            billing_end=water_bill.billing_end,
        )
        total_days = sum(
            WaterAllocationService.overlap_days(
                contract=item,
                billing_start=water_bill.billing_start,
                billing_end=water_bill.billing_end,
            )
            for item in active_contracts
        )
        total_usage = (water_bill.actual_usage_1 or 0) + (water_bill.actual_usage_2 or 0)
        preview_water_amount = WaterAllocationService.allocate_shared_by_stay_days(
            total_amount=water_bill.total_amount,
            contract_days=contract_days,
            total_days=total_days,
        )
        preview_water_usage = WaterAllocationService.allocate_shared_usage_by_stay_days(
            total_usage=total_usage,
            contract_days=contract_days,
            total_days=total_days,
        )
        return {
            "mode": "shared_by_stay_days",
            "monthly_bill": monthly_bill,
            "contract": contract,
            "contract_days": contract_days,
            "total_days": total_days,
            "total_usage": total_usage,
            "preview_water_amount": preview_water_amount,
            "preview_water_usage": preview_water_usage,
        }

    @staticmethod
    def preview_property_shared_by_stay_days(*, water_bill: WaterBill):
        """Build a read-only, property-wide water allocation preview.

        The preview deliberately includes vacant rooms as zero rows.  Repair
        work is not a room occupancy state and never changes allocation.
        """
        rooms = (
            Room.query.filter_by(property_id=water_bill.property_id)
            .order_by(Room.room_number.asc())
            .all()
        )
        room_ids = [room.id for room in rooms]
        contracts = []
        if room_ids:
            contracts = (
                Contract.query.filter(
                    Contract.room_id.in_(room_ids),
                    Contract.status == "active",
                    Contract.start_date <= water_bill.billing_end,
                )
                .order_by(Contract.room_id.asc(), Contract.start_date.asc(), Contract.id.asc())
                .all()
            )

        contracts_by_room = {}
        for contract in contracts:
            contracts_by_room.setdefault(contract.room_id, []).append(contract)

        rows = []
        eligible_rows = []
        for room in rooms:
            room_status = room.status or "vacant"
            room_contracts = contracts_by_room.get(room.id, [])
            if room_status == "vacant":
                rows.append(WaterService._property_preview_row(room=room, reason=WaterService._non_billable_reason(room_status)))
                continue

            if not room_contracts:
                rows.append(WaterService._property_preview_row(room=room, reason="無現行居住合約"))
                continue

            for contract in room_contracts:
                policy_code = UtilityPolicyResolver.resolve_water_policy(contract)
                stay_days = WaterAllocationService.overlap_days(
                    contract=contract,
                    billing_start=water_bill.billing_start,
                    billing_end=water_bill.billing_end,
                )
                row = WaterService._property_preview_row(
                    room=room,
                    contract=contract,
                    stay_days=stay_days,
                    policy_code=policy_code,
                )
                if policy_code != UtilityPolicyResolver.WATER_BILL_BY_STAY_DAYS:
                    row["reason"] = "非水單按居住天數分攤策略"
                elif stay_days == 0:
                    row["reason"] = "帳期內無居住日"
                else:
                    eligible_rows.append(row)
                rows.append(row)

        total_days = sum(row["stay_days"] for row in eligible_rows)
        for row in eligible_rows:
            row["allocated_amount"] = WaterAllocationService.allocate_shared_by_stay_days_ceiling(
                total_amount=water_bill.total_amount,
                contract_days=row["stay_days"],
                total_days=total_days,
            )

        allocated_total = sum((row["allocated_amount"] for row in rows), start=0)
        return {
            "water_bill": water_bill,
            "property": water_bill.property,
            "billing_start": water_bill.billing_start,
            "billing_end": water_bill.billing_end,
            "rows": rows,
            "total_days": total_days,
            "billed_total": water_bill.total_amount,
            "allocated_total": allocated_total,
            "rounding_difference": allocated_total - water_bill.total_amount,
        }

    @staticmethod
    def create_property_draft(*, water_bill: WaterBill, year_month: str):
        try:
            db_year_month = to_db_year_month(year_month)
        except ValueError as exc:
            raise DomainValidationError("入帳月份必須為 YYYYMM 或 YYYY-MM") from exc
        preview = WaterService.preview_property_shared_by_stay_days(water_bill=water_bill)
        draft = UtilityDraftService.create_draft(
            utility_type=UtilityDraftService.WATER,
            property_id=water_bill.property_id,
            year_month=db_year_month,
            billing_start=water_bill.billing_start,
            billing_end=water_bill.billing_end,
            billed_total=water_bill.total_amount,
            policy_code="water_bill_by_stay_days",
            rounding_mode=UtilityDraftService.PER_ROOM_CEILING,
            water_bill_id=water_bill.id,
        )
        lines = []
        for row in preview["rows"]:
            contract = row["contract"]
            monthly_bill = (
                MonthlyBill.query.filter_by(contract_id=contract.id, year_month=db_year_month).one_or_none()
                if contract
                else None
            )
            lines.append({
                "room_id": row["room_id"],
                "contract_id": contract.id if contract else None,
                "monthly_bill_id": monthly_bill.id if monthly_bill else None,
                "room_number_snapshot": row["room_number"],
                "occupant_name_snapshot": row["tenant_name"],
                "occupancy_status": row["room_status"],
                "exclusion_reason": row["reason"],
                "stay_days": row["stay_days"],
                "calculated_amount": row["allocated_amount"],
            })
        return UtilityDraftService.replace_lines(draft, lines)

    @staticmethod
    def _property_preview_row(*, room, contract=None, stay_days=0, policy_code=None, reason=None):
        return {
            "room_id": room.id,
            "address": room.property.address or room.property.name,
            "room_number": room.room_number,
            "tenant_name": contract.tenant.name if contract else None,
            "room_status": room.status or "vacant",
            "room_status_label": WaterService.ROOM_STATUS_LABELS.get(room.status or "vacant", room.status or "未設定"),
            "contract": contract,
            "stay_days": stay_days,
            "policy_code": policy_code,
            "allocated_amount": 0,
            "reason": reason,
        }

    @staticmethod
    def _non_billable_reason(room_status: str) -> str:
        return "空房不分攤"

    @staticmethod
    def preview_independent_to_monthly_bill(*, monthly_bill_id: int, amount):
        monthly_bill, contract = WaterService._resolve_contract_for_monthly_bill(monthly_bill_id)
        preview_water_amount = WaterAllocationService.allocate_independent_meter(amount=amount)
        return {
            "mode": "independent_meter",
            "monthly_bill": monthly_bill,
            "contract": contract,
            "preview_water_amount": preview_water_amount,
            "preview_water_usage": monthly_bill.water_usage or 0,
        }

    @staticmethod
    def preview_policy_to_monthly_bill(*, monthly_bill_id: int, water_bill: WaterBill):
        monthly_bill, contract = WaterService._resolve_contract_for_monthly_bill(monthly_bill_id)
        policy_code = UtilityPolicyResolver.resolve_water_policy(contract)
        if policy_code == UtilityPolicyResolver.WATER_BILL_BY_STAY_DAYS:
            preview = WaterService.preview_shared_to_monthly_bill(
                monthly_bill_id=monthly_bill_id,
                water_bill=water_bill,
            )
            preview["mode"] = "auto_policy"
            preview["resolved_policy"] = policy_code
            return preview

        if policy_code == UtilityPolicyResolver.WATER_FREE:
            return {
                "mode": "auto_policy",
                "resolved_policy": policy_code,
                "monthly_bill": monthly_bill,
                "contract": contract,
                "preview_water_amount": 0,
                "preview_water_usage": 0,
            }

        if policy_code == UtilityPolicyResolver.WATER_FIXED_MONTHLY:
            return {
                "mode": "auto_policy",
                "resolved_policy": policy_code,
                "monthly_bill": monthly_bill,
                "contract": contract,
                "preview_water_amount": RatePolicyService.resolve_water_rate(contract),
                "preview_water_usage": monthly_bill.water_usage or 0,
            }

        raise DomainValidationError("未知的水費策略，無法預覽")

    @staticmethod
    def post_policy_to_monthly_bill(*, monthly_bill_id: int, water_bill: WaterBill):
        preview = WaterService.preview_policy_to_monthly_bill(monthly_bill_id=monthly_bill_id, water_bill=water_bill)
        monthly_bill = preview["monthly_bill"]
        line = UtilityDraftService.confirmed_line_for_monthly_bill(
            utility_type=UtilityDraftService.WATER,
            monthly_bill=monthly_bill,
            water_bill_id=water_bill.id,
        )
        monthly_bill.water_amount = line.confirmed_amount if line.confirmed_amount is not None else line.calculated_amount
        monthly_bill.water_usage = preview["preview_water_usage"]
        BillingService.calculate_total(monthly_bill)
        db.session.commit()
        return monthly_bill

    @staticmethod
    def preview_post_to_monthly_bill(*, monthly_bill_id: int, water_bill: WaterBill, mode: str, amount=None):
        if mode == "auto_policy":
            return WaterService.preview_policy_to_monthly_bill(
                monthly_bill_id=monthly_bill_id,
                water_bill=water_bill,
            )
        if mode == "shared_by_stay_days":
            return WaterService.preview_shared_to_monthly_bill(
                monthly_bill_id=monthly_bill_id,
                water_bill=water_bill,
            )
        if mode == "independent_meter":
            return WaterService.preview_independent_to_monthly_bill(
                monthly_bill_id=monthly_bill_id,
                amount=amount,
            )
        raise DomainValidationError("未知的水費預覽模式")

    @staticmethod
    def delete_water_bill(water_bill: WaterBill):
        try:
            db.session.delete(water_bill)
            db.session.commit()
        except IntegrityError as exc:
            db.session.rollback()
            raise ConflictError("此水費單仍有關聯資料，無法刪除") from exc
