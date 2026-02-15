# MLE Project - Real Estate Price Prediction (Sprint 3)

This project is a production-ready Machine Learning service for predicting real estate prices. It is designed to be deployed on **AWS EC2** using **Docker Compose** for a unified, scalable environment.

## 🚀 Features

*   **ML Prediction Model**: trained on real estate data (CatBoost/Linear Regression) to estimate property prices based on features like area, room count, and building year.
*   **Streamlit UI**: A user-friendly web interface for uploading CSV files and getting batch predictions with interactive data visualization.
*   **FastAPI Backend**: A robust REST API serving the model, supporting both single-item and batch predictions.
*   **Monitoring Stack**: Integrated **Prometheus** and **Grafana** for validatihng model performance and system health in real-time.
*   **Nginx Reverse Proxy**: Single entry point (Port 80) routing traffic to all services securely.

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
| **Prometheus** | `9090` | `internal only` | Metrics Collection |

## 🚦 How to Run

### 1. Start All Services
```bash
docker compose up -d --build
```
*Note: Ensure you run this command without specifying a service name to launch the full stack (Frontend, Backend, Monitoring).*

### 2. Access the Application
Open your browser and navigate to `http://localhost/` (or your EC2 Public IP).

## 📡 API Usage & Integration

The service exposes a JSON API for programmatic access.
For detailed `curl` examples and integration guides, please refer to **[Instructions.md](Instructions.md)**.
