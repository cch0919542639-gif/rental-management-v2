from app.models import Property, Room


def test_property_policy_settings_persist(app, logged_in_client, seeded_data):
    client = logged_in_client

    response = client.post(
        "/properties/create",
        data={
            "landlord_id": seeded_data["landlord_id"],
            "name": "Policy Property",
            "address": "Policy Addr",
            "total_rooms": "3",
            "electricity_meter_type": "shared",
            "water_meter_type": "shared",
            "electricity_policy_code": "electricity_bill_usage_ratio",
            "water_policy_code": "water_bill_by_stay_days",
            "billing_rule": "policy-test",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        prop = Property.query.filter_by(name="Policy Property").first()
        assert prop is not None
        assert prop.electricity_policy_code == "electricity_bill_usage_ratio"
        assert prop.water_policy_code == "water_bill_by_stay_days"


def test_room_policy_override_settings_persist(app, logged_in_client, seeded_data):
    client = logged_in_client

    response = client.post(
        "/rooms/create",
        data={
            "property_id": seeded_data["property_id"],
            "room_number": "A98",
            "rent": "9000",
            "deposit": "18000",
            "area_ping": "7",
            "status": "vacant",
            "electricity_policy_code": "electricity_bill_usage_ratio_plus_public_share",
            "water_policy_code": "water_bill_by_stay_days",
            "notes": "policy override room",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        room = Room.query.filter_by(room_number="A98").first()
        assert room is not None
        assert room.electricity_policy_code == "electricity_bill_usage_ratio_plus_public_share"
        assert room.water_policy_code == "water_bill_by_stay_days"
