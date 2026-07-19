from datetime import date
from decimal import Decimal

from app.core.db import db
from app.models import Contract, Landlord, MonthlyBill, PaymentRecord, Property, PropertyExpense, Room, Tenant, User
from app.services import ReportService


def _add_second_property_with_bill(app, seeded_data):
    with app.app_context():
        property_two = Property(
            landlord_id=seeded_data["landlord_id"],
            name="South House",
            address="Kaohsiung City",
            total_rooms=1,
        )
        room_two = Room(property=property_two, room_number="B01", rent=Decimal("9000"), status="occupied")
        tenant_two = Tenant(name="Tenant Two", phone="0988000000")
        db.session.add_all([property_two, room_two, tenant_two])
        db.session.flush()
        contract_two = Contract(
            tenant_id=tenant_two.id,
            room_id=room_two.id,
            start_date=date(2026, 6, 3),
            end_date=date(2027, 6, 2),
            rent=Decimal("9000"),
            deposit=Decimal("18000"),
            status="active",
        )
        db.session.add(contract_two)
        db.session.flush()
        bill_two = MonthlyBill(
            contract_id=contract_two.id,
            year_month="202606",
            rent=Decimal("9000"),
            electricity_amount=Decimal("500"),
            public_electricity=Decimal("100"),
            water_amount=Decimal("200"),
            other_charges=Decimal("0"),
            previous_balance=Decimal("300"),
            total=Decimal("10100"),
            paid=False,
        )
        db.session.add(bill_two)
        db.session.flush()
        db.session.add(
            PaymentRecord(
                contract_id=contract_two.id,
                monthly_bill_id=bill_two.id,
                amount=Decimal("4000"),
                record_status="linked",
                transaction_date=date(2026, 6, 10),
            )
        )
        db.session.commit()
        return {"property_id": property_two.id, "bill_id": bill_two.id}


def _add_property_expenses(app, seeded_data):
    with app.app_context():
        db.session.add_all(
            [
                PropertyExpense(
                    property_id=seeded_data["property_id"],
                    transaction_date=date(2026, 6, 15),
                    category="repair",
                    amount=Decimal("800"),
                    payee="Posted repair vendor",
                    reference_no="POSTED-1",
                    record_status="posted",
                ),
                PropertyExpense(
                    property_id=seeded_data["property_id"],
                    transaction_date=date(2026, 6, 16),
                    category="cleaning",
                    amount=Decimal("900"),
                    payee="Draft vendor",
                    reference_no="DRAFT-1",
                    record_status="draft",
                ),
                PropertyExpense(
                    property_id=seeded_data["property_id"],
                    transaction_date=date(2026, 6, 17),
                    category="utility",
                    amount=Decimal("1000"),
                    payee="Voided vendor",
                    reference_no="VOID-1",
                    record_status="voided",
                ),
            ]
        )
        db.session.commit()


def test_property_collection_filters_and_uses_linked_payment_amount(app, logged_in_client, seeded_data):
    second = _add_second_property_with_bill(app, seeded_data)

    response = logged_in_client.get(
        f"/reports/collection?year_month=2026-06&property_id={second['property_id']}"
    )

    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "物件收租明細" in text
    assert "South House" in text
    assert "Tenant Two" in text
    assert "2026-06-03" in text
    assert "<td>North House</td>" not in text
    assert "10,100" in text
    assert "4,000" in text
    assert "6,100" in text
    assert "position: sticky" in text


def test_property_summary_new_tenants_and_yearly_support_multiple_properties(app, logged_in_client, seeded_data):
    second = _add_second_property_with_bill(app, seeded_data)
    query = f"property_id={seeded_data['property_id']}&property_id={second['property_id']}"

    settlement = logged_in_client.get(f"/reports/property-settlement?year_month=2026-06&{query}")
    assert settlement.status_code == 200
    settlement_text = settlement.get_data(as_text=True)
    assert "North House" in settlement_text
    assert "South House" in settlement_text
    assert "物件收款彙總" in settlement_text
    assert "合計" in settlement_text

    new_tenants = logged_in_client.get(f"/reports/new-tenants?year_month=2026-06&{query}")
    assert new_tenants.status_code == 200
    assert "Tenant Two" in new_tenants.get_data(as_text=True)

    yearly = logged_in_client.get(f"/reports/property-yearly?year=2026&{query}")
    assert yearly.status_code == 200
    yearly_text = yearly.get_data(as_text=True)
    assert "North House" in yearly_text
    assert "South House" in yearly_text
    assert "2026-06" in yearly_text
    assert "2026-12" in yearly_text
    assert "全年合計" in yearly_text


def test_reporting_expansion_exports_csv_and_xlsx(app, logged_in_client, seeded_data):
    second = _add_second_property_with_bill(app, seeded_data)
    response = logged_in_client.get(
        f"/reports/collection/export?year_month=2026-06&property_id={second['property_id']}&format=csv"
    )
    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("text/csv")
    assert "paid_amount" in response.get_data(as_text=True)
    assert "Tenant Two" in response.get_data(as_text=True)

    response = logged_in_client.get(
        f"/reports/property-yearly/export?year=2026&property_id={second['property_id']}&format=xlsx"
    )
    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith(
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


def test_property_reports_reject_property_outside_landlord_scope(app, seeded_data):
    second = _add_second_property_with_bill(app, seeded_data)
    with app.app_context():
        unrelated_landlord = Landlord(name="Unrelated Owner")
        db.session.add(unrelated_landlord)
        db.session.flush()
        landlord_user = User(
            username="landlord-user",
            name="Landlord User",
            role="landlord",
            landlord_id=unrelated_landlord.id,
        )
        landlord_user.set_password("landlord123")
        db.session.add(landlord_user)
        db.session.commit()

    client = app.test_client()
    response = client.post(
        "/auth/login",
        data={"username": "landlord-user", "password": "landlord123"},
        follow_redirects=True,
    )
    assert response.status_code == 200
    response = client.get(f"/reports/collection?year_month=2026-06&property_id={second['property_id']}")
    assert response.status_code == 403


def test_property_collection_caps_overpayment_and_rounds_export_money(app, logged_in_client, seeded_data):
    second = _add_second_property_with_bill(app, seeded_data)
    with app.app_context():
        db.session.add(
            PaymentRecord(
                monthly_bill_id=second["bill_id"],
                amount=Decimal("10000"),
                record_status="linked",
                transaction_date=date(2026, 6, 12),
            )
        )
        db.session.commit()
        rows = ReportService.property_collection("2026-06", [second["property_id"]])

    assert rows[0]["paid_amount"] == Decimal("14000")
    assert rows[0]["outstanding_amount"] == 0
    assert ReportService.export_money_rows([{"amount": Decimal("100.5")}], ["amount"]) == [{"amount": 101}]


def test_property_expense_report_and_settlement_use_only_posted_expenses(app, logged_in_client, seeded_data):
    _add_property_expenses(app, seeded_data)
    query = f"year_month=2026-06&property_id={seeded_data['property_id']}"

    expense_report = logged_in_client.get(f"/reports/property-expenses?{query}")
    assert expense_report.status_code == 200
    expense_text = expense_report.get_data(as_text=True)
    assert "物件支出明細" in expense_text
    assert "Posted repair vendor" in expense_text
    assert "Draft vendor" not in expense_text
    assert "Voided vendor" not in expense_text
    assert ">800<" in expense_text

    export = logged_in_client.get(f"/reports/property-expenses/export?{query}&format=csv")
    assert export.status_code == 200
    export_text = export.get_data(as_text=True)
    assert "POSTED-1" in export_text
    assert "DRAFT-1" not in export_text
    assert "VOID-1" not in export_text

    xlsx_export = logged_in_client.get(f"/reports/property-expenses/export?{query}&format=xlsx")
    assert xlsx_export.status_code == 200
    assert xlsx_export.headers["Content-Type"].startswith(
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    settlement = logged_in_client.get(f"/reports/property-settlement?{query}")
    assert settlement.status_code == 200
    settlement_text = settlement.get_data(as_text=True)
    assert ">800<" in settlement_text
    assert ">-800<" in settlement_text


def test_property_settlement_includes_property_with_posted_expense_and_no_bill(app, logged_in_client, seeded_data):
    with app.app_context():
        expense_only_property = Property(
            landlord_id=seeded_data["landlord_id"],
            name="Expense Only House",
            address="Kaohsiung City",
            total_rooms=0,
        )
        db.session.add(expense_only_property)
        db.session.flush()
        expense_only_property_id = expense_only_property.id
        db.session.add(
            PropertyExpense(
                property_id=expense_only_property.id,
                transaction_date=date(2026, 6, 20),
                category="tax",
                amount=Decimal("500"),
                record_status="posted",
            )
        )
        db.session.commit()

    response = logged_in_client.get(
        f"/reports/property-settlement?year_month=2026-06&property_id={expense_only_property_id}"
    )
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "Expense Only House" in text
    assert ">500<" in text
    assert ">-500<" in text
