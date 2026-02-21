from fastapi import APIRouter, HTTPException, Depends
from typing import List
from ..db import database, schemas

router = APIRouter(
    prefix="/locations",
    tags=["Locations"]
)

@router.post("/", response_model=schemas.Location)
async def create_location(location: schemas.LocationCreate):
    query = """
        INSERT INTO locations (name, city, country, latitude, longitude)
        VALUES (?, ?, ?, ?, ?)
    """
    params = (location.name, location.city, location.country, location.latitude, location.longitude)
    
    async with database.aiosqlite.connect(database.DB_PATH) as db:
        cursor = await db.execute(query, params)
        await db.commit()
        last_id = cursor.lastrowid
        
    return {**location.dict(), "id": last_id}

@router.get("/", response_model=List[schemas.Location])
async def read_locations():
    query = "SELECT * FROM locations"
    rows = await database.fetch_rows(query)
    return [dict(row) for row in rows]

@router.get("/{location_id}", response_model=schemas.Location)
async def read_location(location_id: int):
    query = "SELECT * FROM locations WHERE id = ?"
    row = await database.fetch_one(query, (location_id,))
    if row is None:
        raise HTTPException(status_code=404, detail="Location not found")
    return dict(row)

@router.delete("/{location_id}")
async def delete_location(location_id: int):
    query = "DELETE FROM locations WHERE id = ?"
    await database.execute_query(query, (location_id,))
    return {"message": "Location deleted successfully"}
