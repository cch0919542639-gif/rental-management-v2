from datetime import date

from app.core.db import db
from app.models import Landlord, Property, Room, Tenant, WaterBill


class TestLandlordDelete:
    def test_delete_landlord_with_properties_fails(self, logged_in_client, seeded_data):
        client = logged_in_client
        response = client.post(f"/landlords/{seeded_data['landlord_id']}/delete", follow_redirects=True)
        assert response.status_code == 200
        with db.session.begin():
            landlord = db.session.get(Landlord, seeded_data["landlord_id"])
        assert landlord is not None

    def test_delete_landlord_without_properties_succeeds(self, app, logged_in_client, seeded_data):
        with app.app_context():
            prop = db.session.get(Property, seeded_data["property_id"])
            landlord_id = seeded_data["landlord_id"]
            landlord = db.session.get(Landlord, landlord_id)
            db.session.delete(prop)
            db.session.commit()

        client = logged_in_client
        response = client.post(f"/landlords/{landlord_id}/delete", follow_redirects=True)
        assert response.status_code == 200
        with app.app_context():
            assert db.session.get(Landlord, landlord_id) is None


class TestTenantDelete:
    def test_delete_tenant_with_contracts_fails(self, logged_in_client, seeded_data):
        client = logged_in_client
        response = client.post(f"/tenants/{seeded_data['tenant_id']}/delete", follow_redirects=True)
        assert response.status_code == 200
        with db.session.begin():
            tenant = db.session.get(Tenant, seeded_data["tenant_id"])
        assert tenant is not None

    def test_delete_tenant_without_contracts_succeeds(self, app, seeded_data, logged_in_client):
        from app.models import Contract
        with app.app_context():
            contracts = Contract.query.filter_by(tenant_id=seeded_data["tenant_id"]).all()
            for c in contracts:
                db.session.delete(c)
            db.session.commit()

        client = logged_in_client
        tenant_id = seeded_data["tenant_id"]
        response = client.post(f"/tenants/{tenant_id}/delete", follow_redirects=True)
        assert response.status_code == 200
        with app.app_context():
            assert db.session.get(Tenant, tenant_id) is None


class TestWaterBillDelete:
    def test_delete_water_bill_succeeds(self, app, logged_in_client, seeded_data):
        with app.app_context():
            wb = WaterBill(
                property_id=seeded_data["property_id"],
                billing_start=date(2026, 6, 1),
                billing_end=date(2026, 6, 30),
                total_amount=500,
            )
            db.session.add(wb)
            db.session.commit()
            bill_id = wb.id

        client = logged_in_client
        response = client.post(f"/water/{bill_id}/delete", follow_redirects=True)
        assert response.status_code == 200
        with app.app_context():
            assert db.session.get(WaterBill, bill_id) is None


class TestElectricityPropertyFilter:
    def test_property_filter_returns_bills(self, app, logged_in_client, seeded_data):
        property_id = seeded_data["property_id"]
        client = logged_in_client
        response = client.get(f"/electricity/property/{property_id}/bills")
        assert response.status_code == 200
        assert "North House" in response.data.decode("utf-8")

    def test_property_filter_404(self, logged_in_client):
        client = logged_in_client
        response = client.get("/electricity/property/99999/bills")
        assert response.status_code == 404
