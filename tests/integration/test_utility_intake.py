from io import BytesIO


def test_utility_intake_is_available_and_does_not_create_bills(logged_in_client, app, seeded_data):
    app.config["OCR_PROVIDER"] = "noop"

    response = logged_in_client.post(
        "/utility-intake/",
        data={
            "property_id": str(seeded_data["property_id"]),
            "utility_type": "electricity",
            "document": (BytesIO(b"not-an-image"), "utility.jpg"),
        },
        content_type="multipart/form-data",
    )

    assert response.status_code == 200
    assert "人工校正草稿" in response.get_data(as_text=True)
    assert "不會建立月帳單或向房客收費" in response.get_data(as_text=True)
