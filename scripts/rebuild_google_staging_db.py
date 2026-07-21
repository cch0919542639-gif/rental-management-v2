"""Build an isolated SQLite staging database from the Google monthly source workbook.

This script is deliberately non-destructive: it refuses to overwrite its output
database and does not read from or write to either existing runtime-real.db file.
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from collections import defaultdict
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path

import requests
from openpyxl import load_workbook
from openpyxl.utils.datetime import from_excel


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


SPREADSHEET_ID = "1WmqQbPo8EsWrbplDInp1Q3rv6bYsCcesh4BE6qYJ-dc"
SOURCE_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=xlsx"
MONTHS = ("202604", "202605", "202606", "202607")

# Property-level sheets supplied on 2026-07-21.  The monthly source remains
# authoritative for monthly charges and the current occupant; these sheets
# only fill otherwise missing agreement dates, deposits, and meter baselines.
SUPPLEMENTARY_SHEETS = {
    "1Kt9eZtBV7WtONNnXJ1zgNXMH85qXBuMdSV8ACudZRmg": "立志街204巷",
    "1fkOeCvSu2zYEwWjAyHd8_7ihGhvdGV0VzhMqEJpxWAE": "昌裕122巷17號",
    "15nY_tNZmZm12pz1gy6jOxX3yefUVLfMDEaOC8KXsfXk": "苓中路33巷",
    "1jb2_kwiIEHvm3N39jzoqmXej3i-QIu9_cbRx9Au9tXA": "必信街26號",
    "1Yvyqy5bpjERutESxI60PYfLnCsWA1w0OIRIwMcsAMr4": "楠都東街",
    "13-koPsavkjtHoCTNfwwDl7KT50PLZ7QKd1ySz9sAAtg": "錦州173號4樓",
    "1XQIzj3BEflAGDgj6DPDC3Skdu5m6MEe5pE_n2N58omU": "宣化62號4樓",
    "1YyoY5A6DA06OglQ7bETWwp1t5ym4TLWaDv-0zW2ljbo": "凱旋309號5樓",
    "1O_1yH-f9hgNiDmqMAGaQdJGm3V47uHqlOzJ1x6-71hw": "廣州39號5樓",
    "1UYqXAEDVV70xv19fYDQ88IIN__K2tBYrBN2uTDav4-Y": "永平38號5樓",
    "1ovrjmw4hhRYfo-oiBYkSTLIUI3-6-v5IjWajmxvb-KU": "自強27巷36號",
    "1Dw8zZwoYdweqUg4atV5uJYbNlA_P4HCJpjXgC3ey700": "永泰84巷5樓",
}

# This file contains two properties.  Its room prefixes make the split
# deterministic, and its agreement rows are used only as supplementary facts.
COMBINED_SHEET_ID = "1GFwFAzXfB27YCumMRE03bv0sngsjfZ_BjDOd_MMyF08"

# Explicitly confirmed by the user: this is a departed tenant's July final
# water settlement.  The other two close-outs lack a former-tenant identity
# and stay out of MonthlyBill until that identity is supplied.
CLOSEOUT_ASSIGNMENTS = {
    ("202607", "錦州173號4樓", "1"): {"tenant": "林胤妘", "phone": "0902200679"},
    # Reconciled from 「轉帳房東紀錄」.  These are former tenants whose
    # utilities appeared after their room became vacant or under repair.
    ("202604", "自強27巷36號", "3"): {"tenant": "王麗美", "phone": "0976180895"},
    ("202604", "自強27巷36號", "16"): {"tenant": "黃文櫻", "phone": "0981900922"},
    ("202605", "廣東77號14樓", "7"): {"tenant": "黃泰祥", "phone": "0986777205"},
    ("202605", "自強27巷36號", "16"): {"tenant": "黃文櫻", "phone": "0981900922"},
    ("202606", "自強27巷36號", "2"): {"tenant": "王儷靜", "phone": "0985577015"},
}

# User-confirmed: vacant-room charges at 昌裕71巷 are owner maintenance or
# incidental electricity, not tenant receivables.  Keep the room history but
# omit these non-tenant rows from settlement review and billing.
IGNORED_NON_TENANT_PROPERTIES = {"昌裕71巷"}
IGNORED_NON_TENANT_CHARGES = {
    ("202605", "自強27巷36號", "20"),
    ("202606", "自強27巷36號", "20"),
    ("202606", "永泰84巷5樓", "2"),
    ("202606", "永泰84巷6樓", "28"),
}


def as_text(value) -> str:
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value).strip()


def as_money(value) -> Decimal:
    if value in (None, ""):
        return Decimal("0")
    return Decimal(str(value)).quantize(Decimal("0.01"))


def parse_date(value) -> date | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, (int, float)):
        return from_excel(value).date()

    raw = as_text(value).replace("-", "/")
    parts = raw.split("/")
    if len(parts) != 3:
        return None
    try:
        year, month, day = (int(part) for part in parts)
        if year < 1911:
            year += 1911
        return date(year, month, day)
    except ValueError:
        return None


def first_header_indexes(header_row):
    indexes = {}
    for index, header in enumerate(header_row):
        label = as_text(header)
        if label and label not in indexes:
            indexes[label] = index
    return indexes


def value(row, indexes, header):
    index = indexes.get(header)
    return row[index] if index is not None and index < len(row) else None


def download_source(destination: Path):
    response = requests.get(SOURCE_URL, timeout=60)
    response.raise_for_status()
    destination.write_bytes(response.content)


def is_room_status_label(name: str) -> str | None:
    """Return a room state for non-person labels found in the monthly source."""
    compact = name.replace(" ", "")
    if not compact:
        return "vacant"
    if "待修" in compact or "維修" in compact:
        return "maintenance"
    if "空房" in compact:
        return "vacant"
    if "倉庫" in compact:
        return "storage"
    return None


def supplementary_property_for(sheet_id: str, room: str) -> str | None:
    if sheet_id != COMBINED_SHEET_ID:
        return SUPPLEMENTARY_SHEETS.get(sheet_id)
    return "廣東77號14樓" if room.startswith("77-") else "廣東73號4樓"


def collect_supplementary_contracts(destination: Path):
    """Download the supplied property sheets and collect non-sensitive lease facts."""
    destination.mkdir(parents=True, exist_ok=True)
    sheet_ids = [*SUPPLEMENTARY_SHEETS, COMBINED_SHEET_ID]
    facts = {}
    audit = {"downloaded": 0, "matched_facts": 0, "skipped_rows": []}
    for sheet_id in sheet_ids:
        path = destination / f"{sheet_id}.xlsx"
        response = requests.get(
            f"https://docs.google.com/spreadsheets/d/{sheet_id}/export?format=xlsx", timeout=60
        )
        if not response.ok:
            audit["skipped_rows"].append(
                {
                    "source": sheet_id,
                    "reason": f"Google 已授權可讀但不允許直接匯出（HTTP {response.status_code}）",
                }
            )
            continue
        path.write_bytes(response.content)
        audit["downloaded"] += 1
        workbook = load_workbook(path, data_only=True, read_only=True)
        sheet = workbook["月合約資料"]
        rows = sheet.iter_rows(values_only=True)
        indexes = first_header_indexes(next(rows))
        for row_number, row in enumerate(rows, start=2):
            room = as_text(value(row, indexes, "房號"))
            if not room:
                continue
            property_name = supplementary_property_for(sheet_id, room)
            if not property_name:
                audit["skipped_rows"].append({"source": sheet_id, "row": row_number, "reason": "無法辨識物件"})
                continue
            facts[(property_name, room)] = {
                "start_date": parse_date(value(row, indexes, "起租")),
                "end_date": parse_date(value(row, indexes, "到約")),
                "deposit": as_money(value(row, indexes, "押金")),
                "meter_start": as_text(value(row, indexes, "起始電度")),
                "source": sheet_id,
                "row": row_number,
            }
            audit["matched_facts"] += 1
    return facts, audit


def collect_rows(source_path: Path, months=MONTHS):
    workbook = load_workbook(source_path, data_only=True, read_only=True)
    records = []
    audit = {"source_rows": {}, "skipped_rows": [], "inferred_contract_dates": []}

    for year_month in months:
        sheet = workbook[year_month]
        rows = sheet.iter_rows(values_only=True)
        headers = next(rows)
        indexes = first_header_indexes(headers)
        count = 0
        for row_number, row in enumerate(rows, start=2):
            property_name = as_text(value(row, indexes, "地點"))
            room_number = as_text(value(row, indexes, "房號"))
            if not property_name and not room_number:
                continue
            count += 1
            if not property_name or not room_number:
                audit["skipped_rows"].append(
                    {"sheet": year_month, "row": row_number, "reason": "缺少地點或房號"}
                )
                continue
            records.append(
                {
                    "sheet": year_month,
                    "row": row_number,
                    "landlord": as_text(value(row, indexes, "屋主")) or "未指定屋主",
                    "property": property_name,
                    "room": room_number,
                    "tenant": as_text(value(row, indexes, "姓名")),
                    "phone": as_text(value(row, indexes, "電話")),
                    "start_date": parse_date(value(row, indexes, "起租")),
                    "end_date": parse_date(value(row, indexes, "到約")),
                    "rent": as_money(value(row, indexes, "租金")),
                    "electricity": as_money(value(row, indexes, "電費")),
                    "water": as_money(value(row, indexes, "水費")),
                    "management": as_money(value(row, indexes, "管理費")),
                    "other": as_money(value(row, indexes, "其他")),
                    "previous_balance": as_money(value(row, indexes, "未收款")),
                    "due": as_money(value(row, indexes, "應繳")),
                    "paid_amount": as_money(value(row, indexes, "已繳")),
                    "transfer_date": parse_date(value(row, indexes, "入帳時間")),
                }
            )
        audit["source_rows"][year_month] = count
    return records, audit


def month_start(year_month: str) -> date:
    return date(int(year_month[:4]), int(year_month[4:]), 1)


def build_database(records, output_path: Path, audit: dict, supplementary_facts: dict, latest_month: str):
    os.environ["DATABASE_URL"] = f"sqlite:///{output_path.as_posix()}"
    from app.core.app_factory.factory import create_app
    from app.core.db.extensions import db
    from app.models.billing import MonthlyBill
    from app.models.parties import Contract, Landlord, Property, Room, Tenant

    app = create_app()
    with app.app_context():
        db.create_all()

        landlords, properties, rooms, tenants, contracts = {}, {}, {}, {}, {}
        records_by_room = defaultdict(list)
        for record in records:
            records_by_room[(record["property"], record["room"])].append(record)

        for (property_name, room_number), room_records in records_by_room.items():
            newest = max(room_records, key=lambda item: item["sheet"])
            landlord = landlords.get(newest["landlord"])
            if landlord is None:
                landlord = Landlord(name=newest["landlord"])
                db.session.add(landlord)
                db.session.flush()
                landlords[newest["landlord"]] = landlord

            property_model = properties.get(property_name)
            if property_model is None:
                property_model = Property(
                    landlord_id=landlord.id,
                    name=property_name,
                    address=property_name,
                    billing_rule="google_source_rebuild",
                )
                db.session.add(property_model)
                db.session.flush()
                properties[property_name] = property_model

            newest_status = is_room_status_label(newest["tenant"])
            room_model = Room(
                property_id=property_model.id,
                room_number=room_number,
                rent=newest["rent"],
                status=newest_status or "occupied",
                notes="來源：Google 月份工作表重建",
            )
            db.session.add(room_model)
            db.session.flush()
            rooms[(property_name, room_number)] = room_model

            for record in sorted(room_records, key=lambda item: item["sheet"]):
                status = is_room_status_label(record["tenant"])
                closeout = CLOSEOUT_ASSIGNMENTS.get((record["sheet"], property_name, room_number))
                if status or not record["tenant"]:
                    if closeout:
                        record = {**record, "tenant": closeout["tenant"], "phone": closeout["phone"]}
                    else:
                        ignored_key = (record["sheet"], property_name, room_number)
                        if (property_name in IGNORED_NON_TENANT_PROPERTIES or ignored_key in IGNORED_NON_TENANT_CHARGES) and record["due"]:
                            audit.setdefault("ignored_non_tenant_charges", []).append(
                                {
                                    "sheet": record["sheet"], "row": record["row"], "property": property_name,
                                    "room": room_number, "amount": str(record["due"]),
                                    "reason": "使用者確認：空房維修／額外電費，不列租客帳或待決定項目",
                                }
                            )
                            continue
                        if record["due"]:
                            audit.setdefault("unassigned_closeouts", []).append(
                                {
                                    "sheet": record["sheet"], "row": record["row"], "property": property_name,
                                    "room": room_number, "amount": str(record["due"]), "room_status": status or "unknown",
                                }
                            )
                        continue

                tenant_key = (record["tenant"], record["phone"])
                tenant = tenants.get(tenant_key)
                if tenant is None:
                    tenant = Tenant(name=record["tenant"], phone=record["phone"] or None)
                    db.session.add(tenant)
                    db.session.flush()
                    tenants[tenant_key] = tenant

                contract_key = (property_name, room_number, tenant_key)
                contract = contracts.get(contract_key)
                supplement = supplementary_facts.get((property_name, room_number), {})
                start = record["start_date"] or supplement.get("start_date") or month_start(record["sheet"])
                end = record["end_date"] or supplement.get("end_date") or date(2099, 12, 31)
                if record["start_date"] is None or record["end_date"] is None:
                    audit["inferred_contract_dates"].append(
                        {"sheet": record["sheet"], "row": record["row"], "property": property_name, "room": room_number}
                    )
                if contract is None:
                    contract = Contract(
                        tenant_id=tenant.id,
                        room_id=room_model.id,
                        start_date=start,
                        end_date=end,
                        rent=record["rent"],
                        status="active" if record["sheet"] == latest_month else "ended",
                        notes="來源：Google 月份工作表重建；日期空值已標記於稽核檔。",
                    )
                    db.session.add(contract)
                    db.session.flush()
                    contracts[contract_key] = contract
                else:
                    contract.start_date = min(contract.start_date, start)
                    contract.end_date = max(contract.end_date, end)
                    if record["sheet"] == latest_month:
                        contract.status = "active"

                paid = record["due"] > 0 and record["paid_amount"] >= record["due"]
                other_charges = record["management"] + record["other"]
                calculated = MonthlyBill.calculate_total(
                    rent=record["rent"],
                    electricity_amount=record["electricity"],
                    water_amount=record["water"],
                    other_charges=other_charges,
                    previous_balance=record["previous_balance"],
                )
                if calculated != record["due"]:
                    source_adjustment = record["due"] - calculated
                    other_charges += source_adjustment
                    audit.setdefault("source_total_differences", []).append(
                        {
                            "sheet": record["sheet"],
                            "row": record["row"],
                            "source_due": str(record["due"]),
                            "calculated_before_source_adjustment": str(calculated),
                            "source_adjustment": str(source_adjustment),
                        }
                    )
                db.session.add(
                    MonthlyBill(
                        contract_id=contract.id,
                        year_month=record["sheet"],
                        rent=record["rent"],
                        electricity_amount=record["electricity"],
                        water_amount=record["water"],
                        other_charges=other_charges,
                        other_desc="管理費、其他費用與來源總額調整（Google 來源）",
                        previous_balance=record["previous_balance"],
                        total=record["due"],
                        paid=paid,
                        paid_date=record["transfer_date"] if paid else None,
                        notes="Google 月份來源；保留來源應繳總額。",
                    )
                )

        db.session.commit()
        audit["created"] = {
            "landlords": len(landlords),
            "properties": len(properties),
            "rooms": len(rooms),
            "tenants": len(tenants),
            "contracts": len(contracts),
            "monthly_bills": MonthlyBill.query.count(),
        }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--through", choices=MONTHS, default=MONTHS[-1], help="latest month to include")
    args = parser.parse_args()
    output_path = args.output.resolve()
    if output_path.exists():
        raise SystemExit(f"Refusing to overwrite existing file: {output_path}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    source_path = output_path.parent / "google-monthly-source-202604-202607.xlsx"
    download_source(source_path)
    active_months = MONTHS[: MONTHS.index(args.through) + 1]
    records, audit = collect_rows(source_path, active_months)
    supplementary_facts, supplementary_audit = collect_supplementary_contracts(
        output_path.parent / "google-property-sources-202607"
    )
    audit["supplementary_sources"] = supplementary_audit
    build_database(records, output_path, audit, supplementary_facts, args.through)
    audit_path = output_path.with_suffix(".audit.json")
    audit_path.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"database": str(output_path), "audit": str(audit_path), **audit["created"]}, ensure_ascii=False))


if __name__ == "__main__":
    main()
