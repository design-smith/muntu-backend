from ..database import db
from motor.motor_asyncio import AsyncIOMotorClient

async def init_db():
    # Create collections
    collections = [
        "users",
        "organizations",
        "assistants",
        "conversations",
        "messages",
        "customers",
        "catalog",
        "team"
    ]
    
    for collection in collections:
        if collection not in await db.list_collection_names():
            await db.create_collection(collection)

    # Create indexes
    await db.users.create_index("email", unique=True)
    await db.organizations.create_index("name")
    await db.assistants.create_index([("organization_id", 1), ("name", 1)])
    await db.conversations.create_index([("organization_id", 1), ("status", 1)])
    await db.messages.create_index("conversation_id")
    await db.customers.create_index([("organization_id", 1), ("email", 1)])
    await db.catalog.create_index([("organization_id", 1), ("name", 1)])
    await db.team.create_index([("organization_id", 1), ("email", 1)])

    print("Database initialized successfully!") 