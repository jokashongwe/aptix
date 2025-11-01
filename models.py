from pydantic import BaseModel
from typing import Optional, Dict

class UserState(BaseModel):
    phone: str
    step: str
    data: Optional[Dict] = {}
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class TripTicketRequest(BaseModel):
    depart: str
    arrivee: str
    date_depart: str
    nbplace: int
    type: str  # 'bus' or 'avion'
    is_one_way: Optional[bool] = True
    created_at: Optional[str] = None
    phone: str = None

class ConcertTicketRequest(BaseModel):
    concert_name: str
    date: str
    nb_tickets: int
    phone: str = None
    created_at: Optional[str] = None

class BusTicketOption(BaseModel):
    bus_company: str
    departure_time: str
    price: float
    destination: str
    departure_location: str
    company_logo_url: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class AirplaneTicketOption(BaseModel):
    airline: str
    flight_number: str
    departure_time: str
    arrival_time: str
    price: float
    origin: str
    destination: str
    airline_logo_url: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class ConcertEventOption(BaseModel):
    event_name: str
    event_date: str
    venue: str
    price: float
    vip_available: bool
    vip_price: Optional[float] = None
    premium_seating_available: bool = None
    premium_seating_price: Optional[float] = None
    event_image_url: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
