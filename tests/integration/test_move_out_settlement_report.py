from datetime import date
from decimal import Decimal

from app.core.db import db
from app.models import Contract, MoveOutSettlement, User
from app.services import MoveOutSettlementService, ReportService


def _settled_move_out(app, seeded_data):
    with app.app_context():
        settlement = MoveOutSettlementService.create(
            contract=db.session.get(Contract, seeded_data["contract_id"]),
            move_out_date=date(2026, 6, 20),
            final_rent=Decimal("1000"), electricity_amount=Decimal("300"), water_amount=Decimal("200"),
            management_fee=0, previous_debt=0, cleaning_fee=0, repair_fee=0, other_charge=0,
        )
        MoveOutSettlementService.settle(
            settlement, allocations={"final_rent": 1000, "electricity_amount": 300, "water_amount": 200}
        )
        return settlement.id


def test_move_out_settlement_report_and_export_are_scoped_and_do_not_create_payments(app, logged_in_client, seeded_data):
    settlement_id = _settled_move_out(app, seeded_data)

    response = logged_in_client.get(
        f"/reports/move-out-settlements?year_month=2026-06&property_id={seeded_data['property_id']}&status=settled"
    )
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "退租結清明細" in text
    assert "已結算" in text
    assert "不代表已付款或已退款" in text
    assert "24,000" in text
    assert "1,500" in text
    assert "22,500" in text

    export = logged_in_client.get(
        f"/reports/move-out-settlements/export?year_month=2026-06&property_id={seeded_data['property_id']}&status=settled&format=csv"
    )
    assert export.status_code == 200
    assert "suggested_cash_refund" in export.get_data(as_text=True)

    with app.app_context():
        assert MoveOutSettlement.query.get(settlement_id).status == "settled"
        assert db.session.execute(db.text("SELECT COUNT(*) FROM payment_records")).scalar_one() == 0


def test_landlord_report_uses_two_statuses_and_explains_unsettled_rows(app, client, seeded_data):
    with app.app_context():
        draft = MoveOutSettlementService.create(
            contract=db.session.get(Contract, seeded_data["contract_id"]),
            move_out_date=date(2026, 6, 21),
            final_rent=0, electricity_amount=0, water_amount=0, management_fee=0,
            previous_debt=0, cleaning_fee=0, repair_fee=0, other_charge=0,
        )
        landlord_user = User(username="owner", name="Owner", role="landlord", landlord_id=seeded_data["landlord_id"])
        landlord_user.set_password("owner123")
        db.session.add(landlord_user)
        db.session.commit()

        rows = ReportService.move_out_settlements("2026-06", [seeded_data["property_id"]], "unsettled")
        assert [row["settlement_id"] for row in rows] == [draft.id]
        assert rows[0]["landlord_status"] == "未結算"
        assert rows[0]["unsettled_reason"] == "尚待完成結算資料"

    response = client.post("/auth/login", data={"username": "owner", "password": "owner123"}, follow_redirects=True)
    assert response.status_code == 200
    response = client.get(f"/reports/move-out-settlements?year_month=2026-06&property_id={seeded_data['property_id']}&status=unsettled")
    assert response.status_code == 200
    assert "未結算" in response.get_data(as_text=True)
    assert client.get(f"/reports/move-out-settlements?year_month=2026-06&status=draft").status_code == 403
