import asyncio
import httpx

async def test_city_fetch():
    url = "http://localhost:8000/pollution/fetch-by-city/Mumbai"
    print(f"Testing city fetch for Mumbai at {url}...")
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(url)
            if response.status_code == 200:
                print("Success!")
                print("Response:", response.json())
            else:
                print(f"Failed with status {response.status_code}")
                print("Error:", response.text)
        except Exception as e:
            print(f"Connection error: {e}")

if __name__ == "__main__":
    asyncio.run(test_city_fetch())
