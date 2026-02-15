#!/bin/bash

# Configuration
API_URL="http://localhost:8081"
CSV_FILE="sample_data_drift.csv"

echo "---------------------------------------------------"
echo "Testing FastAPI Endpoints at $API_URL"
echo "---------------------------------------------------"

# 1. Test Single Prediction (/api/predict)
echo ""
echo "1. Testing Single Prediction (/api/predict)..."
echo "Sending JSON payload:"

JSON_PAYLOAD='{
  "user_id": "CLI_User",
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

echo "$JSON_PAYLOAD" | jq . 2>/dev/null || echo "$JSON_PAYLOAD" # Pretty print if jq installed

response=$(curl -s -X POST "$API_URL/api/predict" \
  -H "Content-Type: application/json" \
  -d "$JSON_PAYLOAD")

echo "Response:"
echo "$response" | jq . 2>/dev/null || echo "$response"


# 2. Test Batch Prediction (/predict_batch)
echo ""
echo "---------------------------------------------------"
echo "2. Testing Batch Prediction (/predict_batch)..."

if [ -f "$CSV_FILE" ]; then
    echo "Uploading $CSV_FILE..."
    # Note: The API expects the file field name to be 'file'
    response=$(curl -s -X POST "$API_URL/predict_batch" \
      -H "accept: application/json" \
      -H "Content-Type: multipart/form-data" \
      -F "file=@$CSV_FILE;type=text/csv")
    
    echo "Response (First 500 chars):"
    echo "$response" | cut -c 1-500
    echo "..."
else
    echo "Error: $CSV_FILE not found. Run generate_drift_data.py first."
fi

echo ""
echo "---------------------------------------------------"
echo "Done."
