from typing import Protocol


class SheetsClientProtocol(Protocol):
    def export_report(self, data: list[dict]) -> bytes:
        """Return export payload for report data."""
