from __future__ import annotations

from io import BytesIO, StringIO
import csv
from typing import Protocol

from openpyxl import Workbook


class SheetsClientProtocol(Protocol):
    def export_report(self, rows: list[dict], headers: list[str]) -> bytes:
        """Return spreadsheet-compatible export payload."""


class CSVSheetsClient:
    def export_report(self, rows: list[dict], headers: list[str]) -> bytes:
        buffer = StringIO()
        writer = csv.DictWriter(buffer, fieldnames=headers)
        writer.writeheader()
        for row in rows:
            writer.writerow({header: row.get(header) for header in headers})
        return buffer.getvalue().encode("utf-8-sig")


class XLSXSheetsClient:
    def export_report(self, rows: list[dict], headers: list[str]) -> bytes:
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = "report"
        worksheet.append(headers)
        for row in rows:
            worksheet.append([row.get(header) for header in headers])
        output = BytesIO()
        workbook.save(output)
        return output.getvalue()


def create_sheets_client(export_format: str) -> SheetsClientProtocol:
    normalized = (export_format or "csv").strip().lower()
    if normalized == "xlsx":
        return XLSXSheetsClient()
    return CSVSheetsClient()
