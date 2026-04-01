import json


def test_register_without_biometrics_success(client, register_user):
    resp = register_user()
    assert resp.status_code == 201
    data = resp.get_json()
    assert data["success"] is True
    assert "token" in data
    assert data["data"]["username"] == "alice"
    assert data["data"]["biometrics_registered"]["face"] is False
    assert data["data"]["biometrics_registered"]["fingerprint"] is False


def test_login_password_only_success(client, register_user):
    reg = register_user()
    assert reg.status_code == 201

    resp = client.post(
        "/api/login",
        data=json.dumps({"username": "alice", "password": "SecurePass123"}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert "token" in data
    assert data["data"]["security_info"]["authentication_method"] == "password"


def test_login_requires_face_when_enrolled(client, register_user, sample_face_image):
    reg = register_user(face_image=sample_face_image)
    assert reg.status_code == 201

    resp = client.post(
        "/api/login",
        data=json.dumps({"username": "alice", "password": "SecurePass123"}),
        content_type="application/json",
    )
    assert resp.status_code == 401
    data = resp.get_json()
    assert data["success"] is False
    assert data["requires_biometric"] == "face"


def test_login_with_face_success(client, register_user, sample_face_image):
    reg = register_user(face_image=sample_face_image)
    assert reg.status_code == 201

    resp = client.post(
        "/api/login",
        data=json.dumps({"username": "alice", "password": "SecurePass123", "face_image": sample_face_image}),
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert data["data"]["security_info"]["face_verified"] is True


def test_login_requires_fingerprint_when_enrolled(client, register_user, sample_fingerprint_data):
    reg = register_user(fingerprint_data=sample_fingerprint_data)
    assert reg.status_code == 201

    resp = client.post(
        "/api/login",
        data=json.dumps({"username": "alice", "password": "SecurePass123"}),
        content_type="application/json",
    )
    assert resp.status_code == 401
    data = resp.get_json()
    assert data["requires_biometric"] == "fingerprint"


def test_login_with_fingerprint_success(client, register_user, sample_fingerprint_data):
    reg = register_user(fingerprint_data=sample_fingerprint_data)
    assert reg.status_code == 201

    resp = client.post(
        "/api/login",
        data=json.dumps(
            {
                "username": "alice",
                "password": "SecurePass123",
                "fingerprint_data": sample_fingerprint_data,
            }
        ),
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["success"] is True
    assert data["data"]["security_info"]["fingerprint_verified"] is True

