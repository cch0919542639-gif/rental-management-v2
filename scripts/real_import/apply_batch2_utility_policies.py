"""Apply approved Batch 2 utility policies to an already imported target database.

Default mode is read-only.  The script intentionally knows only the eight
properties approved in ``open-batch2-resolver-candidates-01.md``.  It refuses
to overwrite a conflicting policy value, so an operator must investigate any
unexpected configuration before making a write.

Usage:
    py -3 .\scripts\real_import\apply_batch2_utility_policies.py \
        --database-url sqlite:///D:\CodexRuntime\rental\rebuild\runtime-real.db
    py -3 .\scripts\real_import\apply_batch2_utility_policies.py \
        --database-url sqlite:///D:\CodexRuntime\rental\rebuild\runtime-real.db --execute

Rollback:
    Restore the database backup made before the Batch 2 execute operation, or
    explicitly clear the two policy columns after reviewing the evidence.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from sqlalchemy import create_engine, inspect, text


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_DATABASE_URL = f"sqlite:///{PROJECT_ROOT / 'runtime-real.db'}"

# Only properties that Open classified as resolver-ready are included here.
BATCH2_POLICIES = {
    1: ("electricity_bill_usage_ratio", "water_bill_by_stay_days"),
    2: ("electricity_bill_usage_ratio", "water_bill_by_stay_days"),
    3: ("electricity_bill_usage_ratio", "water_bill_by_stay_days"),
    4: ("electricity_bill_usage_ratio", "water_bill_by_stay_days"),
    5: ("electricity_bill_usage_ratio_plus_public_share", "water_bill_by_stay_days"),
    6: ("electricity_bill_usage_ratio", "water_bill_by_stay_days"),
    21: ("electricity_bill_usage_ratio", "water_free"),
    22: ("electricity_fixed_rate", "water_bill_by_stay_days"),
}


def _build_parser():
    parser = argparse.ArgumentParser(description="Dry-run-first Batch 2 utility policy assignment")
    parser.add_argument("--database-url", default=DEFAULT_DATABASE_URL, help="Target database URL")
    parser.add_argument("--execute", action="store_true", help="Write approved policy codes")
    return parser


def _validate_target(engine):
    inspector = inspect(engine)
    if not inspector.has_table("properties"):
        raise RuntimeError("Target database has no properties table. Prepare and import the target first.")
    columns = {column["name"] for column in inspector.get_columns("properties")}
    required = {"id", "name", "electricity_policy_code", "water_policy_code"}
    missing = required - columns
    if missing:
        raise RuntimeError(f"Target properties table is missing required columns: {', '.join(sorted(missing))}")


def _load_candidates(conn):
    rows = conn.execute(
        text(
            "SELECT id, name, electricity_policy_code, water_policy_code "
            "FROM properties WHERE id IN (%s) ORDER BY id" % ", ".join(str(item) for item in BATCH2_POLICIES)
        )
    ).mappings().all()
    by_id = {row["id"]: row for row in rows}
    missing = sorted(set(BATCH2_POLICIES) - set(by_id))
    if missing:
        raise RuntimeError(
            "Batch 2 target data is incomplete. Missing approved property IDs: "
            + ", ".join(str(item) for item in missing)
        )
    return by_id


def main(argv: list[str]) -> int:
    args = _build_parser().parse_args(argv)
    engine = create_engine(args.database_url)
    _validate_target(engine)
    mode = "EXECUTE" if args.execute else "DRY-RUN"

    print("=" * 72)
    print(f"Batch 2 Utility Policy Assignment ({mode})")
    print("=" * 72)
    print(f"Target: {args.database_url}")
    print(f"Approved properties: {len(BATCH2_POLICIES)}")
    print("Rollback note: restore the pre-execute backup if policy assignment is incorrect.")

    with engine.begin() as conn:
        candidates = _load_candidates(conn)
        updates = []
        conflicts = []
        for property_id, (electricity_policy, water_policy) in BATCH2_POLICIES.items():
            row = candidates[property_id]
            existing = (row["electricity_policy_code"], row["water_policy_code"])
            desired = (electricity_policy, water_policy)
            if existing == desired:
                outcome = "already configured"
            elif existing == (None, None):
                outcome = "would configure"
                updates.append((property_id, electricity_policy, water_policy))
            else:
                outcome = "CONFLICT"
                conflicts.append((property_id, existing, desired))
            print(
                f"  property_id={property_id} name={row['name']} "
                f"electricity={electricity_policy} water={water_policy} [{outcome}]"
            )

        if conflicts:
            print("-" * 72)
            print("STOP: Existing policy values conflict with the approved Batch 2 map.")
            for property_id, existing, desired in conflicts:
                print(f"  property_id={property_id}: existing={existing}, approved={desired}")
            return 1

        if args.execute:
            for property_id, electricity_policy, water_policy in updates:
                conn.execute(
                    text(
                        "UPDATE properties SET electricity_policy_code = :electricity_policy, "
                        "water_policy_code = :water_policy WHERE id = :property_id"
                    ),
                    {
                        "property_id": property_id,
                        "electricity_policy": electricity_policy,
                        "water_policy": water_policy,
                    },
                )
            print("-" * 72)
            print(f"Configured count: {len(updates)}")
        else:
            print("-" * 72)
            print(f"Candidate count: {len(updates)}")
            print("Dry-run only. Re-run with --execute after Batch 2 import parity passes.")

    print("=" * 72)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
