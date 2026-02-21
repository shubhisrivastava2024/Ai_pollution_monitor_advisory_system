import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "../../data/pollution_monitor.db")

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Create Locations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS locations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            city TEXT NOT NULL,
            country TEXT NOT NULL,
            latitude REAL,
            longitude REAL
        )
    ''')

    # Create PollutionRecords table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS pollution_records (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_id INTEGER NOT NULL,
            aqi INTEGER,
            pm25 REAL,
            pm10 REAL,
            co REAL,
            no2 REAL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (location_id) REFERENCES locations (id)
        )
    ''')

    # Create WeatherPredictions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS weather_predictions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            location_id INTEGER NOT NULL,
            predicted_temp REAL,
            predicted_humidity REAL,
            condition TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (location_id) REFERENCES locations (id)
        )
    ''')

    conn.commit()
    conn.close()
    print(f"Database initialized at {DB_PATH}")

if __name__ == "__main__":
    init_db()
