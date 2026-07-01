"""
Dry-run-first evidence bundle writer for Phase 5 bridge drills.

Purpose:
  - Summarize rehearsal artifacts (manifest, parity log, checklist log)
  - Preview a standardized JSON evidence record
  - Optionally write that evidence bundle to disk for later audit

Rollback:
  - Delete the generated evidence JSON file if it should be discarded.
  - This script never modifies any database state.

Verification:
  - Run without --execute first and confirm the summary matches the supplied artifacts.
  - After --execute, confirm the JSON file exists and contains the expected label and paths.
"""

from __future__ import annotations

import argparse
from datetime import datetime
import json
from pathlib import Path


def _build_parser():
    parser = argparse.ArgumentParser(description="Dry-run-first evidence bundle writer for bridge drills.")
    parser.add_argument("--label", required=True, help="Short evidence label, e.g. rehearsal-01")
    parser.add_argument("--manifest", required=True, help="Path to manifest.json")
    parser.add_argument("--parity-log", help="Path to a saved verify_row_parity output log")
    parser.add_argument("--checklist-log", help="Path to a saved bridge_drill_checklist output log")
    parser.add_argument("--output-dir", default="migration_evidence", help="Directory for evidence JSON bundles")
    parser.add_argument("--execute", action="store_true", help="Actually write the evidence JSON file")
    return parser


def _read_text_if_exists(path_value: str | None):
    if not path_value:
        return None, None
    path = Path(path_value)
    if not path.exists():
        raise SystemExit(f"Artifact not found: {path}")
    return path, path.read_text(encoding="utf-8")


def main():
    args = _build_parser().parse_args()
    manifest_path = Path(args.manifest)
    if not manifest_path.exists():
        raise SystemExit(f"Manifest not found: {manifest_path}")

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    parity_path, parity_text = _read_text_if_exists(args.parity_log)
    checklist_path, checklist_text = _read_text_if_exists(args.checklist_log)

    evidence = {
        "label": args.label,
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "manifest_path": str(manifest_path.resolve()),
        "manifest_table_count": len(manifest.get("tables", [])),
        "manifest_total_rows": sum(item.get("row_count", 0) for item in manifest.get("tables", [])),
        "parity_log_path": str(parity_path.resolve()) if parity_path else None,
        "parity_pass": "Result : PASS" in parity_text if parity_text else None,
        "checklist_log_path": str(checklist_path.resolve()) if checklist_path else None,
        "checklist_has_fail": "[FAIL]" in checklist_text if checklist_text else None,
    }

    print("=" * 72)
    print("Phase 5 Rehearsal Evidence")
    print("=" * 72)
    print(json.dumps(evidence, indent=2, ensure_ascii=False))
    print("-" * 72)

    if not args.execute:
        print("Dry-run only. Re-run with --execute to write the evidence JSON file.")
        print("=" * 72)
        return

    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{args.label}.json"
    output_path.write_text(json.dumps(evidence, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Wrote evidence bundle: {output_path.resolve()}")
    print("=" * 72)


if __name__ == "__main__":
    main()
