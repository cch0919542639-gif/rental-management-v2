from app.models import Property, Room


def test_nested_property_create_for_landlord(app, logged_in_client, seeded_data):
    client = logged_in_client

    response = client.get(f"/properties/landlord/{seeded_data['landlord_id']}/create")
    assert response.status_code == 200
    assert "房東" in response.get_data(as_text=True)

    response = client.post(
        f"/properties/landlord/{seeded_data['landlord_id']}/create",
        data={
            "landlord_id": seeded_data["landlord_id"],
            "name": "Nested Property",
            "address": "Nested Addr",
            "total_rooms": "2",
            "electricity_meter_type": "independent",
            "water_meter_type": "shared",
            "electricity_policy_code": "electricity_bill_usage_ratio",
            "water_policy_code": "water_bill_by_stay_days",
            "billing_rule": "monthly",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        prop = Property.query.filter_by(name="Nested Property").first()
        assert prop is not None
        assert prop.landlord_id == seeded_data["landlord_id"]
        assert prop.electricity_policy_code == "electricity_bill_usage_ratio"
        assert prop.water_policy_code == "water_bill_by_stay_days"


def test_nested_room_create_for_property(app, logged_in_client, seeded_data):
    client = logged_in_client

    response = client.get(f"/rooms/property/{seeded_data['property_id']}/create")
    assert response.status_code == 200
    assert "物業" in response.get_data(as_text=True)

    response = client.post(
        f"/rooms/property/{seeded_data['property_id']}/create",
        data={
            "property_id": seeded_data["property_id"],
            "room_number": "A99",
            "rent": "8000",
            "deposit": "16000",
            "area_ping": "6.5",
            "status": "vacant",
            "electricity_policy_code": "electricity_bill_usage_ratio_plus_public_share",
            "water_policy_code": "water_bill_by_stay_days",
            "notes": "nested room",
        },
        follow_redirects=True,
    )
    assert response.status_code == 200

    with app.app_context():
        room = Room.query.filter_by(room_number="A99").first()
        assert room is not None
        assert room.property_id == seeded_data["property_id"]
        assert room.electricity_policy_code == "electricity_bill_usage_ratio_plus_public_share"
        assert room.water_policy_code == "water_bill_by_stay_days"
