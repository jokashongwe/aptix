from fastapi import APIRouter, Request
from db import bus_options, airplane_options, concert_options
from datetime import datetime
import os

ticket_router = APIRouter()

@ticket_router.post("/busoffers")
async def bus_options_endpoint(req: Request):
    data = await req.json()
    apiSecret = req.headers.get("API-SECRET")
    if apiSecret != os.getenv("API_SECRET"):
        return {"error": "unauthorized"}, 401
    bus_options.insert_one({
        "bus_company": data.get("bus_company"),
        "departure_time": data.get("departure_time"),
        "price": data.get("price"),
        "destination": data.get("destination"),
        "departure_location": data.get("departure_location"),
        "company_logo_url": data.get("company_logo_url"),
        "created_at": datetime.now().isoformat()
    })
    return {"status": "bus options received"}

@ticket_router.post("/ariplaneoffers")
async def airplane_options_endpoint(req: Request):
    data = await req.json()
    apiSecret = req.headers.get("API-SECRET")
    if apiSecret != os.getenv("API_SECRET"):
        return {"error": "unauthorized"}, 401
    airplane_options.insert_one({
        "airline": data.get("airline"),
        "flight_number": data.get("flight_number"),
        "departure_time": data.get("departure_time"),
        "arrival_time": data.get("arrival_time"),
        "price": data.get("price"),
        "classe": data.get("classe", "economic"),
        "departure_location": data.get("departure_location"),
        "destination": data.get("destination"),
        "airline_logo_url": data.get("airline_logo_url"),
        "created_at": datetime.now().isoformat()
    })
    return {"status": "airplane offer created"}

@ticket_router.post("/concertoffers")
async def concert_options_endpoints(req: Request):
    data = await req.json()
    apiSecret = req.headers.get("API-SECRET")
    if apiSecret != os.getenv("API_SECRET"):
        return {"error": "unauthorized"}, 401
    concert_options.insert_one({
        "event_name": data.get("event_name"),
        "event_date": data.get("event_date"),
        "venue": data.get("venue"),
        "price": data.get("price"),
        "vip_available": data.get("vip_available"),
        "vip_price": data.get("vip_price"),
        "premium_seating_available": data.get("premium_seating_available"),
        "premium_seating_price": data.get("premium_seating_price"),
        "event_image_url": data.get("event_image_url"),
        "created_at": datetime.now().isoformat()
    })