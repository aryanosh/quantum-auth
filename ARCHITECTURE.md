## Architecture (Quantum-Inspired Authentication)

### Overview

- **Frontend**: React (routes, auth context, webcam capture UX)
- **Backend**: Flask (JWT auth + biometric verification + PQC/QRNG status)
- **Storage**: SQLAlchemy models (users + WebAuthn credentials)
- **Security**: Argon2 password hashing, encrypted biometric templates, JWT sessions

### Auth flow (register → login → logout)

```mermaid
sequenceDiagram
  participant U as User
  participant FE as Frontend (React)
  participant BE as Backend (Flask)
  participant DB as DB (SQLite/Postgres)

  U->>FE: Register (username/email/password + optional biometrics)
  FE->>BE: POST /api/register
  BE->>BE: Argon2 hash password
  BE->>BE: Extract embedding (face) / template (fingerprint)
  BE->>BE: Encrypt biometric data (Kyber or Fernet fallback)
  BE->>DB: Insert user row
  BE-->>FE: JWT token + user payload

  U->>FE: Login (password)
  FE->>BE: POST /api/login
  alt biometrics enrolled
    BE-->>FE: 401 requires_biometric: face/fingerprint
    FE->>U: prompt webcam / sensor flow
    FE->>BE: POST /api/login (+ biometric payload)
    BE->>BE: Decrypt stored template + compare
  end
  BE-->>FE: JWT token + security_info
  FE->>FE: Store token + show dashboard

  U->>FE: Logout
  FE->>FE: Clear stored token
```

### Biometric enrollment & verification

```mermaid
flowchart LR
  A[Webcam image / fingerprint data] --> B[Feature extraction]
  B --> C[Normalize / template]
  C --> D["Encrypt template (PQC or fallback)"]
  D --> E[(Store in DB)]
  E --> F[Decrypt on login]
  F --> G[Similarity / match scoring]
  G --> H{Threshold pass?}
  H -- No --> I[Reject login]
  H -- Yes --> J[Issue JWT]
```

### PQC / QRNG usage

- **PQC (Kyber KEM)**: used to protect encryption keys when available; otherwise fall back to Fernet.
- **QRNG**: ANU QRNG when available; otherwise use `secrets`-based fallback.
- **Why fallback exists**: to keep the demo runnable on typical machines while still demonstrating the architecture and decision points.

### Why these design choices (portfolio angle)

- **JWT**: straightforward stateless sessions; easy to demo with a dashboard and protected routes.
- **Argon2id**: modern password hashing best-practice.
- **Encrypted biometrics**: avoids storing raw biometric data; matches common privacy expectations.
- **Configurable thresholds**: demonstrates risk tuning and false accept/reject trade-offs.
