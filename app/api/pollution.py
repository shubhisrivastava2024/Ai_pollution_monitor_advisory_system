from fastapi import APIRouter, HTTPException
from typing import List
from ..db import database, schemas

router = APIRouter(
    prefix="/pollution",
    tags=["Pollution"]
)

@router.post("/", response_model=schemas.PollutionRecord)
async def create_pollution_record(record: schemas.PollutionRecordCreate):
    # Check if location exists
    loc_query = "SELECT id FROM locations WHERE id = ?"
    loc = await database.fetch_one(loc_query, (record.location_id,))
    if not loc:
        raise HTTPException(status_code=404, detail="Location not found")
    
    query = """
        INSERT INTO pollution_records (location_id, aqi, pm25, pm10, co, no2)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    params = (record.location_id, record.aqi, record.pm25, record.pm10, record.co, record.no2)
    
    async with database.aiosqlite.connect(database.DB_PATH) as db:
        db.row_factory = database.aiosqlite.Row
        cursor = await db.execute(query, params)
        await db.commit()
        last_id = cursor.lastrowid
        
        async with db.execute("SELECT * FROM pollution_records WHERE id = ?", (last_id,)) as cursor:
            new_record = await cursor.fetchone()
            
    return dict(new_record) if new_record else {}

@router.get("/", response_model=List[schemas.PollutionRecord])
async def read_pollution_records(location_id: int = None):
    if location_id:
        query = "SELECT * FROM pollution_records WHERE location_id = ? ORDER BY timestamp DESC"
        rows = await database.fetch_rows(query, (location_id,))
    else:
        query = "SELECT * FROM pollution_records ORDER BY timestamp DESC"
        rows = await database.fetch_rows(query)
    return [dict(row) for row in rows]

from ..services.external_pollution import external_pollution_service

@router.post("/fetch-by-city/{city_name}", response_model=schemas.PollutionRecord)
async def fetch_pollution_by_city(city_name: str):
    # 1. Fetch real-time data from external service
    data = await external_pollution_service.fetch_pollution_by_city(city_name)
    
    if "error" in data:
        raise HTTPException(status_code=400, detail=data["error"])
    
    # 2. Check if a location with this city exists
    city_response_name = data.get("city", city_name)
    loc_query = "SELECT * FROM locations WHERE city LIKE ?"
    location = await database.fetch_one(loc_query, (f"%{city_name}%",))
    
    if not location:
        # Create a new location automatically
        insert_loc_query = """
            INSERT INTO locations (name, city, country, latitude, longitude)
            VALUES (?, ?, ?, ?, ?)
        """
        # lat/lon from the AI data if available
        geo = data.get("geo", [0.0, 0.0])
        params = (city_response_name, city_name, "Auto", geo[0], geo[1])
        
        async with database.aiosqlite.connect(database.DB_PATH) as db:
            db.row_factory = database.aiosqlite.Row
            cursor = await db.execute(insert_loc_query, params)
            await db.commit()
            location_id = cursor.lastrowid
    else:
        location_id = location['id']
        
    # 3. Save pollution record
    query = """
        INSERT INTO pollution_records (location_id, aqi, pm25, pm10, co, no2)
        VALUES (?, ?, ?, ?, ?, ?)
    """
    params = (location_id, data['aqi'], data['pm25'], data['pm10'], data['co'], data['no2'])
    
    async with database.aiosqlite.connect(database.DB_PATH) as db:
        db.row_factory = database.aiosqlite.Row
        cursor = await db.execute(query, params)
        await db.commit()
        last_id = cursor.lastrowid
        
        async with db.execute("SELECT * FROM pollution_records WHERE id = ?", (last_id,)) as cursor:
            new_record = await cursor.fetchone()
            
    return dict(new_record) if new_record else {}
