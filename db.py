from pymongo import MongoClient
import os
from dotenv import load_dotenv

load_dotenv()

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
client = MongoClient(MONGO_URI)
db = client["chatbot_whatsapp"]
users = db["users"]
tickets = db["tickets"]
bus_options = db["bus_options"]
airplane_options = db["airplane_options"]
concert_options = db["concert_options"]
