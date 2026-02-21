import google.generativeai as genai
import os
from dotenv import load_dotenv

load_dotenv(override=True)

# Configure Gemini
api_key = os.getenv("GEMINI_API_KEY")
if api_key:
    genai.configure(api_key=api_key.strip())

class GenAIService:
    def __init__(self):
        # Using gemini-flash-latest which was confirmed to be available for this key
        # If it fails, we fall back to alternatives in the generate methods.
        self.model_name = 'gemini-flash-latest'
        self.model = genai.GenerativeModel(self.model_name)

    def _get_model(self):
        return self.model

    async def analyze_pollution(self, location_name, aqi, pm25, pm10):
        if not api_key:
            return "GenAI integration is not configured. Please set GEMINI_API_KEY in .env."

        prompt = f"""
        Analyze the following pollution data for {location_name}:
        - AQI: {aqi}
        - PM2.5: {pm25} µg/m³
        - PM10: {pm10} µg/m³

        Provide a concise analysis including:
        1. Health impact summary.
        2. Recommendations for citizens (e.g., masks, outdoor activities).
        3. One policy suggestion for local authorities to reduce this pollution.
        
        Keep it professional and informative.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error communicating with GenAI: {str(e)}"

    async def get_advice(self, location_name, aqi, weather_condition=None):
        if not api_key:
            return "GenAI integration is not configured. Please set GEMINI_API_KEY in .env."

        prompt = f"""
        Give practical and actionable advice for citizens in {location_name} based on the following:
        - Current AQI: {aqi}
        - Weather Condition: {weather_condition if weather_condition else "Unknown"}

        Provide advice in these categories:
        1. Actionable Health Advice (for elderly, children, and general public).
        2. Outdoor Activity Advice.
        3. Simple Household Advice to reduce exposure.
        
        Keep it concise and friendly.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Error communicating with GenAI: {str(e)}"

genai_service = GenAIService()
