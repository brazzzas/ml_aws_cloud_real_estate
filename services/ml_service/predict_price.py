from .handler import FastApiHandler
from fastapi import FastAPI
from sklearn import set_config
set_config(transform_output="pandas")
from prometheus_fastapi_instrumentator import Instrumentator
from prometheus_client import Histogram
from prometheus_client import Counter

from pydantic import BaseModel
from fastapi import UploadFile, File
import pandas as pd

class RealEstateAttributes(BaseModel):
    build_year: int
    building_type_int: int
    ceiling_height: float
    flats_count: int
    floors_total: int
    has_elevator: int
    floor: int
    is_apartment: int
    kitchen_area: float
    living_area: float
    rooms: int
    total_area: float
    district: str

class PredictionRequest(BaseModel):
    user_id: str
    model_params: RealEstateAttributes

    # Swagger example configuration
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "user_id": "User_12345",
                    "model_params": {
                        "build_year": 1965,
                        "building_type_int": 6,
                        "ceiling_height": 2.64,
                        "flats_count": 84,
                        "floors_total": 12,
                        "has_elevator": 1,
                        "floor": 9,
                        "is_apartment": 0,
                        "kitchen_area": 9.9,
                        "living_area": 19.9,
                        "rooms": 1,
                        "total_area": 35.1,
                        "district": "Ryazansky District"
                    }
                }
            ]
        }
    }


app = FastAPI()
app.handler = FastApiHandler()

instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app)


my_buckets = list(range(10_000_000, 52_000_000, 2_000_000))
my_buckets.append(float("inf"))

prediction_bucket = Histogram(
    # metric name
    "price_histogram",
    # metric description
    "Real estate prices by buckets",
    buckets = my_buckets
)

inference_counter = Counter(
    # metric name
    "positive_counter",
    # description
    "number of inferences made"
)

@app.post("/predict")
def get_prediction(request: PredictionRequest):
    """
    Function to predict apartment price

    Args:
        user_id (str): User ID
        model_params (dict): real estate object parameters
    """
    all_params = {
        "user_id": request.user_id,
        "model_params": request.model_params.model_dump()
    }
    result = app.handler.handle(all_params)
    predicted_price = result.get('predicted_price')
    prediction_bucket.observe(predicted_price)
    inference_counter.inc()
    
    return result

@app.post("/predict_batch")
async def predict_batch(file: UploadFile = File(...)):
    if not file.filename.endswith(".csv"):
        return {"error": "Only CSV files are allowed"}

    try:
        df = pd.read_csv(file.file)
        predictions = app.handler.predict_batch(df)
        
        # Add predictions to the DataFrame
        df['predicted_price'] = predictions
        
        # Return as JSON records or you could return a CSV file
        return df.to_dict(orient="records")
    except Exception as e:
        return {"error": f"Failed to process file: {str(e)}"}