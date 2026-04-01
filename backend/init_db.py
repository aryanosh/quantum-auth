from app import app, db
from models import WebAuthnCredential

with app.app_context():
    db.create_all()
    print("Database tables created successfully including WebAuthnCredential")
