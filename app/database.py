from motor.motor_asyncio import AsyncIOMotorClient
from .config import settings
import logging
from pymongo import IndexModel, ASCENDING

logger = logging.getLogger(__name__)

# Create Motor client
print(f"Connecting to MongoDB at: {settings.MONGODB_URL}")
client = AsyncIOMotorClient(settings.MONGODB_URL)

# Get database
db = client[settings.DATABASE_NAME]

# Test connection
async def connect_and_init_db():
    try:
        await client.admin.command('ping')
        print("Successfully connected to MongoDB")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {str(e)}")
        raise e

async def init_db(client: AsyncIOMotorClient):
    db = client.muntuai

    # Create indexes
    await db.users.create_indexes([
        IndexModel([("email", ASCENDING)], unique=True)
    ])
    
    await db.organizations.create_indexes([
        IndexModel([("owner_id", ASCENDING)], unique=True)
    ])
    
    await db.conversations.create_indexes([
        IndexModel([("organization_id", ASCENDING)]),
        IndexModel([("customer_id", ASCENDING)]),
        IndexModel([("assistant_id", ASCENDING)])
    ])
    
    # Add more indexes as needed 