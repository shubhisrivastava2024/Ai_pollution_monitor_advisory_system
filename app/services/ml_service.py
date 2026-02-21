import pandas as pd
from sklearn.linear_model import LinearRegression
import pickle
import os
import numpy as np

MODEL_PATH = os.path.join(os.path.dirname(__file__), "../../models/weather_model.pkl")

class WeatherMLService:
    def __init__(self):
        self.model = None
        self._load_or_train_model()

    def _load_or_train_model(self):
        if os.path.exists(MODEL_PATH):
            with open(MODEL_PATH, 'rb') as f:
                self.model = pickle.load(f)
        else:
            self._train_initial_model()

    def _train_initial_model(self):
        # Simulate local training data
        # Features: [AQI, PM2.5, Month, Hour]
        # Target: [Temperature, Humidity]
        data = {
            'aqi': np.random.randint(0, 500, 100),
            'pm25': np.random.uniform(0, 300, 100),
            'month': np.random.randint(1, 13, 100),
            'hour': np.random.randint(0, 24, 100),
            'temp': np.random.uniform(15, 40, 100),
            'humidity': np.random.uniform(30, 90, 100)
        }
        df = pd.DataFrame(data)
        X = df[['aqi', 'pm25', 'month', 'hour']]
        y = df[['temp', 'humidity']]
        
        self.model = LinearRegression()
        self.model.fit(X, y)
        
        os.makedirs(os.path.dirname(MODEL_PATH), exist_ok=True)
        with open(MODEL_PATH, 'wb') as f:
            pickle.dump(self.model, f)
        print("Initial ML model trained and saved.")

    def predict(self, aqi, pm25, month, hour):
        features = np.array([[aqi, pm25, month, hour]])
        prediction = self.model.predict(features)
        temp, humidity = prediction[0]
        
        # Determine condition based on temperature and humidity
        condition = "Clear"
        if humidity > 80:
            condition = "Rainy/Humid"
        elif temp > 35:
            condition = "Hot/Dry"
        elif aqi > 200:
            condition = "Smoggy"
            
        return {
            "predicted_temp": round(float(temp), 2),
            "predicted_humidity": round(float(humidity), 2),
            "condition": condition
        }

weather_service = WeatherMLService()
