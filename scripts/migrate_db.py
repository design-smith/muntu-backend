from motor.motor_asyncio import AsyncIOMotorClient
import asyncio
from datetime import datetime, UTC
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def migrate_database():
    # Connect to MongoDB
    client = AsyncIOMotorClient("mongodb://localhost:27017")
    
    try:
        # Source databases
        muntu_db = client.muntu
        muntuai_db = client.muntuai
        
        # Target database
        new_db = client.muntuai_new

        # 1. Migrate users and user profiles
        logger.info("Migrating users and profiles...")
        users_seen = set()
        
        # Migrate from muntu.users and user_profiles
        async for user in muntu_db.users.find():
            if user["email"] not in users_seen:
                users_seen.add(user["email"])
                # Get associated profile
                profile = await muntu_db.user_profiles.find_one({"user_id": user["_id"]})
                if profile:
                    user.update({
                        "profile_picture": profile.get("profile_picture"),
                        "bio": profile.get("bio"),
                        "phone": profile.get("phone")
                    })
                await new_db.users.update_one(
                    {"email": user["email"]},
                    {"$set": {**user, "updated_at": datetime.now(UTC)}},
                    upsert=True
                )

        # 2. Migrate businesses and user_businesses
        logger.info("Migrating organizations...")
        async for business in muntu_db.businesses.find():
            # Convert business to organization format
            org = {
                "_id": business["_id"],
                "name": business["name"],
                "owner_id": business["owner_id"],
                "industry": business.get("industry", ""),
                "size": business.get("size", ""),
                "website": business.get("website"),
                "address": business.get("address", ""),
                "phone": business.get("phone", ""),
                "created_at": business.get("created_at", datetime.now(UTC)),
                "updated_at": datetime.now(UTC),
                "status": "active"
            }
            await new_db.organizations.update_one(
                {"_id": org["_id"]},
                {"$set": org},
                upsert=True
            )

        # 3. Migrate AI assistants
        logger.info("Migrating assistants...")
        async for assistant in muntu_db.ai_assistants.find():
            await new_db.assistants.update_one(
                {"_id": assistant["_id"]},
                {"$set": assistant},
                upsert=True
            )

        # 4. Migrate conversations and messages
        logger.info("Migrating conversations and messages...")
        async for conv in muntu_db.conversations.find():
            await new_db.conversations.update_one(
                {"_id": conv["_id"]},
                {"$set": conv},
                upsert=True
            )
            
            # Migrate associated messages
            async for msg in muntu_db.messages.find({"conversation_id": conv["_id"]}):
                await new_db.messages.update_one(
                    {"_id": msg["_id"]},
                    {"$set": msg},
                    upsert=True
                )

        # 5. Migrate channels
        logger.info("Migrating channels...")
        async for channel in muntu_db.channels.find():
            await new_db.channels.update_one(
                {"_id": channel["_id"]},
                {"$set": channel},
                upsert=True
            )

        # 6. Create indexes
        logger.info("Creating indexes...")
        await new_db.users.create_index("email", unique=True)
        await new_db.organizations.create_index("owner_id")
        await new_db.conversations.create_index([("organization_id", 1), ("created_at", -1)])
        await new_db.messages.create_index([("conversation_id", 1), ("created_at", 1)])
        await new_db.channels.create_index([("organization_id", 1), ("type", 1)])

        # 7. Verify migration
        logger.info("Verifying migration...")
        counts = {
            "users": await new_db.users.count_documents({}),
            "organizations": await new_db.organizations.count_documents({}),
            "conversations": await new_db.conversations.count_documents({}),
            "messages": await new_db.messages.count_documents({}),
            "assistants": await new_db.assistants.count_documents({}),
            "channels": await new_db.channels.count_documents({})
        }
        
        logger.info("Migration completed with counts:")
        for collection, count in counts.items():
            logger.info(f"- {collection}: {count}")

        # 8. Replace old database with new one
        logger.info("Finalizing migration...")
        await client.drop_database('muntu')
        await client.drop_database('muntuai')
        
        source_collections = await new_db.list_collection_names()
        target_db = client.muntuai
        
        for collection_name in source_collections:
            async for doc in new_db[collection_name].find():
                await target_db[collection_name].insert_one(doc)
        
        await client.drop_database('muntuai_new')
        
        logger.info("Migration completed successfully!")

    except Exception as e:
        logger.error(f"Migration failed: {str(e)}")
        raise
    finally:
        client.close()

if __name__ == "__main__":
    asyncio.run(migrate_database()) 