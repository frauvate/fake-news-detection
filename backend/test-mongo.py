from pymongo import MongoClient
from decouple import config

MONGO_URL = config("MONGO_URL")

client = MongoClient(MONGO_URL)

mongo_db = client["news_database"]
articles_col = mongo_db["articles"]
