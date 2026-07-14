r"""Dry-run-first backfill of missing historical MonthlyBill rows from Google Sheet evidence.

Scope: 202604 (24 safe candidates) + 202605 (1 safe candidate) only.
Each candidate is gated by 9 stop conditions before insertion.

Usage:
    py -3 .\scripts\repair\backfill_missing_monthly_bills.py
        --database-url sqlite:///D:\CodexRuntime\rental\rebuild\runtime-real.db
        --csv .\real_import\sheet_202604.csv
        --year-month 202604

    py -3 .\scripts\repair\backfill_missing_monthly_bills.py
        --database-url sqlite:///D:\CodexRuntime\rental\rebuild\runtime-real.db
        --csv .\real_import\sheet_202605.csv
        --year-month 202605 --execute

Rollback: restore the pre-execute database backup, or delete the created rows.
The script only creates new MonthlyBill rows and never modifies existing ones.
"""

from __future__ import annotations

import argparse
import csv
import os
import re
import sys
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# ── stop list: contract_id or tenant name never processed ──────────────
STOP_TENANT_NAMES = frozenset({
    "張硯傑", "張啟中", "邱聖霖", "高富國", "侯家敏",
    "李政諺", "何佾洋", "鄭博仁", "田美麗",
})
# Tenant names that indicate a virtual / vacant / repair room
VIRTUAL_NAME_PATTERN = re.compile(
    r"(待修|空房|倉庫|鐵皮|浴室|待補|牆面，三層櫃|冷氣)", re.UNICODE
)

# ── thresholds ─────────────────────────────────────────────────────────
RENT_DIFF_THRESHOLD = Decimal("100")
TOTAL_DIFF_THRESHOLD = Decimal("10")


def _money(value: Decimal) -> str:
    return f"{value.quantize(Decimal('1'), rounding=ROUND_HALF_UP):,.0f}"


def _parse_decimal(raw: str) -> Decimal:
    """Parse a CSV value that may contain commas, empty string, or None."""
    if not raw:
        return Decimal("0")
    cleaned = raw.strip().replace(",", "").replace('"', "").replace(" ", "")
    if not cleaned:
        return Decimal("0")
    return Decimal(cleaned)


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Dry-run-first backfill of missing historical MonthlyBill rows"
    )
    parser.add_argument("--database-url", required=True, help="Target database URL")
    parser.add_argument("--csv", type=Path, required=True, help="Sheet CSV path")
    parser.add_argument("--year-month", required=True, help="Target year-month (YYYYMM)")
    parser.add_argument("--execute", action="store_true", help="Persist the created bills")
    return parser


def _load_rows(path: Path) -> list[dict[str, str]]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def _find_contract(db, prop_address: str, room_number: str):
    """Find active contract for (property_address, room_number).

    Returns (contract, tenant_name) or (None, reason).
    """
    from app.models import Contract, Property, Room, Tenant

    room_number = room_number.strip()
    prop_address = prop_address.strip()

    # Exact match first
    prop = Property.query.filter_by(address=prop_address).first()
    if not prop:
        # Try contains match for properties that have sub-addresses
        props = Property.query.filter(Property.address.like(f"%{prop_address}%")).all()
        if len(props) == 1:
            prop = props[0]
    if not prop:
        return None, f"SKIP no property match for {prop_address}"

    room = Room.query.filter_by(property_id=prop.id, room_number=room_number).first()
    if not room:
        return None, f"SKIP no room {room_number} in property {prop.address}"

    contract = Contract.query.filter_by(room_id=room.id, status="active").first()
    if not contract:
        return None, f"SKIP no active contract for room {room_number} in {prop.address}"

    tenant = db.session.get(Tenant, contract.tenant_id)
    tenant_name = tenant.name if tenant else ""
    return contract, tenant_name


def _is_virtual_name(name: str) -> bool:
    """Check if the tenant name indicates a virtual/vacant/repair room."""
    if not name or not name.strip():
        return True
    return bool(VIRTUAL_NAME_PATTERN.search(name))


def _check_total_diff(
    calculated: Decimal, sheet_total: Decimal
) -> tuple[bool, str]:
    """Returns (is_safe, message)."""
    diff = abs(calculated - sheet_total)
    if diff == 0:
        return True, ""
    if diff <= TOTAL_DIFF_THRESHOLD:
        return True, f"CAUTION total diff={_money(diff)} (<=10)"
    return False, f"STOP total diff={_money(diff)} > 10"


def _check_rent_diff(
    sheet_rent: Decimal, contract_rent: Decimal
) -> tuple[bool, str]:
    """Returns (is_safe, message)."""
    diff = abs(sheet_rent - contract_rent)
    if diff == 0:
        return True, ""
    if diff <= RENT_DIFF_THRESHOLD:
        return True, f"CAUTION rent diff={_money(diff)} (<=100)"
    return False, f"STOP rent diff={_money(diff)} > 100"


def main(argv: list[str]) -> int:
    args = _build_parser().parse_args(argv)
    os.environ["DATABASE_URL"] = args.database_url
    os.environ.setdefault("SCRIPT_APP_CONFIG", "default")

    from app.core.db import db
    from app.models import MonthlyBill
    from app.repositories import BillingRepository
    from app.services import BillingService
    from scripts.repair._common import build_script_app

    app = build_script_app()
    rows = _load_rows(args.csv)
    year_month = args.year_month

    header = f"Missing Monthly Bills Backfill ({'EXECUTE' if args.execute else 'DRY-RUN'})"
    sep = "=" * 72
    print(sep)
    print(header)
    print(f"Database URL: {args.database_url}")
    print(f"CSV: {args.csv}")
    print(f"Year-Month: {year_month}")
    print(f"CSV rows: {len(rows)}")
    print(sep)

    safe = 0
    skipped = 0
    stopped = 0
    created = 0
    results: list[dict] = []

    with app.app_context():
        for row_idx, row in enumerate(rows, start=2):  # 1-indexed, row 1=header
            tenant_name = row.get("姓名", "").strip()
            prop_address = row.get("地點", "").strip()
            room_number = row.get("房號", "").strip()

            # ── C-08: Virtual tenant filter ────────────────
            if _is_virtual_name(tenant_name):
                skipped += 1
                results.append(dict(row=row_idx, name=tenant_name or "(empty)",
                                    status="SKIP", reason="virtual/vacant/repair room"))
                continue

            # ── Stop list check ─────────────────────────────
            if tenant_name in STOP_TENANT_NAMES:
                skipped += 1
                results.append(dict(row=row_idx, name=tenant_name,
                                    status="SKIP", reason="stop-list tenant"))
                continue

            # ── C-07: Find contract ────────────────────────
            contract, name_or_reason = _find_contract(db, prop_address, room_number)
            if contract is None:
                skipped += 1
                results.append(dict(row=row_idx, name=tenant_name,
                                    status="SKIP", reason=name_or_reason))
                continue

            # ── C-07: Contract rent = 0 guard ──────────────
            contract_rent = Decimal(str(contract.rent or 0))
            if contract_rent == 0:
                skipped += 1
                results.append(dict(row=row_idx, name=tenant_name,
                                    status="SKIP", reason="contract rent=0 (placeholder)"))
                continue

            # ── C-06: Duplicate check ───────────────────────
            existing = BillingRepository.find_by_contract_and_month(contract.id, year_month)
            if existing:
                skipped += 1
                results.append(dict(row=row_idx, name=tenant_name,
                                    status="SKIP",
                                    reason=f"duplicate bill={existing.id} exists"))
                continue

            # ── Parse sheet fields ──────────────────────────
            sheet_rent = _parse_decimal(row.get("租金", ""))
            electricity_amount = _parse_decimal(row.get("電費", ""))
            water_amount = _parse_decimal(row.get("水費", ""))
            management_fee = _parse_decimal(row.get("管理費", ""))
            other_raw = row.get("其他", "").strip()
            other_desc = None
            other_amount = _parse_decimal(other_raw)
            # If 其他 is non-numeric text, use only management fee as other_charges
            if other_raw and other_amount == 0 and management_fee == 0:
                other_desc = other_raw[:200] if other_raw else None
                other_amount = Decimal("0")
            other_charges = management_fee + other_amount
            sheet_total = _parse_decimal(row.get("應繳", ""))

            # ── C-09: Rent mismatch check ──────────────────
            rent_ok, rent_msg = _check_rent_diff(sheet_rent, contract_rent)
            if not rent_ok:
                stopped += 1
                results.append(dict(row=row_idx, name=tenant_name,
                                    status="STOP", reason=rent_msg))
                continue

            # ── C-01: previous_balance ─────────────────────
            if year_month == "202604":
                previous_balance = Decimal("0")
                notes_balance = "前期差額無證據，設為0"
            elif year_month == "202605":
                raw_pb = row.get("未收款", "").strip()
                if raw_pb:
                    previous_balance = _parse_decimal(raw_pb)
                else:
                    previous_balance = Decimal("0")
                notes_balance = f"前期差額={_money(previous_balance)}（Sheet未收款）"
            else:
                stopped += 1
                results.append(dict(row=row_idx, name=tenant_name,
                                    status="STOP", reason=f"unsupported year_month {year_month}"))
                continue

            # ── Build bill fields ───────────────────────────
            # Use contract rent (authoritative) when there's a small diff
            rent = contract_rent if rent_ok else sheet_rent
            # electricity_prev/curr/usage = 0 per C-03
            # water_prev/curr/usage = 0 per C-04
            # public_electricity = 0 per C-05
            public_electricity = Decimal("0")

            notes = (
                f"歷史回填 — Google Sheet {year_month} row {row_idx}；"
                f"{notes_balance}"
            )

            # ── C-02: Calculate total ───────────────────────
            calculated_total = MonthlyBill.calculate_total(
                rent=rent,
                electricity_amount=electricity_amount,
                public_electricity=public_electricity,
                water_amount=water_amount,
                other_charges=other_charges,
                previous_balance=previous_balance,
            )

            total_ok, total_msg = _check_total_diff(calculated_total, sheet_total)
            if not total_ok:
                stopped += 1
                results.append(dict(row=row_idx, name=tenant_name,
                                    status="STOP",
                                    reason=f"{total_msg}; sheet={_money(sheet_total)} calc={_money(calculated_total)}"))
                continue

            # ── All gates passed — SAFE candidate ───────────
            safe += 1
            results.append(dict(
                row=row_idx, name=tenant_name,
                status="SAFE",
                contract_id=contract.id,
                rent=rent,
                electricity=electricity_amount,
                water=water_amount,
                other=other_charges,
                previous_balance=previous_balance,
                total=calculated_total,
                sheet_total=sheet_total,
                notes=notes,
                extra=rent_msg if rent_msg else None,
            ))

            if not args.execute:
                continue

            # ── Execute: create the bill ────────────────────
            bill = MonthlyBill(
                contract_id=contract.id,
                year_month=year_month,
                rent=rent,
                electricity_amount=electricity_amount,
                public_electricity=public_electricity,
                water_amount=water_amount,
                other_charges=other_charges,
                other_desc=other_desc,
                previous_balance=previous_balance,
                total=calculated_total,
                paid=False,
                paid_date=None,
                notes=notes,
            )
            db.session.add(bill)
            db.session.flush()
            created += 1

        if args.execute:
            db.session.commit()

    # ── Print report ────────────────────────────────────────────────────
    print(f"\n{'Row':>5} {'Status':>6} {'Contract':>9}  {'Tenant':<20}  Detail")
    print("-" * 72)
    for r in results:
        cid = r.get("contract_id", "")
        detail = r["reason"] if r["status"] in ("SKIP", "STOP") else ""
        if r["status"] == "SAFE":
            detail = (
                f"rent={_money(r['rent'])} elec={_money(r['electricity'])} "
                f"water={_money(r['water'])} other={_money(r['other'])} "
                f"pb={_money(r['previous_balance'])} total={_money(r['total'])}"
            )
            if r.get("extra"):
                detail += f" [{r['extra']}]"
        print(f"{r['row']:>5} {r['status']:>6} {str(cid):>9}  {r['name']:<20}  {detail}")

    print(sep)
    print(f"SAFE: {safe} | SKIP: {skipped} | STOP: {stopped} | Created: {created}")
    if not args.execute:
        print("Dry-run only. Re-run with --execute to persist the SAFE candidates.")
    print(sep)

    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))