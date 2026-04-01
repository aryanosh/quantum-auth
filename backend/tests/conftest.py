import json
import os
import tempfile

import pytest


@pytest.fixture(scope="session")
def app_module():
    # Import the module that defines the Flask `app` and the SQLAlchemy `db`.
    # This project uses a module-level app instance (not an app factory).
    import app as app_module  # noqa: E402
    return app_module


@pytest.fixture()
def app(app_module, monkeypatch):
    app = app_module.app
    db = app_module.db

    # Use a temp sqlite file per test for isolation.
    fd, path = tempfile.mkstemp(prefix="qa_test_", suffix=".db")
    os.close(fd)

    app.config.update(
        TESTING=True,
        SQLALCHEMY_DATABASE_URI=f"sqlite:///{path}",
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY="test-secret-key",
    )

    # Make crypto deterministic and independent of liboqs/fernet.
    monkeypatch.setattr(app_module.quantum_crypto, "encrypt", lambda s: s)
    monkeypatch.setattr(app_module.quantum_crypto, "decrypt", lambda s: s)
    monkeypatch.setattr(app_module.quantum_crypto, "pqc_available", False)

    # Avoid MediaPipe/OpenCV work in tests.
    def _fake_face_embedding(_bytes):
        # A stable, normalized-ish vector
        return [0.1, 0.2, 0.3, 0.4]

    monkeypatch.setattr(app_module.biometric_service, "extract_face_embedding", _fake_face_embedding)

    with app.app_context():
        db.drop_all()
        db.create_all()

    yield app

    try:
        os.remove(path)
    except OSError:
        pass


@pytest.fixture()
def client(app):
    return app.test_client()


def _b64img(payload=b"fake-image-bytes"):
    import base64

    return "data:image/jpeg;base64," + base64.b64encode(payload).decode("ascii")


@pytest.fixture()
def sample_face_image():
    return _b64img()


@pytest.fixture()
def sample_fingerprint_data():
    import base64

    return base64.b64encode(b"test_fingerprint_person_A" * 50).decode("ascii")


@pytest.fixture()
def register_user(client):
    def _register(**kwargs):
        body = {
            "username": "alice",
            "email": "alice@example.com",
            "password": "SecurePass123",
            "face_image": None,
            "fingerprint_data": None,
        }
        body.update(kwargs)
        return client.post("/api/register", data=json.dumps(body), content_type="application/json")

    return _register

