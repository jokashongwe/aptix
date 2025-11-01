from db import bus_options, airplane_options

def get_destinations(type: str="bus") -> list:
    """Retourne la liste unique des destinations"""
    if type == "bus":
        return bus_options.distinct("destination")
    return airplane_options.distinct("destination")

def get_departure_locations(type: str="bus") -> list:
    """Retourne la liste unique des villes de départ"""
    if type == "bus":
        return bus_options.distinct("departure_location")
    return airplane_options.distinct("departure_location")


def get_prices_with_company(departure, destination, type: str="bus", classe: str = None) -> list:
    query = {"departure_location": departure, "destination": destination}
    projection = {"_id": 0, "bus_company": 1, "price": 1}
    if type == "bus":
        return list(bus_options.find(query, projection))
    query = {"departure_location": departure, "destination": destination, "classe": classe}
    projection = {"_id": 0, "airline": 1, "price": 1}
    return list(airplane_options.find(query, projection))
