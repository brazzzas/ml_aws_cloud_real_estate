# MLE Project Instructions

## 📡 API Usage Guide

The backend provides a REST API for making predictions programmatically.

### Base URL
*   **Local**: `http://localhost/api`
*   **AWS EC2**: `http://<PUBLIC-IP>/api`

---

### 1. Single Prediction
Make a prediction for a single apartment object via `POST /predict`.

**Request (cURL):**
```bash
curl -X 'POST' \
  'http://localhost/api/predict' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{
  "user_id": "cli_user",
  "model_params": {
    "build_year": 2005,
    "building_type_int": 3,
    "ceiling_height": 2.8,
    "flats_count": 50,
    "floors_total": 15,
    "has_elevator": 1,
    "floor": 7,
    "is_apartment": 0,
    "kitchen_area": 12.0,
    "living_area": 25.0,
    "rooms": 2,
    "total_area": 55.0,
    "district": "Central"
  }
}'
```

---

### 2. Batch Prediction
Upload a CSV file containing multiple objects to `POST /predict_batch`.

**CSV Format:**
The CSV should contain columns matching the model features (e.g., `total_area`, `rooms`, `kitchen_area`, etc.). See `sample_data.csv` for a template.

**Request (cURL):**
```bash
curl -X 'POST' \
  'http://localhost/api/predict_batch' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'file=@sample_data.csv;type=text/csv'
```

---

## 📊 Monitoring (Prometheus & Grafana)

The system includes a monitoring stack to track service health and data drift.

1.  **Access Grafana**: `http://localhost/monitor/`
2.  **Login**: Default credentials are `admin` / `admin`.
3.  **Dashboards**:
    *   Navigate to **Dashboards** -> **General** to see pre-configured panels.
    *   Metrics include Request Count, Latency, and potentially custom model metrics (if configured).

**Troubleshooting Monitoring:**
If you cannot access Grafana:
1.  Ensure all containers are running:
    ```bash
    docker compose ps
    ```
2.  If `ml_grafana` or `ml_prometheus` are missing, restart the *entire* stack:
    ```bash
    docker compose up -d --build
    ```