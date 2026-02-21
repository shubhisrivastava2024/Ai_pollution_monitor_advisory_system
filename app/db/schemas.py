from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

# Location Schemas
class LocationBase(BaseModel):
    name: str
    city: str
    country: str
    latitude: Optional[float] = None
    longitude: Optional[float] = None

class LocationCreate(LocationBase):
    pass

class Location(LocationBase):
    id: int

    class Config:
        from_attributes = True

# Pollution Schemas
class PollutionRecordBase(BaseModel):
    location_id: int
    aqi: Optional[int] = None
    pm25: Optional[float] = None
    pm10: Optional[float] = None
    co: Optional[float] = None
    no2: Optional[float] = None

class PollutionRecordCreate(PollutionRecordBase):
    pass

class PollutionRecord(PollutionRecordBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

# Weather Prediction Schemas
class WeatherPredictionBase(BaseModel):
    location_id: int
    predicted_temp: float
    predicted_humidity: float
    condition: str

class WeatherPrediction(WeatherPredictionBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True
