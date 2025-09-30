
def test_listings_endpoint_available(client):
    response = client.get("/listings")
    assert response.status_code == 200
    payload = response.get_json()
    assert "data" in payload
