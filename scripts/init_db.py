from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from datetime import datetime, UTC
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def init_database():
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    db = client.muntuai
    
    try:
        # Create collections
        collections = [
            "users",
            "organizations",
            "assistants",
            "conversations",
            "messages",
            "channels",
            "customers",
            "catalog",
            "team",
            "knowledge_base",
            "assistant_training",
            "channel_configs",
            "analytics",
            "templates",
            "workflows",
            "integrations"
        ]
        
        # Create collections if they don't exist
        for collection in collections:
            if collection not in await db.list_collection_names():
                await db.create_collection(collection)
                logger.info(f"Created collection: {collection}")

        # Create indexes
        logger.info("Creating indexes...")
        
        # Users collection
        await db.users.create_index("email", unique=True)
        await db.users.create_index("status")
        
        # Organizations collection
        await db.organizations.create_index("owner_id")
        await db.organizations.create_index("name")
        await db.organizations.create_index("status")
        
        # Assistants collection
        await db.assistants.create_index([("organization_id", 1), ("name", 1)])
        await db.assistants.create_index("status")
        
        # Conversations collection
        await db.conversations.create_index([("organization_id", 1), ("created_at", -1)])
        await db.conversations.create_index("status")
        await db.conversations.create_index("customer_id")
        await db.conversations.create_index("assistant_id")
        
        # Messages collection
        await db.messages.create_index([("conversation_id", 1), ("created_at", 1)])
        await db.messages.create_index("sender_id")
        
        # Channels collection
        await db.channels.create_index([("organization_id", 1), ("type", 1)])
        await db.channels.create_index("status")
        
        # Customers collection
        await db.customers.create_index([("organization_id", 1), ("email", 1)])
        await db.customers.create_index("phone")
        
        # Team collection
        await db.team.create_index([("organization_id", 1), ("email", 1)])
        await db.team.create_index("role")
        await db.team.create_index("status")

        # Knowledge Base
        await db.knowledge_base.create_index([("organization_id", 1), ("category", 1)])

        # Assistant Training
        await db.assistant_training.create_index([("assistant_id", 1), ("created_at", -1)])

        # Analytics
        await db.analytics.create_index([("organization_id", 1), ("date", -1)])
        await db.analytics.create_index([("assistant_id", 1), ("date", -1)])

        # Templates
        await db.templates.create_index([("organization_id", 1), ("type", 1)])

        # Workflows
        await db.workflows.create_index([("organization_id", 1), ("trigger_type", 1)])

        # Create a test user if none exists
        if await db.users.count_documents({}) == 0:
            test_user = {
                "email": "test@example.com",
                "password": "$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewKyNiAYqeScNazC",  # "password123"
                "first_name": "Test",
                "last_name": "User",
                "created_at": datetime.now(UTC),
                "updated_at": datetime.now(UTC),
                "status": "active",
                "role": "owner"
            }
            await db.users.insert_one(test_user)
            logger.info("Created test user: test@example.com / password123")

        logger.info("Database initialization completed successfully!")
        
    except Exception as e:
        logger.error(f"Database initialization failed: {str(e)}")
        raise
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(init_database()) 