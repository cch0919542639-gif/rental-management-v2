"""Apply independently reviewed allocations to the approved backup rehearsal only."""
from __future__ import annotations

import csv
import hashlib
import sqlite3
from pathlib import Path


ROOT = Path(r"D:\CodexRuntime\rental\rebuild-main")
BACKUP = ROOT / "backups" / "runtime_20260719_143424.db"
REAL = ROOT / "runtime-real.db"
REVIEW = Path(r"C:\Users\v1728\Downloads\退租結清覆核結果_20260719 (1).csv")
EXPECTED_BACKUP_SHA256 = "954391c6c25eae941a5825caa651e4c4670838247ecb09f4bc42d9c337361040"


def digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def as_int(value: str) -> int:
    return int(value.strip())


def main() -> None:
    if digest(BACKUP) != EXPECTED_BACKUP_SHA256:
        raise RuntimeError("Backup changed after the reviewed-draft baseline; refusing to settle")
    real_before = digest(REAL)
    with REVIEW.open(encoding="utf-8-sig", newline="") as f:
        reviewed = {row["tenant_name"]: row for row in csv.DictReader(f)}
    expected = {"潘文宏", "柯明寰", "何佾洋", "陳雅鈴", "陳夢翰"}
    if set(reviewed) != expected:
        raise RuntimeError("Reviewed CSV does not contain exactly the five approved tenants")
    for name, row in reviewed.items():
        if row["review_result"] != "已覆核—可進入分攤" or not row["reviewer_name"].strip():
            raise RuntimeError(f"{name} is not independently approved")
        if as_int(row["deposit_and_full_refund"]) != as_int(row["proposed_refund_allocation"]) + as_int(row["proposed_cash_refund"]):
            raise RuntimeError(f"{name} refund formula failed")
        if as_int(row["charges_total"]) != as_int(row["proposed_refund_allocation"]):
            raise RuntimeError(f"{name} charge formula failed")

    con = sqlite3.connect(BACKUP)
    con.row_factory = sqlite3.Row
    try:
        cur = con.cursor()
        if cur.execute("SELECT COUNT(*) FROM payment_records").fetchone()[0] != 175:
            raise RuntimeError("Unexpected PaymentRecord baseline")
        if cur.execute("SELECT COUNT(*) FROM move_out_settlement_allocations").fetchone()[0] != 0:
            raise RuntimeError("Allocations already exist; refusing to duplicate them")
        settlement_rows = cur.execute("""SELECT s.*, t.name FROM move_out_settlements s
                                       JOIN contracts c ON c.id=s.contract_id
                                       JOIN tenants t ON t.id=c.tenant_id
                                       WHERE s.status='draft'""").fetchall()
        if len(settlement_rows) != 5 or {r["name"] for r in settlement_rows} != expected:
            raise RuntimeError("Expected five approved draft settlements")
        for settlement in settlement_rows:
            name = settlement["name"]
            row = reviewed[name]
            charge_fields = {
                "final_rent": settlement["final_rent"],
                "electricity_amount": settlement["electricity_amount"],
                "water_amount": settlement["water_amount"],
                "management_fee": settlement["management_fee"],
                "previous_debt": settlement["previous_debt"],
                "cleaning_fee": settlement["cleaning_fee"],
                "repair_fee": settlement["repair_fee"],
                "other_charge": settlement["other_charge"],
            }
            total = sum(int(value or 0) for value in charge_fields.values())
            if total != as_int(row["charges_total"]):
                raise RuntimeError(f"{name} database charges no longer match review CSV")
            allocation_total = 0
            for charge_type, amount in charge_fields.items():
                if amount:
                    cur.execute("""INSERT INTO move_out_settlement_allocations
                                   (settlement_id, charge_type, amount, confirmed_by_id)
                                   VALUES (?, ?, ?, NULL)""", (settlement["id"], charge_type, amount))
                    allocation_total += int(amount)
            if allocation_total != as_int(row["proposed_refund_allocation"]):
                raise RuntimeError(f"{name} allocation mismatch")
            note = (settlement["notes"] or "") + (
                f" Independent manual review: {row['reviewer_name']}; "
                f"review source: {REVIEW.name}; evidence type: {row['evidence_type'] or 'none'}."
            )
            cur.execute("""UPDATE move_out_settlements
                           SET status='settled', settled_at=CURRENT_TIMESTAMP,
                               evidence_type=?, evidence_reference=?, notes=?, updated_at=CURRENT_TIMESTAMP
                           WHERE id=? AND status='draft'""",
                        (row["evidence_type"] or None, row["evidence_reference"] or None, note, settlement["id"]))
            if cur.rowcount != 1:
                raise RuntimeError(f"{name} was not a draft at settlement time")
        con.commit()
    finally:
        con.close()
    if digest(REAL) != real_before:
        raise RuntimeError("Formal database changed unexpectedly")


if __name__ == "__main__":
    main()
