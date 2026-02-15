FROM python:3.10-slim
LABEL author=${AUTHOR}
# Install system dependencies for ML libraries (CatBoost needs libgomp1)
RUN apt-get update && apt-get install -y libgomp1 && rm -rf /var/lib/apt/lists/*

WORKDIR /services

COPY requirements.txt .

RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

EXPOSE ${APP_PORT}

CMD uvicorn ml_service.predict_price:app --port ${APP_PORT} --host 0.0.0.0