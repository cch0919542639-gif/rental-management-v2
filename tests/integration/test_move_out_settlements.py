from datetime import date
from decimal import Decimal

import pytest
from flask_login import login_user
from werkzeug.exceptions import Forbidden

from app.core.db import db
from app.models import Contract, Landlord, MoveOutSettlement, PaymentRecord, Property, Room, Tenant, User
from app.modules.move_out_settlements.routes import _assert_visible, _visible_property_ids
from app.services import MoveOutSettlementService


def _draft(app, seeded_data):
    with app.app_context():
        contract = db.session.get(Contract, seeded_data["contract_id"])
        settlement = MoveOutSettlementService.create(
            contract=contract,
            move_out_date=date(2026, 7, 1),
            final_rent=Decimal("1000"),
            electricity_amount=Decimal("300"),
            water_amount=Decimal("200"),
            management_fee=Decimal("0"),
            previous_debt=Decimal("0"),
            cleaning_fee=Decimal("500"),
            repair_fee=Decimal("0"),
            other_charge=Decimal("0"),
        )
        return settlement.id


def test_r6_keeps_full_refund_separate_from_manual_allocations(app, seeded_data):
    settlement_id = _draft(app, seeded_data)
    with app.app_context():
        settlement = db.session.get(MoveOutSettlement, settlement_id)
        assert settlement.deposit_held == Decimal("24000")
        assert settlement.refund_amount == Decimal("24000")
        assert settlement.gross_charges == Decimal("2000")

        MoveOutSettlementService.settle(
            settlement,
            allocations={"final_rent": 1000, "electricity_amount": 300, "water_amount": 200, "cleaning_fee": 500},
        )
        assert settlement.status == "settled"
        assert settlement.allocated_amount == Decimal("2000")
        assert settlement.net_refund_amount == Decimal("22000")
        assert settlement.outstanding_amount == Decimal("0")
        assert PaymentRecord.query.count() == 0
        assert "closed" not in MoveOutSettlement.TRANSITIONS


def test_r6_rejects_over_allocation_and_post_settlement_edits(app, seeded_data):
    settlement_id = _draft(app, seeded_data)
    with app.app_context():
        settlement = db.session.get(MoveOutSettlement, settlement_id)
        with pytest.raises(ValueError, match="單一費用"):
            MoveOutSettlementService.settle(settlement, allocations={"electricity_amount": 301})
        MoveOutSettlementService.settle(settlement, allocations={"final_rent": 1000})
        with pytest.raises(ValueError, match="只有草稿"):
            MoveOutSettlementService.update(settlement, cleaning_fee=100)


def test_r6_routes_render_draft_and_manual_confirmation(app, logged_in_client, seeded_data):
    response = logged_in_client.post(
        "/move-out-settlements/create",
        data={
            "contract_id": seeded_data["contract_id"], "move_out_date": "2026-07-01",
            "final_rent": "1000", "electricity_amount": "300", "water_amount": "200",
            "management_fee": "0", "previous_debt": "0", "cleaning_fee": "500", "repair_fee": "0",
            "other_charge": "0", "evidence_type": "", "evidence_reference": "", "notes": "", "submit": "儲存草稿",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "全額退款" in response.get_data(as_text=True)
    with app.app_context():
        settlement = MoveOutSettlement.query.one()
        settlement_id = settlement.id

    response = logged_in_client.post(
        f"/move-out-settlements/{settlement_id}/settle",
        data={
            "final_rent": "1000", "electricity_amount": "300", "water_amount": "200",
            "management_fee": "0", "previous_debt": "0", "cleaning_fee": "500", "repair_fee": "0", "other_charge": "0",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "付款與退款仍待另行認列" in text
    assert "closed" not in text


def test_r6_filters_exports_and_enforces_landlord_property_scope(app, logged_in_client, seeded_data):
    north_settlement_id = _draft(app, seeded_data)
    with app.app_context():
        external_landlord = Landlord(name="External Owner")
        db.session.add(external_landlord)
        db.session.flush()
        external_property = Property(landlord_id=external_landlord.id, name="External House", address="Elsewhere", total_rooms=1)
        db.session.add(external_property)
        db.session.flush()
        external_room = Room(property_id=external_property.id, room_number="B01", rent=Decimal("8000"), deposit=Decimal("16000"), status="occupied")
        external_tenant = Tenant(name="External Tenant")
        db.session.add_all([external_room, external_tenant])
        db.session.flush()
        external_contract = Contract(
            tenant_id=external_tenant.id, room_id=external_room.id, start_date=date(2026, 1, 1), end_date=date(2026, 12, 31),
            rent=Decimal("8000"), deposit=Decimal("16000"), status="active",
        )
        landlord_user = User(username="external-landlord", name="External Owner", role="landlord", landlord_id=external_landlord.id)
        landlord_user.set_password("landlord123")
        db.session.add_all([external_contract, landlord_user])
        db.session.flush()
        external_settlement = MoveOutSettlementService.create(
            contract=external_contract, move_out_date=date(2026, 7, 2),
            final_rent=Decimal("800"), electricity_amount=0, water_amount=0, management_fee=0,
            previous_debt=0, cleaning_fee=0, repair_fee=0, other_charge=0,
        )
        external_settlement_id = external_settlement.id
        external_property_id = external_property.id
        external_user_id = landlord_user.id

    response = logged_in_client.get(
        f"/move-out-settlements/?property_id={seeded_data['property_id']}&move_out_from=2026-07-01&move_out_to=2026-07-01"
    )
    text = response.get_data(as_text=True)
    assert response.status_code == 200
    assert "North House" in text
    assert "External Tenant／External House" not in text

    response = logged_in_client.get(f"/move-out-settlements/export?property_id={seeded_data['property_id']}&format=csv")
    assert response.status_code == 200
    assert "North House" in response.get_data(as_text=True)
    assert "External House" not in response.get_data(as_text=True)
    response = logged_in_client.get(f"/move-out-settlements/export?property_id={seeded_data['property_id']}&format=xlsx")
    assert response.status_code == 200
    assert response.headers["Content-Type"].startswith("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")

    with app.test_request_context():
        scoped_user = db.session.get(User, external_user_id)
        assert scoped_user.role == "landlord"
        assert scoped_user.landlord_id == external_property_id
        north_settlement = db.session.get(MoveOutSettlement, north_settlement_id)
        external_settlement = db.session.get(MoveOutSettlement, external_settlement_id)
        login_user(scoped_user)
        assert _visible_property_ids() == {external_property_id}
        assert _assert_visible(external_settlement).id == external_settlement_id
        with pytest.raises(Forbidden):
            _assert_visible(north_settlement)
