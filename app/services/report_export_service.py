from __future__ import annotations

from dataclasses import dataclass

from app.core.errors import DomainValidationError
from app.integrations import create_sheets_client

EXPORT_CONTENT_TYPES = {
    "csv": "text/csv; charset=utf-8",
    "xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
}


@dataclass
class ReportExportPayload:
    content: bytes
    content_type: str
    filename: str


class ReportExportService:
    @staticmethod
    def export_rows(*, rows: list[dict], headers: list[str], filename_base: str, export_format: str) -> ReportExportPayload:
        normalized = (export_format or "csv").strip().lower()
        if normalized not in EXPORT_CONTENT_TYPES:
            raise DomainValidationError("不支援的匯出格式", details={"format": ["僅支援 csv 或 xlsx"]})
        client = create_sheets_client(normalized)
        content = client.export_report(rows, headers)
        return ReportExportPayload(
            content=content,
            content_type=EXPORT_CONTENT_TYPES[normalized],
            filename=f"{filename_base}.{normalized}",
        )
