from datetime import date
from decimal import Decimal

from app.core.db import db
from app.models import Contract, Room, Tenant, WaterBill
from app.services import WaterService


def test_property_preview_includes_active_expired_contract_vacant_and_rounding(app, seeded_data):
    with app.app_context():
        prop_id = seeded_data["property_id"]
        property_row = db.session.get(Room, seeded_data["room_id"]).property
        property_row.water_policy_code = "water_bill_by_stay_days"

        vacant = Room(property_id=prop_id, room_number="A02", status="vacant")
        continued = Room(property_id=prop_id, room_number="A04", status="occupied")
        tenant = Tenant(name="續住房客")
        db.session.add_all([vacant, continued, tenant])
        db.session.flush()
        db.session.add(
            Contract(
                tenant_id=tenant.id,
                room_id=continued.id,
                start_date=date(2026, 1, 1),
                end_date=date(2026, 7, 31),
                rent=Decimal("10000"),
                deposit=Decimal("20000"),
                status="active",
            )
        )
        water_bill = WaterBill(
            property_id=prop_id,
            billing_start=date(2026, 8, 1),
            billing_end=date(2026, 8, 31),
            total_amount=Decimal("198.50"),
        )
        db.session.add(water_bill)
        db.session.commit()

        preview = WaterService.preview_property_shared_by_stay_days(water_bill=water_bill)

        assert preview["billed_total"] == Decimal("198.50")
        assert preview["allocated_total"] == Decimal("200")
        assert preview["rounding_difference"] == Decimal("1.50")
        by_room = {row["room_number"]: row for row in preview["rows"]}
        assert by_room["A01"]["stay_days"] == 31
        assert by_room["A04"]["tenant_name"] == "續住房客"
        assert by_room["A04"]["stay_days"] == 31
        assert by_room["A01"]["allocated_amount"] == Decimal("100")
        assert by_room["A04"]["allocated_amount"] == Decimal("100")
        assert by_room["A02"]["allocated_amount"] == 0
        assert by_room["A02"]["reason"] == "空房不分攤"


def test_property_preview_route_renders_property_reconciliation(app, logged_in_client, seeded_data):
    with app.app_context():
        property_row = db.session.get(Room, seeded_data["room_id"]).property
        property_row.water_policy_code = "water_bill_by_stay_days"
        water_bill = WaterBill(
            property_id=seeded_data["property_id"],
            billing_start=date(2026, 8, 1),
            billing_end=date(2026, 8, 31),
            total_amount=Decimal("200"),
        )
        db.session.add(water_bill)
        db.session.commit()
        water_bill_id = water_bill.id

    response = logged_in_client.get(f"/water/{water_bill_id}/property-preview")
    text = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "水費全物件分攤預覽" in text
    assert "進位差額" in text
    assert "NT " in text
