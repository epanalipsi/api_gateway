from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from dotenv import dotenv_values
import certifi
import urllib.parse

# Load env config
config = dotenv_values("deployment/deploy.env")

# Encode password to handle special characters
password_encoded = urllib.parse.quote_plus(config["DB_PASSWORD"])

# Construct MongoDB URI
MONGO_URL = f"mongodb+srv://{config['DB_USERNAME']}:{password_encoded}@" \
            f"{config['DB_HOST']}/?retryWrites=true&w=majority&appName=POCDB"

print("Connecting to:", MONGO_URL)

# ✅ SYNC Test connection with PyMongo and TLS CA cert
try:
    pymongo_client = MongoClient(
        MONGO_URL,
        tls=True,
        tlsCAFile=certifi.where()
    )
    pymongo_client.admin.command("ping")
    print("✅ MongoDB connection (sync) succeeded.")
except ConnectionFailure as e:
    print("❌ MongoDB connection (sync) failed:", e)
    exit()

# ✅ ASYNC client for actual usage (e.g., FastAPI)
motor_client = AsyncIOMotorClient(
    MONGO_URL,
    tls=True,
    tlsCAFile=certifi.where()
)
database = motor_client[config["DB_NAME"]]