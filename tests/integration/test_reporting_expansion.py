import csv
from datetime import date
from decimal import Decimal
from io import StringIO

from app.core.db import db
from app.models import Contract, Landlord, MonthlyBill, PaymentRecord, Property, PropertyExpense, Room, Tenant, User, UserPropertyAccess
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
    assert "<th>物件</th>" in text
    assert "<th>房號</th>" in text
    assert "<th>房客</th>" in text
    assert '<th class="money-col">當月應繳</th>' in text
    assert '<th class="money-col">本月收款</th>' in text
    assert '<th class="money-col">抵扣/調整</th>' in text
    assert '<th class="money-col">期末餘額</th>' in text
    assert "<th>狀態</th>" in text
    assert "collection-detail-row" in text
    assert "<summary>差額明細</summary>" in text
    assert "<dt>租金</dt>" in text
    assert "部分未收" in text
    assert "report-summary-cards" in text
    assert "2026-06-03" not in text
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
    response = client.get("/reports/monthly?year_month=2026-06")
    assert response.status_code == 200
    assert "South House" not in response.get_data(as_text=True)


def test_landlord_without_explicit_property_access_sees_no_property_data(app, seeded_data):
    with app.app_context():
        landlord = Landlord(name="No Access Owner")
        db.session.add(landlord)
        db.session.flush()
        user = User(
            username="owner-no-access",
            name="No Access Account",
            role="landlord",
            landlord_id=landlord.id,
        )
        user.set_password("owner-no-access-password")
        db.session.add(user)
        db.session.commit()

    client = app.test_client()
    login = client.post(
        "/auth/login",
        data={"username": "owner-no-access", "password": "owner-no-access-password"},
        follow_redirects=True,
    )
    assert login.status_code == 200

    for url in [
        "/reports/monthly?year_month=2026-06",
        "/reports/landlord-summary?year_month=2026-06",
    ]:
        response = client.get(url)
        assert response.status_code == 200
        assert "North House" not in response.get_data(as_text=True)

    for url in [
        "/reports/monthly/export?year_month=2026-06&format=csv",
        "/reports/landlord-summary/export?year_month=2026-06&format=csv",
        "/reports/collection/export?year_month=2026-06&format=csv",
    ]:
        response = client.get(url)
        assert response.status_code == 200
        assert "North House" not in response.get_data(as_text=True)

    for url in [
        "/reports/monthly/export?year_month=2026-06&format=xlsx",
        "/reports/landlord-summary/export?year_month=2026-06&format=xlsx",
        "/reports/collection/export?year_month=2026-06&format=xlsx",
    ]:
        response = client.get(url)
        assert response.status_code == 200
        assert response.headers["Content-Type"].startswith(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

    collection = client.get("/reports/collection?year_month=2026-06")
    assert collection.status_code == 200
    assert "North House" not in collection.get_data(as_text=True)

    property_yearly = client.get("/reports/property-yearly?year=2026")
    assert property_yearly.status_code == 200
    assert "North House" not in property_yearly.get_data(as_text=True)

    property_yearly_csv = client.get("/reports/property-yearly/export?year=2026&format=csv")
    assert property_yearly_csv.status_code == 200
    assert "North House" not in property_yearly_csv.get_data(as_text=True)

    property_yearly_xlsx = client.get("/reports/property-yearly/export?year=2026&format=xlsx")
    assert property_yearly_xlsx.status_code == 200
    assert property_yearly_xlsx.headers["Content-Type"].startswith(
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    yearly = client.get("/reports/yearly?year=2026")
    assert yearly.status_code == 200
    assert ">0<" in yearly.get_data(as_text=True)
    assert ">12000<" not in yearly.get_data(as_text=True)

    yearly_csv = client.get("/reports/yearly/export?year=2026&format=csv")
    assert yearly_csv.status_code == 200
    yearly_rows = list(csv.DictReader(StringIO(yearly_csv.get_data(as_text=True).lstrip("\ufeff"))))
    june = next(row for row in yearly_rows if row["year_month"] == "2026-06")
    assert june["total_amount"] == "0"

    yearly_xlsx = client.get("/reports/yearly/export?year=2026&format=xlsx")
    assert yearly_xlsx.status_code == 200
    assert yearly_xlsx.headers["Content-Type"].startswith(
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    response = client.get(
        f"/reports/collection?year_month=2026-06&property_id={seeded_data['property_id']}"
    )
    assert response.status_code == 403


def test_landlord_portal_scopes_summary_monthly_yearly_and_downloads(app, seeded_data):
    with app.app_context():
        unrelated_landlord = Landlord(name="Owner B")
        db.session.add(unrelated_landlord)
        db.session.flush()
        foreign_property = Property(
            landlord_id=unrelated_landlord.id,
            name="Private House",
            address="Kaohsiung City",
            total_rooms=1,
        )
        foreign_room = Room(property=foreign_property, room_number="P01", rent=Decimal("9000"), status="occupied")
        foreign_tenant = Tenant(name="Private Tenant", phone="0977000000")
        db.session.add_all([foreign_property, foreign_room, foreign_tenant])
        db.session.flush()
        foreign_property_id = foreign_property.id
        foreign_contract = Contract(
            tenant_id=foreign_tenant.id,
            room_id=foreign_room.id,
            start_date=date(2026, 6, 1),
            end_date=date(2027, 5, 31),
            rent=Decimal("9000"),
            deposit=Decimal("18000"),
            status="active",
        )
        db.session.add(foreign_contract)
        db.session.flush()
        db.session.add(
            MonthlyBill(
                contract_id=foreign_contract.id,
                year_month="202606",
                rent=Decimal("9000"),
                total=Decimal("9000"),
                paid=False,
            )
        )
        landlord_user = User(
            username="owner-a",
            name="Owner A Account",
            role="landlord",
            landlord_id=seeded_data["landlord_id"],
        )
        landlord_user.set_password("owner-a-password")
        db.session.add(landlord_user)
        db.session.flush()
        db.session.add(UserPropertyAccess(user_id=landlord_user.id, property_id=seeded_data["property_id"]))
        db.session.commit()

    client = app.test_client()
    login = client.post(
        "/auth/login",
        data={"username": "owner-a", "password": "owner-a-password"},
        follow_redirects=True,
    )
    assert login.status_code == 200

    for url in [
        "/reports/monthly?year_month=2026-06",
        "/reports/landlord-summary?year_month=2026-06",
        "/reports/monthly/export?year_month=2026-06&format=csv",
        "/reports/landlord-summary/export?year_month=2026-06&format=csv",
    ]:
        response = client.get(url)
        assert response.status_code == 200
        assert "Private House" not in response.get_data(as_text=True)

    for url in ["/reports/monthly?year_month=2026-04"]:
        response = client.get(url)
        assert response.status_code == 403
        assert "Private House" not in response.get_data(as_text=True)

    yearly = client.get("/reports/yearly?year=2026")
    assert yearly.status_code == 200
    yearly_text = yearly.get_data(as_text=True)
    assert ">12,000<" in yearly_text
    assert ">21,000<" not in yearly_text

    yearly_csv = client.get("/reports/yearly/export?year=2026&format=csv")
    assert yearly_csv.status_code == 200
    yearly_rows = list(csv.DictReader(StringIO(yearly_csv.get_data(as_text=True).lstrip("\ufeff"))))
    june = next(row for row in yearly_rows if row["year_month"] == "2026-06")
    assert june["total_amount"] == "12000"

    yearly_xlsx = client.get("/reports/yearly/export?year=2026&format=xlsx")
    assert yearly_xlsx.status_code == 200
    assert yearly_xlsx.headers["Content-Type"].startswith(
        "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    hub = client.get("/reports/")
    hub_text = hub.get_data(as_text=True)
    assert "我的月報" in hub_text
    assert "年度總覽" in hub_text
    assert "房東彙總" in hub_text
    assert client.get(f"/reports/collection?year_month=2026-06&property_id={foreign_property_id}").status_code == 403


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
