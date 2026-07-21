"""Create row-level human review data for the Google-source staging rebuild."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from datetime import date
from pathlib import Path

from rebuild_google_staging_db import MONTHS, as_money, collect_rows


def iso(value):
    return value.isoformat() if isinstance(value, date) else ""


def base(record):
    return {
        "月份": record["sheet"],
        "來源列": record["row"],
        "屋主": record["landlord"],
        "地點": record["property"],
        "房號": record["room"],
        "房客姓名": record["tenant"],
        "電話": record["phone"],
        "起租日": iso(record["start_date"]),
        "到約日": iso(record["end_date"]),
        "租金": float(record["rent"]),
        "電費": float(record["electricity"]),
        "水費": float(record["water"]),
        "管理費": float(record["management"]),
        "其他": float(record["other"]),
        "未收款": float(record["previous_balance"]),
        "應繳": float(record["due"]),
        "已繳": float(record["paid_amount"]),
        "入帳日": iso(record["transfer_date"]),
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    records, _ = collect_rows(args.source)
    records_by_room = defaultdict(list)
    for record in records:
        records_by_room[(record["property"], record["room"])].append(record)

    vacant_closeout, date_review, total_difference, all_review = [], [], [], []
    for room_records in records_by_room.values():
        prior_tenant = ""
        prior_month = ""
        for record in sorted(room_records, key=lambda item: MONTHS.index(item["sheet"])):
            if not record["tenant"] and record["due"] != 0:
                row = base(record)
                row.update(
                    {
                        "前一期房客": prior_tenant or "來源表前期未提供",
                        "前一期月份": prior_month or "",
                        "審查重點": "退租後帳單／入帳：確認前一期房客與結清歸屬。",
                        "建議處理": "確認後建立或補正退租結清，不視為空房帳單錯誤。",
                        "人工決定": "待確認",
                    }
                )
                vacant_closeout.append(row)
                all_review.append({"類型": "退租後結清", **row})

            if record["tenant"] and (record["start_date"] is None or record["end_date"] is None):
                missing = "、".join(
                    field
                    for field, value in (("起租日", record["start_date"]), ("到約日", record["end_date"]))
                    if value is None
                )
                row = base(record)
                row.update(
                    {
                        "缺少欄位": missing,
                        "審查重點": "目前隔離庫以月份起日／2099-12-31暫代；請填入實際租約日期。",
                        "人工決定": "待確認",
                    }
                )
                date_review.append(row)
                all_review.append({"類型": "租約日期", **row})

            calculated = (
                record["rent"]
                + record["electricity"]
                + record["water"]
                + record["management"]
                + record["other"]
                + record["previous_balance"]
            )
            if record["tenant"] and calculated != record["due"]:
                row = base(record)
                row.update(
                    {
                        "欄位加總": float(calculated),
                        "差額": float(record["due"] - calculated),
                        "審查重點": "來源應繳與可見費用欄位加總不同；可能含公共電費、調整款或公式項目。",
                        "人工決定": "待確認",
                    }
                )
                total_difference.append(row)
                all_review.append({"類型": "金額差異", **row})

            if record["tenant"]:
                prior_tenant = record["tenant"]
                prior_month = record["sheet"]

    output = {
        "summary": {
            "source_months": list(MONTHS),
            "vacant_closeout_rows": len(vacant_closeout),
            "date_review_rows": len(date_review),
            "total_difference_rows": len(total_difference),
            "all_review_rows": len(all_review),
        },
        "vacant_closeout": vacant_closeout,
        "date_review": date_review,
        "total_difference": total_difference,
        "all_review": all_review,
    }
    args.output.write_text(json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(output["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
