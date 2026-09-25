from decimal import Decimal

from app.core.db import db
from app.core.errors import DomainValidationError
from app.core.year_month import to_db_year_month
from app.models import ElectricityBill, ElectricityMeter, ElectricityReading, MonthlyBill, Room
from app.repositories import BillingRepository, ContractRepository, ElectricityReadingRepository
from app.services.billing_service import BillingService
from app.services.rate_policy_service import RatePolicyService
from app.services.utility_draft_service import UtilityDraftService
from app.services.utility_policy_resolver import UtilityPolicyResolver


class ElectricityService:
    @staticmethod
    def _resolve_contract(room_id: int | None):
        if not room_id:
            return None
        return ContractRepository.active_for_room(room_id)

    @staticmethod
    def _resolve_contract_for_period(room_id: int | None, *, period_start, period_end):
        if not room_id:
            return None
        candidates = [
            item
            for item in ContractRepository.list_active()
            # Active is the actual residence flag.  A still-active tenant is
            # kept in the allocation even when the original contract end date
            # has passed.
            if item.room_id == room_id and item.start_date <= period_end
        ]
        if candidates:
            return sorted(candidates, key=lambda item: item.start_date, reverse=True)[0]
        return ContractRepository.active_for_room(room_id)

    @staticmethod
    def _active_contracts_for_property_period(property_id: int, *, period_start, period_end):
        return [
            item
            for item in ContractRepository.list_active()
            if item.room.property_id == property_id and item.start_date <= period_end
        ]

    @staticmethod
    def _calculate_reading_amount(*, bill: ElectricityBill, reading: ElectricityReading, total_usage: Decimal):
        contract = ElectricityService._resolve_contract_for_period(
            reading.room_id,
            period_start=bill.period_start,
            period_end=bill.period_end,
        )
        policy_code = UtilityPolicyResolver.resolve_electricity_policy(contract)
        usage = Decimal(str(reading.usage or 0))
        bill_total_amount = Decimal(str(bill.total_amount or 0))
        public_amount = Decimal(str(bill.public_amount or 0))
        breakdown = {
            "policy_code": policy_code,
            "usage": usage,
            "flow_amount": Decimal("0.00"),
            "public_amount": Decimal("0.00"),
            "total_amount": Decimal("0.00"),
        }

        if policy_code == UtilityPolicyResolver.FIXED_ELECTRICITY:
            rate = RatePolicyService.resolve_electricity_rate(contract)
            amount = (usage * rate).quantize(Decimal("0.01"))
            breakdown["flow_amount"] = amount
            breakdown["total_amount"] = amount
            return breakdown

        if total_usage <= 0:
            raise DomainValidationError("非固定電費策略需要有效的總用電度數才可計算")

        if policy_code == UtilityPolicyResolver.BILL_USAGE_RATIO:
            amount = (bill_total_amount * usage / total_usage).quantize(Decimal("0.01"))
            breakdown["flow_amount"] = amount
            breakdown["total_amount"] = amount
            return breakdown

        if policy_code == UtilityPolicyResolver.BILL_USAGE_RATIO_PLUS_PUBLIC:
            active_contracts = ElectricityService._active_contracts_for_property_period(
                bill.property_id,
                period_start=bill.period_start,
                period_end=bill.period_end,
            )
            active_room_count = len({item.room_id for item in active_contracts})
            if active_room_count <= 0:
                raise DomainValidationError("公電均攤策略需要至少一筆有效合約")

            flow_pool = bill_total_amount - public_amount
            flow_amount = (flow_pool * usage / total_usage).quantize(Decimal("0.01"))
            public_share = (public_amount / Decimal(active_room_count)).quantize(Decimal("0.01"))
            breakdown["flow_amount"] = flow_amount
            breakdown["public_amount"] = public_share
            breakdown["total_amount"] = (flow_amount + public_share).quantize(Decimal("0.01"))
            return breakdown

        raise DomainValidationError("未知的電費策略，無法計算")

    @staticmethod
    def create_meter(**payload):
        meter = ElectricityMeter(**payload)
        db.session.add(meter)
        db.session.commit()
        return meter

    @staticmethod
    def update_meter(meter: ElectricityMeter, **payload):
        for key, value in payload.items():
            setattr(meter, key, value)
        db.session.commit()
        return meter

    @staticmethod
    def create_bill(**payload):
        if payload["period_end"] <= payload["period_start"]:
            raise DomainValidationError("電費帳期結束日必須晚於開始日")

        prev_reading = Decimal(str(payload.get("prev_reading") or 0))
        curr_reading = Decimal(str(payload.get("curr_reading") or 0))
        total_usage = curr_reading - prev_reading
        if total_usage < 0:
            raise DomainValidationError("電表讀數不可倒退")

        payload["year_month"] = to_db_year_month(payload["year_month"])
        payload["total_usage"] = total_usage
        bill = ElectricityBill(status="pending", **payload)
        db.session.add(bill)
        db.session.commit()
        return bill

    @staticmethod
    def add_reading(bill: ElectricityBill, **payload):
        prev_reading = Decimal(str(payload.get("prev_reading") or 0))
        curr_reading = Decimal(str(payload.get("curr_reading") or 0))
        usage = curr_reading - prev_reading
        if usage < 0:
            raise DomainValidationError("抄表 usage 不可為負值")

        payload["usage"] = usage
        confirmed_amount = payload.get("confirmed_amount")
        calculated_amount = payload.get("calculated_amount")
        if calculated_amount in (None, ""):
            contract = ElectricityService._resolve_contract_for_period(
                payload.get("room_id"),
                period_start=bill.period_start,
                period_end=bill.period_end,
            )
            policy_code = UtilityPolicyResolver.resolve_electricity_policy(contract)
            if policy_code == UtilityPolicyResolver.FIXED_ELECTRICITY:
                rate = RatePolicyService.resolve_electricity_rate(contract)
                calculated_amount = (usage * rate).quantize(Decimal("0.01"))
            else:
                calculated_amount = Decimal("0.00")
        payload["calculated_amount"] = calculated_amount
        if confirmed_amount is not None:
            payload["confirmed_amount"] = confirmed_amount

        reading = ElectricityReading(bill_id=bill.id, **payload)
        db.session.add(reading)
        db.session.commit()
        return reading

    @staticmethod
    def calculate_bill(bill: ElectricityBill):
        readings = ElectricityReadingRepository.list_for_bill(bill.id)
        total_usage = sum((Decimal(str(item.usage or 0)) for item in readings), Decimal("0.0"))
        flow_amount = Decimal("0.00")
        total_amount = Decimal("0.00")
        has_policy_resolver_amount = False

        for reading in readings:
            breakdown = ElectricityService._calculate_reading_amount(
                bill=bill,
                reading=reading,
                total_usage=total_usage,
            )
            reading.calculated_amount = breakdown["total_amount"]
            effective_amount = Decimal(
                str(reading.confirmed_amount if reading.confirmed_amount is not None else reading.calculated_amount or 0)
            )
            flow_amount += effective_amount
            total_amount += effective_amount
            if breakdown["policy_code"] != UtilityPolicyResolver.FIXED_ELECTRICITY:
                has_policy_resolver_amount = True

        bill.total_usage = total_usage
        bill.flow_amount = flow_amount.quantize(Decimal("0.01"))
        if has_policy_resolver_amount:
            bill.total_amount = total_amount.quantize(Decimal("0.01"))
        else:
            bill.total_amount = (bill.flow_amount + Decimal(str(bill.public_amount or 0))).quantize(Decimal("0.01"))
        bill.status = "calculated"
        db.session.commit()
        return bill

    @staticmethod
    def preview_property_bill(*, bill: ElectricityBill):
        """Build a read-only reconciliation for every room on an electricity bill."""
        readings = ElectricityReadingRepository.list_for_bill(bill.id)
        rooms = Room.query.filter_by(property_id=bill.property_id).order_by(Room.room_number.asc()).all()
        blockers = ElectricityService._preview_blockers(bill=bill, readings=readings)
        total_usage = sum((Decimal(str(item.usage or 0)) for item in readings), Decimal("0.0"))
        rows = []

        if not blockers:
            for reading in readings:
                breakdown = ElectricityService._calculate_reading_amount(
                    bill=bill,
                    reading=reading,
                    total_usage=total_usage,
                )
                rows.append(ElectricityService._preview_reading_row(reading=reading, breakdown=breakdown))
        else:
            for reading in readings:
                rows.append(ElectricityService._preview_reading_row(reading=reading))

        read_room_ids = {reading.room_id for reading in readings if reading.room_id}
        for room in rooms:
            if room.id not in read_room_ids:
                rows.append(
                    {
                        "address": room.property.address or room.property.name,
                        "room_number": room.room_number,
                        "meter_number": None,
                        "prev_reading": None,
                        "curr_reading": None,
                        "usage": Decimal("0.0"),
                        "policy_code": None,
                        "flow_amount": Decimal("0.00"),
                        "public_amount": Decimal("0.00"),
                        "allocated_amount": Decimal("0.00"),
                        "reason": "空房未抄表" if room.status == "vacant" else "缺少房間抄表資料",
                    }
                )

        allocated_total = sum((row["allocated_amount"] for row in rows), Decimal("0.00"))
        return {
            "bill": bill,
            "property": bill.property,
            "rows": sorted(rows, key=lambda row: (row["room_number"] or "", row["meter_number"] or "")),
            "total_usage": total_usage,
            "billed_total": Decimal(str(bill.total_amount or 0)),
            "allocated_total": allocated_total,
            "unallocated_difference": (Decimal(str(bill.total_amount or 0)) - allocated_total).quantize(Decimal("0.01")),
            "blockers": blockers,
            "can_create_draft": not blockers,
        }

    @staticmethod
    def create_property_draft(*, bill: ElectricityBill):
        preview = ElectricityService.preview_property_bill(bill=bill)
        if preview["blockers"]:
            raise DomainValidationError("資料核對未通過，不能產生電費草稿")
        draft = UtilityDraftService.create_draft(
            utility_type=UtilityDraftService.ELECTRICITY,
            property_id=bill.property_id,
            year_month=bill.year_month,
            billing_start=bill.period_start,
            billing_end=bill.period_end,
            billed_total=bill.total_amount,
            policy_code="property_electricity_preview",
            rounding_mode=UtilityDraftService.BILL_RECONCILED,
            electricity_bill_id=bill.id,
        )
        lines = []
        for row in preview["rows"]:
            contract = ElectricityService._resolve_contract_for_period(
                row["room_id"], period_start=bill.period_start, period_end=bill.period_end
            )
            monthly_bill = (
                MonthlyBill.query.filter_by(contract_id=contract.id, year_month=bill.year_month).one_or_none()
                if contract
                else None
            )
            lines.append({
                "room_id": row["room_id"],
                "contract_id": contract.id if contract else None,
                "monthly_bill_id": monthly_bill.id if monthly_bill else None,
                "room_number_snapshot": row["room_number"],
                "occupancy_status": "vacant" if row["reason"] == "空房未抄表" else "occupied",
                "exclusion_reason": row["reason"] if row["allocated_amount"] == 0 else None,
                "stay_days": 0,
                "calculated_amount": row["allocated_amount"],
            })
        return UtilityDraftService.replace_lines(draft, lines)

    @staticmethod
    def _preview_blockers(*, bill: ElectricityBill, readings):
        blockers = []
        bill_usage = Decimal(str(bill.curr_reading or 0)) - Decimal(str(bill.prev_reading or 0))
        if bill_usage < 0:
            blockers.append("電費單主表讀數倒退")
        if bill.period_end <= bill.period_start:
            blockers.append("電費單帳期不完整或結束日早於開始日")

        reading_usage = Decimal("0.0")
        for reading in readings:
            usage = Decimal(str(reading.curr_reading or 0)) - Decimal(str(reading.prev_reading or 0))
            if usage < 0:
                blockers.append(f"房間 {reading.room.room_number if reading.room else reading.room_id or '-'} 的讀數倒退")
            if Decimal(str(reading.usage or 0)) != usage:
                blockers.append(f"房間 {reading.room.room_number if reading.room else reading.room_id or '-'} 的儲存度數與前後讀數不一致")
            reading_usage += Decimal(str(reading.usage or 0))
            if reading.meter is None or reading.meter.property_id != bill.property_id:
                blockers.append(f"抄表 #{reading.id} 的電表不屬於此物件")
            if reading.room is not None and reading.room.property_id != bill.property_id:
                blockers.append(f"抄表 #{reading.id} 的房間不屬於此物件")
            if reading.meter and reading.meter.room_id and reading.room_id and reading.meter.room_id != reading.room_id:
                blockers.append(f"抄表 #{reading.id} 的表號與房號不符")
            if bill.meter and not bill.meter.is_main and reading.meter_id != bill.meter_id:
                blockers.append(f"抄表 #{reading.id} 的表號與電費單指定表號不符")

        if bill.meter and bill.meter.is_main and readings and reading_usage != bill_usage:
            blockers.append("分表度數合計與主表帳期度數不一致")
        if not readings:
            blockers.append("尚無房間抄表資料")
        return list(dict.fromkeys(blockers))

    @staticmethod
    def _preview_reading_row(*, reading: ElectricityReading, breakdown=None):
        breakdown = breakdown or {
            "policy_code": None,
            "flow_amount": Decimal("0.00"),
            "public_amount": Decimal("0.00"),
            "total_amount": Decimal("0.00"),
        }
        room = reading.room
        meter = reading.meter
        return {
            "room_id": room.id if room else None,
            "address": room.property.address if room and room.property.address else (meter.property.address if meter else "-"),
            "room_number": room.room_number if room else "未指定",
            "meter_number": meter.meter_number if meter and meter.meter_number else str(reading.meter_id),
            "prev_reading": reading.prev_reading,
            "curr_reading": reading.curr_reading,
            "usage": reading.usage,
            "policy_code": breakdown["policy_code"],
            "flow_amount": breakdown["flow_amount"],
            "public_amount": breakdown["public_amount"],
            "allocated_amount": breakdown["total_amount"],
            "reason": "待修正資料後才可產生草稿" if breakdown["policy_code"] is None else "依策略計算",
        }

    @staticmethod
    def post_to_monthly_bill(*, monthly_bill: MonthlyBill, reading: ElectricityReading, public_electricity=0):
        bill = reading.bill
        if bill is None:
            raise DomainValidationError("抄表缺少來源電費單，不能入帳")
        line = UtilityDraftService.confirmed_line_for_monthly_bill(
            utility_type=UtilityDraftService.ELECTRICITY,
            monthly_bill=monthly_bill,
            electricity_bill_id=bill.id,
        )
        resolved_public = Decimal(str(public_electricity or 0))
        electricity_amount = Decimal(str(reading.confirmed_amount or reading.calculated_amount or 0))
        if bill is not None:
            breakdown = ElectricityService._calculate_reading_amount(
                bill=bill,
                reading=reading,
                total_usage=Decimal(str(bill.total_usage or 0)),
            )
            if breakdown["policy_code"] == UtilityPolicyResolver.BILL_USAGE_RATIO_PLUS_PUBLIC and not public_electricity:
                resolved_public = breakdown["public_amount"]
                electricity_amount = breakdown["flow_amount"]

        reviewed_amount = Decimal(str(line.confirmed_amount if line.confirmed_amount is not None else line.calculated_amount))
        if (electricity_amount + resolved_public).quantize(Decimal("0.01")) != reviewed_amount.quantize(Decimal("0.01")):
            raise DomainValidationError("來源讀數與已確認草稿金額不一致，請重新產生並確認草稿")

        monthly_bill.electricity_prev = reading.prev_reading
        monthly_bill.electricity_curr = reading.curr_reading
        monthly_bill.electricity_usage = reading.usage
        monthly_bill.electricity_amount = electricity_amount
        monthly_bill.public_electricity = resolved_public
        BillingService.calculate_total(monthly_bill)
        db.session.commit()
        return monthly_bill

    @staticmethod
    def post_reading_to_monthly_bill(*, monthly_bill_id: int, reading: ElectricityReading, public_electricity=0):
        monthly_bill = BillingRepository.get_or_404(monthly_bill_id)
        return ElectricityService.post_to_monthly_bill(
            monthly_bill=monthly_bill,
            reading=reading,
            public_electricity=public_electricity,
        )

    @staticmethod
    def property_overview(*, property_obj, meters, bills):
        total_public_amount = sum((Decimal(str(bill.public_amount or 0)) for bill in bills), Decimal("0.00"))
        total_flow_amount = sum((Decimal(str(bill.flow_amount or 0)) for bill in bills), Decimal("0.00"))
        total_bill_amount = sum((Decimal(str(bill.total_amount or 0)) for bill in bills), Decimal("0.00"))
        return {
            "property_id": property_obj.id,
            "property_name": property_obj.name,
            "meter_count": len(meters),
            "main_meter_count": sum(1 for meter in meters if meter.is_main),
            "bill_count": len(bills),
            "pending_count": sum(1 for bill in bills if bill.status == "pending"),
            "calculated_count": sum(1 for bill in bills if bill.status == "calculated"),
            "posted_count": sum(1 for bill in bills if bill.status == "posted"),
            "total_public_amount": total_public_amount,
            "total_flow_amount": total_flow_amount,
            "total_bill_amount": total_bill_amount,
        }
