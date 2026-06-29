from app.models import ElectricityBill, ElectricityReading, ElectricityMeter


def test_electricity_property_new_bill_quick_reading_and_log(app, logged_in_client, seeded_data):
    client = logged_in_client

    response = client.post(
        "/electricity/meters/create",
        data={
            "property_id": seeded_data["property_id"],
            "room_id": seeded_data["room_id"],
            "meter_number": "M-PROP-WF-001",
            "room_number": "A01",
            "is_main": True,
            "notes": "property workflow meter",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        meter = ElectricityMeter.query.filter_by(meter_number="M-PROP-WF-001").first()
        assert meter is not None
        meter_id = meter.id

    response = client.post(
        f"/electricity/property/{seeded_data['property_id']}/new-bill",
        data={
            "property_id": seeded_data["property_id"],
            "meter_id": meter_id,
            "calc_method_id": seeded_data["calc_method_id"],
            "year_month": "2026-10",
            "period_start": "2026-10-01",
            "period_end": "2026-10-31",
            "prev_reading": "20",
            "curr_reading": "60",
            "total_amount": "300",
            "public_amount": "40",
            "flow_amount": "260",
            "notes": "property workflow bill",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "物件電費單已建立" in response.get_data(as_text=True)

    with app.app_context():
        bill = ElectricityBill.query.filter_by(notes="property workflow bill").first()
        assert bill is not None
        bill_id = bill.id

    response = client.post(
        f"/electricity/property/{seeded_data['property_id']}/quick-reading",
        data={
            "bill_id": bill_id,
            "meter_id": meter_id,
            "room_id": seeded_data["room_id"],
            "prev_reading": "20",
            "curr_reading": "60",
            "calculated_amount": "260",
            "confirmed_amount": "260",
            "notes": "property workflow reading",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    assert "物件抄表資料已建立" in response.get_data(as_text=True)

    with app.app_context():
        reading = ElectricityReading.query.filter_by(notes="property workflow reading").first()
        assert reading is not None

    response = client.get(f"/electricity/property/{seeded_data['property_id']}/reading-log")
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "抄表歷史" in text
    assert "property workflow reading" in text
    assert "2026-10" in text
