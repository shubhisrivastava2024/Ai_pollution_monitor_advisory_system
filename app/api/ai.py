from fastapi import APIRouter, HTTPException
from ..db import database, schemas
from ..services.ml_service import weather_service
from ..services.genai_service import genai_service
from datetime import datetime

router = APIRouter(
    prefix="/ai",
    tags=["AI Services"]
)

@router.post("/predict_weather/{location_id}", response_model=schemas.WeatherPrediction)
async def predict_weather(location_id: int):
    # Get latest pollution record for this location
    query = "SELECT * FROM pollution_records WHERE location_id = ? ORDER BY timestamp DESC LIMIT 1"
    record = await database.fetch_one(query, (location_id,))
    
    if not record:
        raise HTTPException(status_code=404, detail="No pollution records found for this location to base prediction on.")
    
    # Extract features for ML model
    now = datetime.now()
    prediction_result = weather_service.predict(
        aqi=record['aqi'],
        pm25=record['pm25'],
        month=now.month,
        hour=now.hour
    )
    
    # Save prediction to DB
    insert_query = """
        INSERT INTO weather_predictions (location_id, predicted_temp, predicted_humidity, condition)
        VALUES (?, ?, ?, ?)
    """
    params = (
        location_id, 
        prediction_result['predicted_temp'], 
        prediction_result['predicted_humidity'], 
        prediction_result['condition']
    )
    
    async with database.aiosqlite.connect(database.DB_PATH) as db:
        db.row_factory = database.aiosqlite.Row
        cursor = await db.execute(insert_query, params)
        await db.commit()
        last_id = cursor.lastrowid
        
        async with db.execute("SELECT * FROM weather_predictions WHERE id = ?", (last_id,)) as cursor:
            new_pred = await cursor.fetchone()
            
    return dict(new_pred) if new_pred else {}

@router.get("/analyze/{location_id}")
async def analyze_pollution(location_id: int):
    # Get location details
    loc_query = "SELECT * FROM locations WHERE id = ?"
    location = await database.fetch_one(loc_query, (location_id,))
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
        
    # Get latest pollution record
    poll_query = "SELECT * FROM pollution_records WHERE location_id = ? ORDER BY timestamp DESC LIMIT 1"
    record = await database.fetch_one(poll_query, (location_id,))
    
    if not record:
        raise HTTPException(status_code=404, detail="No pollution data found for analysis.")
        
    analysis = await genai_service.analyze_pollution(
        location_name=location['name'],
        aqi=record['aqi'],
        pm25=record['pm25'],
        pm10=record['pm10']
    )
    
    return {
        "location": location['name'],
        "timestamp": record['timestamp'],
        "aqi": record['aqi'],
        "analysis": analysis
    }

@router.get("/advice/{location_id}")
async def get_ai_advice(location_id: int):
    # Get location details
    loc_query = "SELECT * FROM locations WHERE id = ?"
    location = await database.fetch_one(loc_query, (location_id,))
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
        
    # Get latest pollution record
    poll_query = "SELECT * FROM pollution_records WHERE location_id = ? ORDER BY timestamp DESC LIMIT 1"
    record = await database.fetch_one(poll_query, (location_id,))
    
    if not record:
        raise HTTPException(status_code=404, detail="No pollution data found for generating advice.")
        
    # Get latest weather prediction (if available)
    weather_query = "SELECT * FROM weather_predictions WHERE location_id = ? ORDER BY timestamp DESC LIMIT 1"
    weather = await database.fetch_one(weather_query, (location_id,))
    
    condition = weather['condition'] if weather else None
    
    advice = await genai_service.get_advice(
        location_name=location['name'],
        aqi=record['aqi'],
        weather_condition=condition
    )
    
    return {
        "location": location['name'],
        "timestamp": record['timestamp'],
        "aqi": record['aqi'],
        "weather_condition": condition,
        "advice": advice
    }
