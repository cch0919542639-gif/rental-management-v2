from app.models import ElectricityBill, Landlord, Tenant, WaterBill


def test_electricity_property_filter(app, logged_in_client, seeded_data):
    client = logged_in_client

    response = client.post(
        "/electricity/bills/create",
        data={
            "property_id": seeded_data["property_id"],
            "meter_id": 0,
            "calc_method_id": seeded_data["calc_method_id"],
            "year_month": "2026-07",
            "period_start": "2026-07-01",
            "period_end": "2026-07-31",
            "prev_reading": "0",
            "curr_reading": "100",
            "total_amount": "500",
            "public_amount": "50",
            "flow_amount": "450",
            "notes": "filter target",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    response = client.get(f"/electricity/property/{seeded_data['property_id']}/bills")
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "目前篩選物件" in text
    assert "filter target" not in text

    with app.app_context():
        bill = ElectricityBill.query.filter_by(year_month="202607").first()
        assert bill is not None

    response = client.get(f"/electricity/property/{seeded_data['property_id']}/bills")
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert str(bill.id) in text


def test_delete_low_risk_records(app, logged_in_client):
    client = logged_in_client

    client.post(
        "/landlords/create",
        data={
            "name": "Delete Landlord",
            "phone": "0912000001",
            "electricity_account": "",
            "water_account": "",
            "electricity_rate_type": "fixed",
            "electricity_rate": "5",
            "water_rate_type": "fixed",
            "water_rate": "100",
            "notes": "",
        },
        follow_redirects=True,
    )
    client.post(
        "/tenants/create",
        data={
            "name": "Delete Tenant",
            "phone": "0912000002",
            "id_number": "A123456788",
            "emergency_contact": "",
            "emergency_phone": "",
            "notes": "",
        },
        follow_redirects=True,
    )
    client.post(
        "/water/create",
        data={
            "property_id": 1,
            "billing_start": "2026-07-01",
            "billing_end": "2026-07-31",
            "total_amount": "200",
            "meter_prev_1": "0",
            "meter_curr_1": "10",
            "sub_meter_1": "10",
            "actual_usage_1": "10",
            "meter_prev_2": "0",
            "meter_curr_2": "0",
            "sub_meter_2": "0",
            "actual_usage_2": "0",
            "notes": "delete target",
        },
        follow_redirects=True,
    )

    with app.app_context():
        landlord = Landlord.query.filter_by(name="Delete Landlord").first()
        tenant = Tenant.query.filter_by(name="Delete Tenant").first()
        water_bill = WaterBill.query.filter_by(notes="delete target").first()
        assert landlord is not None
        assert tenant is not None
        assert water_bill is not None

    response = client.post(f"/landlords/{landlord.id}/delete", follow_redirects=True)
    assert response.status_code == 200
    assert "房東已刪除" in response.get_data(as_text=True)

    response = client.post(f"/tenants/{tenant.id}/delete", follow_redirects=True)
    assert response.status_code == 200
    assert "房客已刪除" in response.get_data(as_text=True)

    response = client.post(f"/water/{water_bill.id}/delete", follow_redirects=True)
    assert response.status_code == 200
    assert "水費單已刪除" in response.get_data(as_text=True)

    with app.app_context():
        assert Landlord.query.filter_by(name="Delete Landlord").first() is None
        assert Tenant.query.filter_by(name="Delete Tenant").first() is None
        assert WaterBill.query.filter_by(notes="delete target").first() is None
