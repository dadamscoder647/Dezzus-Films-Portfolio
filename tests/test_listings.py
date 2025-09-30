from services.jwt_utils import encode_token


def auth_header_for(user):
    token = encode_token(user)
    return {"Authorization": f"Bearer {token}"}


def create_listing(client, user, **overrides):
    payload = {
        "title": "Software Engineer",
        "description": "Build things",
        "company": "Tech Co",
        "location": "Remote",
        "category": "Engineering",
        "is_remote": True,
    }
    payload.update(overrides)
    return client.post("/listings", json=payload, headers=auth_header_for(user))


def test_listings_get_returns_created_listing(client, employer_user):
    create_listing(client, employer_user)
    response = client.get("/listings")
    assert response.status_code == 200
    data = response.get_json()["data"]
    assert len(data) == 1
    assert data[0]["title"] == "Software Engineer"


def test_create_listing_requires_employer_context(client, applicant_user):
    response = client.post(
        "/listings",
        json={"title": "Role"},
        headers=auth_header_for(applicant_user),
    )
    assert response.status_code == 400


def test_create_listing_assigns_employer(client, employer_user):
    response = create_listing(client, employer_user)
    assert response.status_code == 201
    listing = response.get_json()["data"]
    assert listing["employer_id"] == employer_user.id


def test_update_listing_allows_admin_override(client, employer_user, admin_user):
    create_listing(client, employer_user)
    response = client.patch(
        "/listings/1",
        json={"title": "Updated"},
        headers=auth_header_for(admin_user),
    )
    assert response.status_code == 200
    assert response.get_json()["data"]["title"] == "Updated"


def test_apply_to_listing(client, employer_user, applicant_user):
    create_listing(client, employer_user)
    response = client.post(
        "/listings/1/apply",
        json={"applicant_name": "Jane", "applicant_email": "jane@example.com"},
        headers=auth_header_for(applicant_user),
    )
    assert response.status_code == 201
    data = response.get_json()["data"]
    assert data["listing_id"] == 1

