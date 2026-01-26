import os
from dotenv import load_dotenv

load_dotenv()

OPENWEATHER_API_KEY = os.getenv("OPENWEATHER_API_KEY")
MONGO_URI = os.getenv("MONGO_URI")

DB_NAME = "aqi_db"

LAT = 25.3960
LON = 68.3578
CITY = "Hyderabad"
