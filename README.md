# CyberPulse 

### Real-Time Security Log Analytics with AI-Driven Threat Intelligence

CyberPulse is a security log analytics system designed to ingest security events, detect suspicious activities, generate alerts, and provide AI-assisted threat analysis. It combines a FastAPI backend, a React frontend, Elasticsearch, Redis, PostgreSQL, and a locally hosted LLM through Ollama.

The system demonstrates how real-time security event processing and AI-assisted investigation can support security monitoring and incident response.

---

## 📌 Features

* **Security Log Ingestion:** Accepts security logs through REST APIs.
* **Authentication:** Provides user registration, login, and JWT-based authentication.
* **Log Indexing:** Stores security logs in Elasticsearch for searching and retrieval.
* **Real-Time Event Streaming:** Publishes incoming security events to Redis Streams.
* **Threat Detection:** Identifies suspicious activities using rule-based and behavior-based detection.
* **Alert Management:** Stores detected alerts in PostgreSQL and supports status updates.
* **AI-Assisted Investigation:** Uses a locally hosted LLM to analyze alerts and suggest response actions.
* **Web Interface:** Provides a React frontend for interacting with the application.
* **Containerized Infrastructure:** Uses Docker Compose to run the supporting services.

---

## 🏗️ System Architecture

```text
                 ┌─────────────────────┐
                 │    React Frontend   │
                 └──────────┬──────────┘
                            │ REST API
                            ▼
                 ┌─────────────────────┐
                 │   FastAPI Backend   │
                 │                     │
                 │ Authentication      │
                 │ Log Ingestion       │
                 │ Alert Management    │
                 └──────┬───────┬──────┘
                        │       │
               ┌────────▼─┐  ┌──▼────────────┐
               │Elasticsearch│ │ Redis Streams│
               │ Log Storage │ │ Event Queue  │
               └────────────┘ └──────┬───────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │ Detection Engine│
                            └────────┬────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │   PostgreSQL    │
                            │  Alert Storage  │
                            └────────┬────────┘
                                     │
                                     ▼
                            ┌─────────────────┐
                            │  Ollama / LLM   │
                            │  Alert Analysis │
                            └─────────────────┘
```

*Note: This is a conceptual architecture. Ollama is called by the backend's AI analysis service when alert analysis is requested. The detection engine processes Redis events separately from the FastAPI request flow.*

---

## 🧰 Technology Stack

| Component       | Technology             | Purpose                                         |
| --------------- | ---------------------- | ----------------------------------------------- |
| Frontend        | React, JavaScript      | User interface                                  |
| Backend         | Python, FastAPI        | REST API and application logic                  |
| Authentication  | JWT, bcrypt            | Token-based authentication and password hashing |
| Log Storage     | Elasticsearch          | Indexing and searching security logs            |
| Event Streaming | Redis Streams          | Passing events to the detection engine          |
| Alert Storage   | PostgreSQL             | Persisting detected alerts and their statuses   |
| AI Analysis     | Ollama, Llama 3.1      | Local AI-assisted alert analysis                |
| Infrastructure  | Docker, Docker Compose | Running supporting services                     |

---

## 📁 Project Structure

```text
CyberPulse/
├── backend/
│   ├── app/
│   │   ├── core/
│   │   │   ├── auth.py
│   │   │   └── connections.py
│   │   ├── models/
│   │   │   └── log.py
│   │   ├── routes/
│   │   │   ├── auth.py
│   │   │   ├── logs.py
│   │   │   └── alerts.py
│   │   ├── services/
│   │   │   ├── detection_engine.py
│   │   │   └── ai_analyzer.py
│   │   ├── __init__.py
│   │   └── main.py
│   └── requirements.txt
├── frontend/
│   ├── public/
│   ├── src/
│   ├── package.json
│   └── package-lock.json
├── docker-compose.yml
├── .env.example
├── .gitignore
└── README.md
```

*The structure above shows the main project files. Your actual repository may contain additional files.*

---

## ⚙️ Prerequisites

Install the following before running CyberPulse:

* Python 3.11 or a compatible version
* Node.js and npm
* Docker Desktop with Docker Compose
* Ollama
* Git

Check your installations:

```bash
python3 --version
node --version
npm --version
docker --version
docker compose version
ollama --version
```

---

## 🚀 Installation and Setup

### 1. Clone the Repository

```bash
git clone <YOUR_GITHUB_REPOSITORY_URL>
cd CyberPulse
```

Replace `<YOUR_GITHUB_REPOSITORY_URL>` with your repository URL.

### 2. Configure Environment Variables

Create a local `.env` file in the project root using `.env.example` as a template.

Example `.env.example`:

```env
JWT_SECRET=replace_with_a_long_random_secret
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60
```

Copy the template:

```bash
cp .env.example .env
```

Replace the placeholder secret in `.env` with a strong, randomly generated value. Never commit your actual `.env` file or production secrets.

Ensure the backend loads the environment variables from the location expected by your configuration.

### 3. Start the Docker Services

From the project root:

```bash
docker compose up -d
```

Check the service status:

```bash
docker compose ps
```

View logs if a service fails to start:

```bash
docker compose logs
```

The Docker Compose configuration should define the Elasticsearch, Redis, and PostgreSQL services and their required ports and credentials.

Expected host ports in the current development configuration:

| Service       | Host Port |
| ------------- | --------: |
| Elasticsearch |      9200 |
| Redis         |      6379 |
| PostgreSQL    |      5433 |

Verify these values against your `docker-compose.yml`.

### 4. Verify the Infrastructure

**Elasticsearch**

```bash
curl http://localhost:9200
```

**Redis**

```bash
docker exec cyberpulse-redis redis-cli ping
```

Expected response:

```text
PONG
```

**PostgreSQL**

```bash
docker exec -it cyberpulse-postgres psql -U cyberpulse -d cyberpulse
```

If your container, database, or user names differ, use the values in `docker-compose.yml`.

### 5. Set Up the Python Environment

The Python virtual environment is intentionally excluded from the repository. Create a new one locally:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Install the backend dependencies:

```bash
pip install -r backend/requirements.txt
```

If the virtual environment already exists, activate it instead of recreating it.

### 6. Start the Backend

```bash
cd backend
../.venv/bin/python -m uvicorn app.main:app --reload
```

The API should be available at:

* API base URL: `http://localhost:8000`
* Interactive Swagger documentation: `http://localhost:8000/docs`
* ReDoc documentation: `http://localhost:8000/redoc`

Use the Swagger documentation to register a user, log in, authorize requests, submit logs, and interact with alerts.

### 7. Set Up Ollama

Install Ollama if it is not already installed, then download the configured model:

```bash
ollama pull llama3.1:8b
```

Ensure Ollama is running and the model is available:

```bash
ollama list
```

The current AI analysis service expects Ollama at:

```text
http://localhost:11434/api/generate
```

and uses the model name:

```text
llama3.1:8b
```

Make sure these match your backend configuration.

### 8. Start the Detection Engine

Open a **separate terminal** from the project root:

```bash
source .venv/bin/activate
cd backend
python -c "from app.services.detection_engine import process_events; process_events()"
```

Keep this terminal running while testing log ingestion and detection.

The detection engine reads events from Redis Streams, evaluates the configured rules, and stores generated alerts in PostgreSQL.

### 9. Start the React Frontend

Open another terminal:

```bash
cd frontend
npm install
npm start
```

`npm install` recreates the ignored `node_modules/` directory using `package.json` and `package-lock.json`.

For a Create React App frontend, the development server typically runs at:

```text
http://localhost:3000
```

If the frontend uses Vite instead, use its configured command, typically `npm run dev`.

Ensure the frontend's API configuration points to the backend at `http://localhost:8000` and that CORS is configured appropriately in FastAPI.

---

## 🔐 Authentication

CyberPulse uses JWT-based authentication.

### Register

**Endpoint:** `POST /auth/register`

Example request body:

```json
{
  "username": "security_user",
  "email": "security@example.com",
  "password": "ChangeThisPassword123!"
}
```

Use a unique email and username when registering. The actual required fields and response depend on the backend implementation.

### Login

**Endpoint:** `POST /auth/login`

The current backend uses form data for login, with fields named `username` and `password`, rather than a JSON request body.

A successful login returns an access token. Use this token to authorize protected requests.

In Swagger:

1. Open `/docs`.
2. Register a user if needed.
3. Use the login endpoint to obtain a token.
4. Click **Authorize** and enter the credentials or bearer token as required by the Swagger configuration.
5. Execute protected endpoints.

The token expires according to `JWT_EXPIRATION_MINUTES`; log in again when it expires.

---

## 📥 Security Log Ingestion

**Endpoint:** `POST /logs`

The endpoint accepts security log data, indexes it in Elasticsearch, and publishes it to the Redis Stream `security-events`.

Example request:

```json
{
  "timestamp": "2026-10-07T10:30:00Z",
  "source": "firewall",
  "source_ip": "10.20.30.80",
  "destination_ip": "192.168.1.10",
  "destination_port": 22,
  "event_type": "failed_login",
  "severity": "high",
  "message": "Multiple failed login attempts detected"
}
```

The timestamp should be a valid datetime, and severity must be one of the values supported by the API: `low`, `medium`, `high`, or `critical`.

A successful ingestion response includes the status and the Elasticsearch document ID.

---

## 🚨 Threat Detection and Alerts

The detection engine consumes security events from Redis Streams and applies configured detection rules.

Examples of supported detection scenarios include:

* **Brute-force activity:** Repeated failed login attempts from a source within a time window.
* **Port scanning:** Connections to multiple distinct destination ports within a time window.
* **Explicit threat events:** Rules for events such as `brute_force_attempt`, `port_scan`, `malware_detected`, and `unauthorized_access`.

The exact thresholds and time windows are defined in the detection engine's implementation.

Detected alerts are stored in PostgreSQL for retrieval and status management.

### Alert API

| Method | Endpoint                                  | Purpose                  |
| ------ | ----------------------------------------- | ------------------------ |
| GET    | `/alerts`                                 | Retrieve alerts          |
| PATCH  | `/alerts/{alert_id}?status=investigating` | Update an alert's status |

Supported alert statuses in the current implementation are:

* `open`
* `investigating`
* `resolved`

These endpoints require authentication if protected by the backend's JWT dependency configuration.

---

## 🤖 AI-Assisted Alert Analysis

CyberPulse integrates a locally hosted LLM through Ollama.

The AI analysis service receives an alert's threat type, severity, source IP, and message. It generates a concise analysis covering:

1. What the threat means.
2. Why the activity is suspicious.
3. Recommended immediate actions.

The service uses the configured Llama 3.1 model through the local Ollama API.

AI output is advisory. Recommendations should be reviewed by a security analyst before any operational response is taken.

---

## 🗄️ Data Storage

### Elasticsearch

Stores indexed security logs in the `security-logs` index. It supports searching and inspecting ingested security events.

Check the index:

```bash
curl "http://localhost:9200/security-logs/_search?pretty"
```

### Redis Streams

The `security-events` stream carries events from the ingestion API to the detection engine.

Inspect stream entries from the Redis container:

```bash
docker exec -it cyberpulse-redis redis-cli XRANGE security-events - +
```

### PostgreSQL

Stores application data such as registered users and detected alerts, according to the database schema.

Connect to the database:

```bash
docker exec -it cyberpulse-postgres psql -U cyberpulse -d cyberpulse
```

Inside `psql`, list tables:

```sql
\dt
```

---

## 🧹 Keeping the Repository Lightweight

CyberPulse does not require committing local dependency folders. Git should track source code and dependency manifests, not generated environments.

Recommended `.gitignore`:

```gitignore
# Python virtual environments
.venv/
venv/

# Secrets and local environment
.env

# Python cache
__pycache__/
*.py[cod]

# Node.js dependencies
node_modules/

# Frontend build output
build/
dist/

# macOS
.DS_Store
```

**Do not upload:**

* `.venv/` — the local Python virtual environment.
* `node_modules/` — installed npm dependencies.
* `.env` — local configuration and secrets.
* Generated caches and build output.

**Do upload:**

* `backend/` source code and `backend/requirements.txt`.
* `frontend/` source code, `package.json`, and `package-lock.json`.
* `docker-compose.yml`.
* `.env.example` with placeholders only.
* `.gitignore`.
* `README.md`.

Anyone cloning the project can recreate the Python environment with `python3 -m venv` and `pip install -r backend/requirements.txt`, and recreate the frontend dependencies with `npm install`.

If either dependency directory was already tracked by Git, adding it to `.gitignore` is not enough. Remove it from Git's index while keeping your local files:

```bash
git rm -r --cached .venv frontend/node_modules
```

Run this only for paths that are tracked. Then inspect the changes with:

```bash
git status
```

---

## 🛠️ Troubleshooting

### Backend cannot connect to Elasticsearch, Redis, or PostgreSQL

* Check that Docker services are running with `docker compose ps`.
* Confirm host ports and credentials in `docker-compose.yml` and backend connection settings.
* Remember that host applications use published host ports; applications running inside Docker generally need service names and container ports instead.

### Login returns an authentication error

* Register a user before logging in.
* Confirm that login uses form data with `username` and `password`.
* Check that the backend has loaded the correct JWT secret.
* Log in again if the token has expired.

### No alerts appear after submitting logs

* Confirm that the POST `/logs` request succeeded.
* Check that the Redis `security-events` stream receives events.
* Ensure the detection engine is running in its separate terminal.
* Check the detection rules, event type, thresholds, and PostgreSQL connection.

### AI analysis fails

* Verify that Ollama is running.
* Confirm that `llama3.1:8b` is installed using `ollama list`.
* Check that the configured Ollama URL is reachable and matches `ai_analyzer.py`.

### Frontend cannot reach the backend

* Confirm that FastAPI is running on port `8000`.
* Check the frontend API base URL.
* Confirm that FastAPI CORS settings allow the frontend's origin.

---

## 🛑 Stopping the Project

Stop the FastAPI server and detection engine with `Ctrl+C` in their respective terminals. Stop the React development server with `Ctrl+C` as well.

To stop the Docker services:

```bash
docker compose down
```

This stops and removes the containers created by Compose. Persistent database data may remain in Docker volumes.

---

## 🔮 Future Improvements

Potential enhancements include:

* Persisting AI analysis so repeated alert retrieval does not trigger repeated model calls.
* Adding richer threat correlation and configurable detection thresholds.
* Improving alert filtering, search, and dashboard visualizations.
* Adding role-based access control and audit trails.
* Improving deployment configuration, observability, and automated testing.
* Adding automated tests for API endpoints and detection rules.

---

## 👩‍💻 Project Status

CyberPulse is a development-stage security analytics project combining log ingestion, event streaming, rule-based threat detection, alert storage, JWT authentication, and AI-assisted alert analysis.

Features and setup instructions may evolve as implementation progresses.

---

## 📄 License

Add a license before redistributing the project publicly. If no license is included, standard copyright restrictions apply.
