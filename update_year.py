import os
import sys
from datetime import datetime
from pymongo import MongoClient

# Add parent folder to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from config import *

client = MongoClient(MONGO_URI)
db = client[DB_NAME]

# Find documents without 'year'
for doc in db.engineered_features.find({"year": {"$exists": False}}):
    if "date" in doc:
        date_obj = datetime.strptime(doc["date"], "%Y-%m-%d")
        year = date_obj.year
        db.engineered_features.update_one({"_id": doc["_id"]}, {"$set": {"year": year}})
        print(f"Updated {doc['date']} with year {year}")
    else:
        print(f"No date in doc {doc['_id']}")

print("Update complete")
