import httpx
import asyncio

async def test_rate_limiter():
    async with httpx.AsyncClient() as client:
        for i in range(15):
            response = await client.get("http://localhost:8000/test")
            print(f"Req {i+1}: {response.status_code}")
            if response.status_code == 429:
                print(f"  → {response.json()}")

asyncio.run(test_rate_limiter())