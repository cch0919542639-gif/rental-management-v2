"""Run the approved move-out rehearsal against the designated backup only."""
from __future__ import annotations

import csv
import hashlib
import sqlite3
from pathlib import Path


ROOT = Path(r"D:\CodexRuntime\rental\rebuild-main")
BACKUP = ROOT / "backups" / "runtime_20260719_143424.db"
REAL = ROOT / "runtime-real.db"
CSV_PATH = ROOT / "evidence" / "move-out-settlement-rehearsal-20260719.csv"
EXPECTED_BACKUP_SHA256 = "260489f6a5d112c9c99e9865e190a05a0a5d1c5a63c0ff7bdc7cc18cb6d28b31"


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def one(cursor: sqlite3.Cursor, query: str, params: tuple) -> sqlite3.Row:
    rows = cursor.execute(query, params).fetchall()
    if len(rows) != 1:
        raise RuntimeError(f"Expected exactly one row; got {len(rows)} for {params!r}")
    return rows[0]


def insert_settlement(cursor: sqlite3.Cursor, *, contract_id: int, move_out_date: str,
                      final_rent: int = 0, electricity: int = 0, water: int = 0,
                      previous_debt: int = 0) -> int:
    deposit = one(cursor, "SELECT deposit FROM contracts WHERE id = ?", (contract_id,))[0]
    if deposit is None:
        raise RuntimeError(f"Contract {contract_id} has no deposit")
    cursor.execute(
        """INSERT INTO move_out_settlements
           (contract_id, move_out_date, final_rent, electricity_amount, water_amount,
            previous_debt, deposit_held, refund_amount, status, notes)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'draft', ?)""",
        (contract_id, move_out_date, final_rent, electricity, water, previous_debt,
         deposit, deposit, "2026-07-19 rehearsal: draft only; pending independent manual review."),
    )
    return cursor.lastrowid


def main() -> None:
    if not BACKUP.is_file() or sha256(BACKUP) != EXPECTED_BACKUP_SHA256:
        raise RuntimeError("Backup is missing or no longer matches the approved pre-write baseline")
    real_before = sha256(REAL)

    con = sqlite3.connect(BACKUP)
    con.row_factory = sqlite3.Row
    try:
        cur = con.cursor()
        if cur.execute("SELECT COUNT(*) FROM move_out_settlements").fetchone()[0]:
            raise RuntimeError("Rehearsal settlements already exist; refusing to duplicate them")
        if cur.execute("SELECT COUNT(*) FROM payment_records").fetchone()[0] != 175:
            raise RuntimeError("Unexpected PaymentRecord baseline")

        # Supplemental migration, using the user-confirmed composite identifiers.
        pan_landlord = one(cur, "SELECT id FROM landlords WHERE name = ?", ("郭麗娥",))[0]
        cur.execute("INSERT INTO properties (landlord_id, name, address, total_rooms) VALUES (?, ?, ?, ?)",
                    (pan_landlord, "自強27巷36號", "自強27巷36號", 1))
        pan_property = cur.lastrowid
        cur.execute("INSERT INTO rooms (property_id, room_number, rent, deposit, status, notes) VALUES (?, ?, ?, ?, ?, ?)",
                    (pan_property, "13", 4750, 9500, "available", "Supplemental rehearsal migration; contract ended"))
        pan_room = cur.lastrowid
        cur.execute("INSERT INTO tenants (name, phone, notes) VALUES (?, ?, ?)",
                    ("潘文宏", "0917182431", "Supplemental rehearsal migration 2026-07-19"))
        pan_tenant = cur.lastrowid
        cur.execute("""INSERT INTO contracts
                       (tenant_id, room_id, start_date, end_date, rent, deposit, status, notes)
                       VALUES (?, ?, ?, ?, ?, ?, 'ended', ?)""",
                    (pan_tenant, pan_room, "2025-04-26", "2026-04-24", 4750, 9500,
                     "Supplemental rehearsal migration; user-confirmed composite match"))
        pan_contract = cur.lastrowid

        cur.execute("INSERT INTO landlords (name, notes) VALUES (?, ?)",
                    ("黃采玲", "Supplemental rehearsal migration 2026-07-19; source import owner"))
        ke_landlord = cur.lastrowid
        cur.execute("INSERT INTO properties (landlord_id, name, address, total_rooms) VALUES (?, ?, ?, ?)",
                    (ke_landlord, "昌裕71巷", "昌裕71巷", 1))
        ke_property = cur.lastrowid
        cur.execute("INSERT INTO rooms (property_id, room_number, rent, deposit, status, notes) VALUES (?, ?, ?, ?, ?, ?)",
                    (ke_property, "3A", 6500, 13000, "available", "Supplemental rehearsal migration; contract ended"))
        ke_room = cur.lastrowid
        cur.execute("INSERT INTO tenants (name, phone, notes) VALUES (?, ?, ?)",
                    ("柯明寰", "0988290693", "Supplemental rehearsal migration 2026-07-19"))
        ke_tenant = cur.lastrowid
        cur.execute("""INSERT INTO contracts
                       (tenant_id, room_id, start_date, end_date, rent, deposit, status, notes)
                       VALUES (?, ?, ?, ?, ?, ?, 'ended', ?)""",
                    (ke_tenant, ke_room, "2025-06-01", "2026-05-31", 6500, 13000,
                     "Supplemental rehearsal migration; user-confirmed composite match"))
        ke_contract = cur.lastrowid

        # User-authorized migration corrections needed for refund validation.
        cur.execute("UPDATE contracts SET rent = ?, deposit = ? WHERE id = ?", (5000, 10000, 81))
        cur.execute("UPDATE contracts SET deposit = ? WHERE id = ?", (12000, 85))
        cur.execute("UPDATE contracts SET deposit = ? WHERE id = ?", (11600, 173))
        if cur.rowcount != 1:
            raise RuntimeError("Contract 173 migration correction failed")

        settlements = [
            ("潘文宏", insert_settlement(cur, contract_id=pan_contract, move_out_date="2026-04-24", electricity=678, water=328), 1006, 8494),
            ("柯明寰", insert_settlement(cur, contract_id=ke_contract, move_out_date="2026-05-31", electricity=1010), 1010, 11990),
            ("何佾洋", insert_settlement(cur, contract_id=81, move_out_date="2026-05-05", final_rent=5000, previous_debt=5000), 10000, 0),
            ("陳雅鈴", insert_settlement(cur, contract_id=85, move_out_date="2026-05-28", electricity=880), 880, 11120),
            ("陳夢翰", insert_settlement(cur, contract_id=173, move_out_date="2026-05-24", electricity=41, water=176), 217, 11383),
        ]
        con.commit()

        rows = []
        for tenant, settlement_id, proposed_allocation, proposed_refund in settlements:
            s = one(cur, """SELECT s.*, c.deposit AS contract_deposit FROM move_out_settlements s
                           JOIN contracts c ON c.id=s.contract_id WHERE s.id = ?""", (settlement_id,))
            gross = sum(s[field] for field in ("final_rent", "electricity_amount", "water_amount", "management_fee", "previous_debt", "cleaning_fee", "repair_fee", "other_charge"))
            rows.append({
                "tenant_name": tenant, "settlement_id": settlement_id, "contract_id": s["contract_id"],
                "move_out_date": s["move_out_date"], "status": s["status"],
                "contract_deposit": s["contract_deposit"], "full_refund": s["refund_amount"],
                "final_rent": s["final_rent"], "electricity": s["electricity_amount"], "water": s["water_amount"],
                "previous_debt": s["previous_debt"], "charges_total": gross,
                "reviewer_proposed_refund_allocation": proposed_allocation,
                "reviewer_proposed_cash_refund": proposed_refund,
                "refund_formula_ok": s["refund_amount"] == proposed_allocation + proposed_refund,
                "charges_formula_ok": gross == proposed_allocation,
                "reviewer_name": "", "evidence_type": "", "evidence_reference": "",
            })
        with CSV_PATH.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=rows[0].keys())
            writer.writeheader()
            writer.writerows(rows)
    finally:
        con.close()

    if sha256(REAL) != real_before:
        raise RuntimeError("Formal database changed unexpectedly")


if __name__ == "__main__":
    main()
