from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
import os

class Database:
    client: Optional[AsyncIOMotorClient] = None
    database = None

db_instance = Database()

async def get_database():
    return db_instance.database

async def connect_to_mongo():
    """Create database connection"""
    mongo_url = os.environ.get('MONGO_URL')
    if not mongo_url:
        raise ValueError("MONGO_URL environment variable is not set")
    
    db_instance.client = AsyncIOMotorClient(mongo_url)
    db_instance.database = db_instance.client[os.environ.get('DB_NAME', 'aurum_life')]
    
    # Test connection
    try:
        await db_instance.client.admin.command('ping')
        print("✅ Successfully connected to MongoDB")
    except Exception as e:
        print(f"❌ Failed to connect to MongoDB: {e}")
        raise

async def close_mongo_connection():
    """Close database connection"""
    if db_instance.client:
        db_instance.client.close()
        print("✅ MongoDB connection closed")

# Collection helpers
async def get_collection(collection_name: str):
    """Get a MongoDB collection"""
    db = await get_database()
    return db[collection_name]

# CRUD helpers
async def create_document(collection_name: str, document: dict):
    """Create a new document"""
    collection = await get_collection(collection_name)
    result = await collection.insert_one(document)
    return str(result.inserted_id)

async def find_document(collection_name: str, query: dict):
    """Find a single document"""
    collection = await get_collection(collection_name)
    document = await collection.find_one(query)
    if document:
        document['_id'] = str(document['_id'])
    return document

async def find_documents(collection_name: str, query: dict = None, skip: int = 0, limit: int = 100):
    """Find multiple documents"""
    collection = await get_collection(collection_name)
    query = query or {}
    cursor = collection.find(query).skip(skip).limit(limit)
    documents = await cursor.to_list(length=limit)
    for doc in documents:
        doc['_id'] = str(doc['_id'])
    return documents

async def update_document(collection_name: str, query: dict, update: dict):
    """Update a document"""
    collection = await get_collection(collection_name)
    update_doc = {"$set": update}
    result = await collection.update_one(query, update_doc)
    return result.modified_count > 0

async def delete_document(collection_name: str, query: dict):
    """Delete a document"""
    collection = await get_collection(collection_name)
    result = await collection.delete_one(query)
    return result.deleted_count > 0

async def count_documents(collection_name: str, query: dict = None):
    """Count documents matching query"""
    collection = await get_collection(collection_name)
    query = query or {}
    return await collection.count_documents(query)

# Aggregation helpers
async def aggregate_documents(collection_name: str, pipeline: list):
    """Run aggregation pipeline"""
    collection = await get_collection(collection_name)
    cursor = collection.aggregate(pipeline)
    results = await cursor.to_list(length=None)
    for doc in results:
        if '_id' in doc:
            doc['_id'] = str(doc['_id'])
    return results