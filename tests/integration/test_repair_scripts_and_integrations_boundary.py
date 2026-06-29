from pathlib import Path
import subprocess
import sys


def _run_script(script_path: Path):
    return subprocess.run(
        [sys.executable, str(script_path)],
        capture_output=True,
        text=True,
        cwd=script_path.parents[2],
        check=True,
    )


def test_repair_scripts_run_read_only():
    root = Path(__file__).resolve().parents[2]
    scripts = [
        root / "scripts" / "repair" / "year_month_audit.py",
        root / "scripts" / "repair" / "room_status_audit.py",
        root / "scripts" / "repair" / "user_table_audit.py",
        root / "scripts" / "repair" / "contract_expiry_repair.py",
    ]
    for script in scripts:
        result = _run_script(script)
        assert result.returncode == 0
        assert result.stdout.strip()


def test_line_webhook_placeholder_returns_501(client, logged_in_client):
    response = client.post("/integrations/line/callback")
    assert response.status_code == 501
    payload = response.get_json()
    assert payload["error"] == "not_implemented"


def test_payment_list_shows_ocr_section_when_present(app, logged_in_client, seeded_data):
    client = logged_in_client
    response = client.post(
        "/payments/create",
        data={
            "contract_id": seeded_data["contract_id"],
            "monthly_bill_id": seeded_data["monthly_bill_id"],
            "amount": "12000",
            "bank_name": "Bank A",
            "account_number": "123456",
            "account_holder": "Tenant One",
            "transaction_date": "2026-06-05",
            "payer_name": "Tenant One",
            "transaction_id": "TXN-OCR-001",
            "status_text": "匯款成功",
            "raw_ocr_text": "OCR TEXT",
            "raw_llm_response": "{\"amount\":12000}",
            "image_path": "uploads/payment-001.jpg",
            "ocr_engine": "placeholder",
            "notes": "ocr evidence test",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "OCR 資訊" in text
    assert "uploads/payment-001.jpg" in text
