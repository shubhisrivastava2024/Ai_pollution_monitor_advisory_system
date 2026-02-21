import httpx
import os
from dotenv import load_dotenv

load_dotenv(override=True)

WAQI_TOKEN = os.getenv("WAQI_TOKEN")

class ExternalPollutionService:
    async def fetch_real_time_pollution(self, lat: float, lon: float):
        if not WAQI_TOKEN:
            return {
                "error": "WAQI_TOKEN not configured. Please set it in .env.",
                "aqi": 50, # Mock data
                "pm25": 12.5,
                "pm10": 20.0,
                "co": 0.4,
                "no2": 15.0
            }

        url = f"https://api.waqi.info/feed/geo:{lat};{lon}/?token={WAQI_TOKEN}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                data = response.json()
                
                if data.get("status") == "ok":
                    iaqi = data["data"]["iaqi"]
                    return {
                        "aqi": data["data"]["aqi"],
                        "pm25": iaqi.get("pm25", {}).get("v", 0),
                        "pm10": iaqi.get("pm10", {}).get("v", 0),
                        "co": iaqi.get("co", {}).get("v", 0),
                        "no2": iaqi.get("no2", {}).get("v", 0),
                        "city": data["data"]["city"]["name"],
                        "geo": data["data"]["city"]["geo"]
                    }
                else:
                    return {"error": f"API Error: {data.get('data')}"}
            except Exception as e:
                return {"error": f"Connection Error: {str(e)}"}

    async def fetch_pollution_by_city(self, city_name: str):
        if not WAQI_TOKEN:
            return {
                "error": "WAQI_TOKEN not configured. Please set it in .env.",
                "aqi": 50, # Mock data
                "pm25": 12.5,
                "pm10": 20.0,
                "co": 0.4,
                "no2": 15.0,
                "city": city_name,
                "geo": [0, 0]
            }

        url = f"https://api.waqi.info/feed/{city_name}/?token={WAQI_TOKEN}"
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(url)
                data = response.json()
                
                if data.get("status") == "ok":
                    iaqi = data["data"]["iaqi"]
                    return {
                        "aqi": data["data"]["aqi"],
                        "pm25": iaqi.get("pm25", {}).get("v", 0),
                        "pm10": iaqi.get("pm10", {}).get("v", 0),
                        "co": iaqi.get("co", {}).get("v", 0),
                        "no2": iaqi.get("no2", {}).get("v", 0),
                        "city": data["data"]["city"]["name"],
                        "geo": data["data"]["city"]["geo"]
                    }
                else:
                    return {"error": f"API Error: {data.get('data')}"}
            except Exception as e:
                return {"error": f"Connection Error: {str(e)}"}

external_pollution_service = ExternalPollutionService()
