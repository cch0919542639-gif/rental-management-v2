def test_electricity_property_detail_renders_summary_and_recent_bills(app, logged_in_client, seeded_data):
    client = logged_in_client

    response = client.post(
        "/electricity/meters/create",
        data={
            "property_id": seeded_data["property_id"],
            "room_id": seeded_data["room_id"],
            "meter_number": "M-PROP-001",
            "room_number": "A01",
            "is_main": True,
            "notes": "property detail meter",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    response = client.post(
        "/electricity/bills/create",
        data={
            "property_id": seeded_data["property_id"],
            "meter_id": 1,
            "calc_method_id": seeded_data["calc_method_id"],
            "year_month": "2026-09",
            "period_start": "2026-09-01",
            "period_end": "2026-09-30",
            "prev_reading": "10",
            "curr_reading": "30",
            "total_amount": "200",
            "public_amount": "20",
            "flow_amount": "180",
            "notes": "property detail bill",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    response = client.get(f"/electricity/property/{seeded_data['property_id']}")
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "電力總覽" in text
    assert "North House" in text
    assert "電表數" in text
    assert "最近電費單" in text
    assert "property detail bill" not in text
    assert "2026-09" in text
