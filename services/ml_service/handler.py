from catboost import CatBoostRegressor
import mlflow
import pandas as pd
from sklearn import set_config
set_config(transform_output="pandas")
import os

import sklearn
print(f"Server Sklearn Version: {sklearn.__version__}")



class FastApiHandler:
    """FastApiHandler class that processes the request and returns the price prediction for the real estate service"""

    def __init__(self):
        """Class variable initialization"""

        self.param_types = {
            'user_id': str,
            'model_params': dict
        }

        current_dir = os.path.dirname(os.path.abspath(__file__))
        service_root = os.path.dirname(current_dir)
        self.model_path = os.path.join(service_root, "models", "model")

        # self.model_path = "models/model/"
        self.load_model(model_path=self.model_path)
        self.required_params = ['build_year', 'building_type_int', 'ceiling_height', 'flats_count', 'floors_total',
                                'has_elevator', 'floor', 'is_apartment', 'kitchen_area', 'living_area', 'rooms', 'total_area',
                                'district']
        
    def load_model(self, model_path:str):
        """Loads model from MLflow."""
        try:
            # 1. Load
            loaded_object = mlflow.sklearn.load_model(model_path)
            
            if hasattr(loaded_object, 'best_estimator_'):
                 self.model = loaded_object.best_estimator_
            else:
                 self.model = loaded_object

            # 2. Determine what we are working with (Pipeline or TransformedTargetRegressor)
            pipeline_obj = self.model
            if hasattr(self.model, 'regressor_'):
                pipeline_obj = self.model.regressor_

            # 3. Patch broken ManualMathFeatures with SafeMathFeatures
            if hasattr(pipeline_obj, 'steps'):
                try:
                    # Check if step 3 is math_features
                    if len(pipeline_obj.steps) > 3 and pipeline_obj.steps[3][0] == 'math_features':
                        print("Patching broken ManualMathFeatures with SafeMathFeatures...")
                        # Replace the step. Modifying the list in place.
                        pipeline_obj.steps[3] = ('math_features', SafeMathFeatures())
                    
                    # Check for 'selector' step (usually around index 4 or 5) and remove it
                    # We look for step named 'selector'
                    selector_index = -1
                    for i, (name, step) in enumerate(pipeline_obj.steps):
                        if name == 'selector':
                            selector_index = i
                            break
                    
                    if selector_index != -1:
                         print(f"Removing broken 'selector' step at index {selector_index}...")
                         pipeline_obj.steps.pop(selector_index)

                except Exception as e:
                    print(f"Failed to patch model: {e}")

            # 4. Carefully iterate through pipeline steps
            if hasattr(pipeline_obj, 'steps'):
                print("Configuring pipeline steps...")
                for name, step in pipeline_obj.steps:
                    # Try to enable pandas only for steps that support it
                    if hasattr(step, 'set_output'):
                        try:
                            step.set_output(transform="pandas")
                        except Exception:
                            # If it's ManualMathFeatures and it doesn't support set_output — just skip it
                            print(f"Step '{name}' does not support set_output — skipping.")
            else:
                # If it's not a pipeline, but a single model
                if hasattr(pipeline_obj, 'set_output'):
                    try:
                        pipeline_obj.set_output(transform="pandas")
                    except Exception:
                        pass
                
            print("Model loaded successfully (with patch and Pandas configuration)")

        except Exception as e:
            print(f'CRITICAL: Failed to load the model: {e}')
            raise e
    
    def predict_price(self, model_params: dict) -> float:
        X = pd.DataFrame([model_params])[self.required_params]
        return float(self.model.predict(X)[0])
    
    def predict_batch(self, data: pd.DataFrame) -> list:
        """
        Process batch predictions for a pandas DataFrame.
        This method assumes the DataFrame already has the correct columns.
        Missing columns will be filled with 0 or handled by the model if robust.
        """
        # Ensure we only use required columns, adding missing ones if necessary
        for col in self.required_params:
            if col not in data.columns:
                data[col] = 0 # or some default value
        
        # Filter to only required columns to match model expectation
        X = data[self.required_params]
        
        # Predict
        predictions = self.model.predict(X)
        return predictions.tolist()
    
    def check_required_query_params(self, query_params):
        """
        Docstring for check_required_query_params
        
        :returns: True - if all needed params (user_id + model_params) are present, False - otherwise
        :param query_params: dict
        """
        if "user_id" not in query_params or "model_params" not in query_params:
            return False
        
        if not isinstance(query_params["user_id"], self.param_types["user_id"]):
            return False 
        
        if not isinstance(query_params["model_params"], self.param_types["model_params"]):
            return False
        return True
    
    def check_required_model_params(self, model_params: dict) -> bool:
        """
        Docstring for check_required_model_params
        
        :param model_params: check if necessary params are present
        """
        # Implement possibility to check for required keys and keep only them
        # Allows script to work even if extra params are provided
        filtered_model_params = {k: model_params[k] for k in model_params if k in self.required_params}
        if set(filtered_model_params) == set(self.required_params):
            return True
        return False
    
    def validate_params(self, params: dict) -> dict:
        """
        Combined function checks parameters of both request and model
        """
        if self.check_required_query_params(params):
            print("All query params exists")
        else:
            print("Not all query params exists")
            return False

        if self.check_required_model_params(params['model_params']):
            print("All required model params exist")
        else:
            print('There are missing model params')
            return False
        return True
    
    def handle(self, params):
        """ Function for handling incoming API requests.
            Request consists of parameters.
        """
        try:
            if not self.validate_params(params):
                print("Error while handling request")
                response = {"Error": "Problem with parameters"}
            else:
                model_params = params['model_params']
                user_id = params['user_id']
                print(f'Predicting for user_id: {user_id} and model_params:\n{model_params}')
                predicted_price = self.predict_price(model_params)
                response = {
                    "user_id": user_id,
                    "predicted_price": predicted_price
                }
        except Exception as e:
            print(f"Error while handling request: {e}")
            return {"Error": "Problem with the request"}
        else:
            return response


from sklearn.base import BaseEstimator, TransformerMixin
import numpy as np

class SafeMathFeatures(BaseEstimator, TransformerMixin):
    def fit(self, X, y=None):
        return self
    
    def transform(self, X):
        # Ensure X is DataFrame. If numpy, convert?
        # Ideally we assume pandas input from previous steps
        df = X.copy() if hasattr(X, 'copy') else pd.DataFrame(X)
        
        # Calculate features identified as missing
        # 'total_area**2/kitchen_area'
        df['total_area**2/kitchen_area'] = df['total_area']**2 / df['kitchen_area']
        
        # 'ceiling_height**2*sqrt(kitchen_area)'
        df['ceiling_height**2*sqrt(kitchen_area)'] = df['ceiling_height']**2 * np.sqrt(df['kitchen_area'])
        
        # 'total_area**5'
        df['total_area**5'] = df['total_area']**5
        
        # 'kitchen_area**2*rooms**2'
        df['kitchen_area**2*rooms**2'] = df['kitchen_area']**2 * df['rooms']**2
        
        # 'log(ceiling_height)/ceiling_height'
        df['log(ceiling_height)/ceiling_height'] = np.log(df['ceiling_height']) / df['ceiling_height']
        
        # '1/(kitchen_area*total_area)'
        df['1/(kitchen_area*total_area)'] = 1 / (df['kitchen_area'] * df['total_area'])
        
        # 'living_area**3/kitchen_area'
        df['living_area**3/kitchen_area'] = df['living_area']**3 / df['kitchen_area']
        
        # 'log(kitchen_area)/ceiling_height'
        df['log(kitchen_area)/ceiling_height'] = np.log(df['kitchen_area']) / df['ceiling_height']
        
        return df

    def set_output(self, transform=None):
        return self


