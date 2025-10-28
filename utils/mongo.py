from pymongo import MongoClient
import os 
from dotenv import load_dotenv
load_dotenv()

def _mongo_client():
    conn_string = os.getenv("MONGO_CONN_STRING", "").strip()
    return MongoClient(conn_string)
