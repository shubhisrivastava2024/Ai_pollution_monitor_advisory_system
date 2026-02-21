# AI Pollution Monitor

A comprehensive REST API for monitoring pollution levels, predicting weather trends using Machine Learning, and providing AI-powered analysis for better decision-making.

## Tech Stack
- **Framework**: FastAPI (Python)
- **Database**: SQLite (via `aiosqlite` and `sqlite3`)
- **ML**: Scikit-learn (Linear Regression for weather prediction)
- **GenAI**: Google Gemini 1.5 Flash (for pollution analysis and recommendations)
- **Documentation**: Swagger/OpenAPI (built-in FastAPI)

## Folder Structure
```
ai-pollution-monitor/
├── app/
│   ├── api/           # API Routers (Locations, Pollution, AI)
│   ├── db/            # Database initialization and schemas
│   ├── services/      # ML and GenAI logic
│   ├── utils/         # Error handlers and logging
│   └── main.py        # Entry point
├── data/              # SQLite database storage
├── models/            # Trained ML models
├── requirements.txt   # Dependencies
└── README.md
```

## Setup Instructions

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**:
   Create a `.env` file in the root directory and add your Gemini API key:
   ```
   GEMINI_API_KEY=your_api_key_here
   ```

3. **Initialize Database**:
   ```bash
   python app/db/init_db.py
   ```

4. **Run the Application**:
   ```bash
   python -m app.main
   ```
   The API will be available at `http://localhost:8000`. Documentation (Swagger UI) at `http://localhost:8000/docs`.

## API Endpoints

### Locations
- `POST /locations/`: Create a new location.
- `GET /locations/`: List all locations.
- `GET /locations/{id}`: Get details of a specific location.

### Pollution Records
- `POST /pollution/`: Add a new pollution record.
- `GET /pollution/`: Get all records (optional `location_id` filter).

### AI Services
- `POST /ai/predict_weather/{location_id}`: Predict future weather condition based on latest pollution data.
- `GET /ai/analyze/{location_id}`: Get GenAI-powered analysis and recommendations for a location.

## ML usage
The weather prediction model uses historical simulation to predict Temperature and Humidity based on AQI, PM2.5, Month, and Hour.

## GenAI Usage
Uses Google Gemini to provide health impact summaries and policy recommendations based on real-time pollution data.
