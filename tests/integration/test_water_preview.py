def test_water_preview_shared_mode_renders_result(app, logged_in_client, seeded_data):
    client = logged_in_client

    response = client.post(
        "/water/create",
        data={
            "property_id": seeded_data["property_id"],
            "billing_start": "2026-06-01",
            "billing_end": "2026-06-30",
            "total_amount": "300",
            "meter_prev_1": "10",
            "meter_curr_1": "20",
            "sub_meter_1": "10",
            "actual_usage_1": "10",
            "notes": "preview shared test",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        from app.models import WaterBill
        wb = WaterBill.query.filter_by(notes="preview shared test").first()
        assert wb is not None
        water_bill_id = wb.id

    response = client.post(
        f"/water/{water_bill_id}/preview",
        data={
            "monthly_bill_id": seeded_data["monthly_bill_id"],
            "mode": "shared_by_stay_days",
            "amount": "",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "預覽結果" in text
    assert "預覽水費金額" in text
    assert "合約居住天數" in text


def test_water_preview_independent_mode_renders_result(app, logged_in_client, seeded_data):
    client = logged_in_client

    response = client.post(
        "/water/create",
        data={
            "property_id": seeded_data["property_id"],
            "billing_start": "2026-07-01",
            "billing_end": "2026-07-31",
            "total_amount": "350",
            "meter_prev_1": "50",
            "meter_curr_1": "80",
            "sub_meter_1": "30",
            "actual_usage_1": "30",
            "notes": "preview independent test",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        from app.models import WaterBill
        wb = WaterBill.query.filter_by(notes="preview independent test").first()
        assert wb is not None
        water_bill_id = wb.id

    response = client.post(
        f"/water/{water_bill_id}/preview",
        data={
            "monthly_bill_id": seeded_data["monthly_bill_id"],
            "mode": "independent_meter",
            "amount": "350",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    assert "預覽結果" in text
    assert "independent_meter" in text
    assert "350.00" in text or "350" in text


def test_water_preview_get_renders_form(app, logged_in_client, seeded_data):
    """GET /water/<id>/preview should render the form page without preview result."""
    client = logged_in_client

    response = client.post(
        "/water/create",
        data={
            "property_id": seeded_data["property_id"],
            "billing_start": "2026-08-01",
            "billing_end": "2026-08-31",
            "total_amount": "200",
            "notes": "preview get test",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        from app.models import WaterBill
        wb = WaterBill.query.filter_by(notes="preview get test").first()
        assert wb is not None
        water_bill_id = wb.id

    response = client.get(f"/water/{water_bill_id}/preview")
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    # Form should be present, no preview result yet
    assert "預覽分攤" in text
    assert "水費預覽" in text or "預覽" in text


def test_water_preview_post_no_monthly_bill(app, logged_in_client, seeded_data):
    """POST /water/<id>/preview without monthly_bill_id should re-render the form."""
    client = logged_in_client

    response = client.post(
        "/water/create",
        data={
            "property_id": seeded_data["property_id"],
            "billing_start": "2026-09-01",
            "billing_end": "2026-09-30",
            "total_amount": "400",
            "notes": "preview no-bill test",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        from app.models import WaterBill
        wb = WaterBill.query.filter_by(notes="preview no-bill test").first()
        assert wb is not None
        water_bill_id = wb.id

    # POST with missing required field (no monthly_bill_id)
    response = client.post(
        f"/water/{water_bill_id}/preview",
        data={
            "monthly_bill_id": "",
            "mode": "shared_by_stay_days",
            "amount": "",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200
    text = response.get_data(as_text=True)
    # Form should still be displayed; no preview result since validation failed
    assert "預覽分攤" in text
