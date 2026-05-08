# Quantum-Auth Architecture

Here is a visual architecture diagram for **Quantum-Auth** along with descriptions for the key components and the flow of data.

```mermaid
flowchart TD
    %% Define Styles for better scaling and visuals
    classDef frontend fill:#3b82f6,stroke:#2563eb,stroke-width:2px,color:#fff;
    classDef backend fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff;
    classDef crypto fill:#8b5cf6,stroke:#7c3aed,stroke-width:2px,color:#fff;
    classDef database fill:#f59e0b,stroke:#d97706,stroke-width:2px,color:#fff;

    User([👤 User]) -->|Interacts with| ClientUI

    subgraph Frontend["Frontend Layer (React + Tailwind / JS)"]
        ClientUI["💻 User Interface\n(Captures Credentials & Biometrics)"]:::frontend
        JWTSession["🔑 Local Session Management\n(Stores JWT)"]:::frontend
    end

    ClientUI -->|Auth Request\n(Payload)| APIGateway

    subgraph Backend["Backend Layer (Python)"]
        APIGateway["🌐 API Handlers / Gateway\n(Routes requests)"]:::backend
        SessionControl["🛡️ Session Control\n(Issues & Validates JWTs)"]:::backend
        
        subgraph SecurityCore["Core Security & Identity Engine"]
            AuthEngine["⚙️ Authentication Engine\n(Coordinates verification)"]:::backend
            BiometricVerifier["👁️ Biometric Verification\n(Validates traits)"]:::crypto
            PQCrypto["🔒 Post-Quantum Crypto Techniques\n(Future-proof encryption)"]:::crypto
            Argon2id["🔐 Password Hashing\n(Argon2id)"]:::crypto
        end
    end

    APIGateway --> SessionControl
    APIGateway --> AuthEngine
    AuthEngine <--> BiometricVerifier
    AuthEngine <--> PQCrypto
    AuthEngine <--> Argon2id

    subgraph Storage["Data Persistence Layer"]
        DB[("🗄️ Secure Database\n- Argon2id Password Hashes\n- Encrypted Biometric Templates")]:::database
    end

    AuthEngine -->|Fetches/Compares Data| DB
    SessionControl -.->|Returns JWT upon success| ClientUI
```

### Architectural Description

1. **Frontend Layer (JavaScript - React + Tailwind):**
   - Acts as the presentation layer providing a modern, responsive UI. It captures user input, including traditional credentials and biometric data, securely passing it to the backend. It also handles the local storage and injection of JWTs for subsequent requests.
2. **Backend Layer (Python):**
   - **API Handlers:** The entry point for frontend requests.
   - **Session Control:** Generates and validates **JWT (JSON Web Tokens)** to maintain secure, stateless sessions that scale easily across multiple servers.
   - **Core Security Engine:** This is where the heavy lifting happens. It orchestrates the **Argon2id** hashing for traditional passwords, the **Biometric Verification** module for identity traits, and wraps the sensitive operations using **Post-Quantum Cryptographic techniques** to ensure long-term resistance against future quantum computing attacks.
3. **Data Persistence Layer:**
   - Safely stores user profiles, the salted/hashed Argon2id passwords, and the post-quantum encrypted biometric templates.
