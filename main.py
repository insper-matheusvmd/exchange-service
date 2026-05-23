from fastapi import FastAPI, Header, HTTPException
from datetime import datetime
import httpx

app = FastAPI(title="exchange-service")

AWESOME_API_URL = "https://economia.awesomeapi.com.br/json/last/{from_currency}-{to_currency}"


@app.get("/health-check")
async def health_check():
    return {"status": "ok"}


@app.get("/exchanges/{from_currency}/{to_currency}")
async def get_exchange(
    from_currency: str,
    to_currency: str,
    id_account: str = Header(...),
):
    from_currency = from_currency.upper()
    to_currency = to_currency.upper()
    pair_key = f"{from_currency}{to_currency}"
    url = AWESOME_API_URL.format(from_currency=from_currency, to_currency=to_currency)

    async with httpx.AsyncClient() as client:
        response = await client.get(url)

    if response.status_code != 200:
        raise HTTPException(status_code=502, detail=f"Failed to fetch exchange rate for {from_currency}/{to_currency}")

    data = response.json()

    if pair_key not in data:
        raise HTTPException(status_code=404, detail=f"Currency pair {from_currency}/{to_currency} not found")

    pair = data[pair_key]

    return {
        "sell": float(pair["ask"]),
        "buy": float(pair["bid"]),
        "date": pair["create_date"],
        "id-account": id_account,
    }
