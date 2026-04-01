## 🛡️ Quantum-Inspired Authentication

**Post-Quantum Cryptography (PQC)** meets **Biometric Multi-Factor Auth**.

A full-stack authentication ecosystem designed to showcase **defense-in-depth engineering**. This project implements a multi-stage verification pipeline combining modern password hashing, facial biometric landmarks, and a fallback strategy for Post-Quantum Cryptography (PQC).

[View Architecture Deep-Dive](ARCHITECTURE.md) · Explore API Docs (see **Key endpoints** below)

---

## 🚀 The Mission

In a world approaching **“Q-Day,”** standard RSA/ECC encryption becomes vulnerable. This project is a technical proof-of-concept for **Hybrid Security**:

- **Classical hardening**: Argon2id (Password Hashing Competition winner) for password storage.
- **Biometric layer**: real-time facial landmark analysis via MediaPipe.
- **Future-proofing**: PQC concepts (CRYSTALS-Kyber) to secure the data protection layer (with fallback for compatibility).

---

## ✨ Key Features

- **Multi-step adaptive auth**: users are prompted for biometrics only after primary credentials succeed, minimizing friction.
- **Biometric integrity**: MediaPipe Face Mesh landmarks; biometric templates are encrypted before storage.
- **Entropy-as-a-service**: integrates ANU Quantum Random Number Generation (QRNG) for high-entropy operations (with secure local fallback).
- **Security-first UX**: protected routes, JWT session persistence, and real-time webcam quality feedback.

---

## 🛠️ Tech Stack

| Layer | Technologies |
|------|--------------|
| Frontend | React 18, TailwindCSS, Lucide Icons |
| Backend | Flask (Python), SQLAlchemy, PyJWT |
| Security | Argon2id, liboqs (Kyber) + Fernet fallback |
| AI / Vision | MediaPipe (Face Mesh), NumPy |
| Database | SQLite (dev) / PostgreSQL-ready |

---
---

## ⚙️ System Design & Security Trade-offs

- **Why Flask?** Lightweight footprint and precise control over the cryptographic/verification pipeline.
- **Stateless vs. stateful sessions**: currently uses stateless JWTs for simplicity and scalability. Roadmap includes a **Redis-backed revocation list** for production.
- **PQC fallback**: if `liboqs` is unavailable, the system gracefully falls back to **Fernet** to keep the demo runnable.

---

## 🏗️ Installation & Setup

### 1) Backend (Security Core)

```bash
cd backend
python -m venv venv

# Activate venv (Windows: venv\Scripts\activate | Unix: source venv/bin/activate)
pip install -r requirements.txt
python app.py
```

### 2) Frontend (User Interface)

```bash
cd frontend
npm install
npm start
```

`REACT_APP_API_URL` defaults to `http://localhost:5000/api`.

> Windows note: Python **3.11 / 3.12** is recommended. Very new Python versions may fail due to missing wheels for scientific dependencies (NumPy/MediaPipe).

---

## 🧪 Quality Assurance

Reliability is a feature. This project includes backend tests for key auth flows and biometric threshold behavior.

```bash
# Run Backend Tests
cd backend
pip install -r requirements-dev.txt
pytest -q
pytest --cov=. --cov-report=term-missing

# Run Frontend Tests
cd ../frontend
npm test -- --watchAll=false
```

---

## Key endpoints

- `GET /api/health`
- `POST /api/register`
- `POST /api/login` (may return `requires_biometric`)
- `GET /api/user` (Bearer token)

---

## 🛣️ Roadmap & Limitations

- [Done] Argon2id password hashing
- [Done] MediaPipe face enrollment
- [In progress] OIDC (OpenID Connect) compatibility
- [Planned] Hardware security key (WebAuthn/FIDO2) integration
- [Note] Fingerprint verification is simulated for UI demonstration (plus optional WebAuthn support)

---

## 📄 License

MIT

---
