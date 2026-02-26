# MLE Project — Real Estate Price Prediction

This project is a production-ready Machine Learning service for predicting real estate prices. It is designed to be deployed on **AWS EC2** using **Docker Compose** for a unified, scalable environment.

## 🚀 Features

*   **ML Prediction Model**: Trained on real estate data (CatBoost / Linear Regression) to estimate property prices based on features like area, room count, and building year.
*   **Streamlit UI**: A user-friendly web interface for uploading CSV files and getting batch predictions with interactive data visualization.
*   **FastAPI Backend**: A robust REST API serving the model, supporting both single-item and batch predictions.
*   **Monitoring Stack**: Integrated **Prometheus** and **Grafana** for validating model performance and system health in real-time.
*   **Nginx Reverse Proxy**: Single entry point (Port 80) routing traffic to all services securely.

## 🏗️ Architecture

```mermaid
graph LR
    Client([Browser / cURL]) --> Nginx

    subgraph Docker Compose
        Nginx[Nginx :80]
        Frontend[Streamlit :8501]
        Backend[FastAPI :8081]
        Prometheus[Prometheus :9090]
        Grafana[Grafana :3000]
        Model[(CatBoost Model)]

        Nginx -- "/" --> Frontend
        Nginx -- "/api/" --> Backend
        Nginx -- "/monitor/" --> Grafana

        Backend --> Model
        Frontend -- "POST /predict_batch" --> Backend
        Prometheus -- "scrape /metrics" --> Backend
        Grafana -- "query" --> Prometheus
    end
```

## 📂 Project Structure

```
mle-project-sprint-3-v001/
├── docker-compose.yml          # Orchestrates all services
├── nginx.conf                  # Reverse proxy configuration
├── .env                        # Environment variables (credentials)
│
├── frontend/                   # Streamlit Web UI
│   ├── Dockerfile
│   ├── app.py                  # Main Streamlit application
│   └── requirements.txt
│
├── services/                   # Backend API + ML Model
│   ├── Dockerfile
│   ├── requirements.txt        # Python dependencies (pinned)
│   ├── ml_service/             # Core application package
│   │   ├── handler.py          # Model loading & prediction logic
│   │   └── predict_price.py    # FastAPI routes & Prometheus metrics
│   ├── models/model/           # Trained model artifact (model.pkl)
│   └── prometheus/
│       └── prometheus.yml      # Prometheus scrape config
│
├── utils/                      # Utility scripts for testing & traffic
│   ├── generate_drift_data.py  # Generates sample CSV with drift/errors
│   ├── imitation.py            # Load-test script (generates traffic)
│   └── test_api.sh             # Shell script for API smoke tests
│
├── sample_data.csv             # Normal sample data for batch prediction
├── sample_data_drift.csv       # Drift sample data for testing
├── dashboard.json              # Grafana dashboard export
├── dashboard.jpg               # Grafana dashboard screenshot
│
├── README.md                   # This file
├── Instructions.md             # API usage guide with cURL examples
└── Monitoring.md               # Dashboard metrics documentation
```

## 🛠️ Tech Stack

*   **Language**: Python 3.10
*   **ML Framework**: Scikit-Learn / CatBoost / MLflow
*   **Web**: FastAPI (Backend), Streamlit (Frontend), Nginx
*   **DevOps**: Docker, Docker Compose, AWS EC2
*   **Monitoring**: Prometheus, Grafana

## 📦 Services

| Service | Port (Internal) | URL (Public via Nginx) | Description |
| :--- | :--- | :--- | :--- |
| **Frontend** | `8501` | `http://<HOST>/` | Main Web UI |
| **Backend** | `8081` | `http://<HOST>/api/docs` | API Documentation (Swagger) |
| **Grafana** | `3000` | `http://<HOST>/monitor/` | Monitoring Dashboards (Login: `admin`/`admin`) |
| **Prometheus** | `9090` | internal only | Metrics Collection |

## 🚦 How to Run

### 1. Start All Services
```bash
docker compose up -d --build
```
> **Note:** Run this command from the project root without specifying a service name to launch the full stack (Frontend, Backend, Monitoring).

### 2. Access the Application
Open your browser and navigate to `http://localhost/` (or your EC2 Public IP).

## 🧰 Utility Scripts

The project includes several built-in scripts to help test functionality and simulate traffic for the monitoring stack:

### `utils/generate_drift_data.py`
A python script used to generate a mock dataset (`sample_data_drift.csv`) for testing. 
* **Purpose:** This file randomly generates "Normal" predictions, "Luxury/Drift" data (abnormally large areas/rooms), and "Errors" (negative areas, future build years). 
* **Usage:** Run `python utils/generate_drift_data.py` to recreate the drift dataset. You can feed this dataset to the batch prediction endpoint to see how the model behaves when given extreme outliers. 

### `utils/test_api.sh`
A quick smoke-testing shell script for verifying system health.
* **Purpose:** Programmatically sends a simulated JSON payload to the `/predict` endpoint, and uploads the `.csv` generated by `generate_drift_data.py` to the `/predict_batch` endpoint. 
* **Usage:** Run `sh utils/test_api.sh` to quickly verify that both the Backend API and the Nginx routing are functioning properly.

### `utils/imitation.py`
A load-testing script to populate monitoring dashboards.
* **Purpose:** Runs a continuous `while True` loop sending random prediction requests (some succeeding, some intentionally broken) to generate active traffic.
* **Usage:** Use this to fill **Grafana** with live data: run `python utils/imitation.py`.

## 📡 API Usage & Integration

The service exposes a JSON API for programmatic access.
For detailed `curl` examples and integration guides, see **[Instructions.md](Instructions.md)**.

## 📊 Monitoring

The system includes a Prometheus + Grafana monitoring stack for tracking service health and data drift.
For detailed dashboard documentation, see **[Monitoring.md](Monitoring.md)**.
