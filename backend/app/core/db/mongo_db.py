import os
from motor.motor_asyncio import AsyncIOMotorClient
import uuid
from typing import Dict, List, Any

class MongoDB:
    def __init__(self):
        self.client = None
        self.db = None
        self.collection = None

    async def connect(self):
        """Establish connection to MongoDB."""
        mongodb_uri = os.getenv("MONGODB_URI")
        database_name = os.getenv("MONGODB_DATABASE")
        collection_name = os.getenv("MONGODB_COLLECTION")

        if not all([mongodb_uri, database_name, collection_name]):
            raise ValueError("MongoDB connection details are not properly configured in environment variables.")

        try:
            self.client = AsyncIOMotorClient(mongodb_uri)
            self.db = self.client[database_name]
            self.collection = self.db[collection_name]
            print("Successfully connected to MongoDB.")
        except Exception as e:
            print(f"Error connecting to MongoDB: {str(e)}")
            raise

    async def close_connection(self):
        """Close the MongoDB connection."""
        if self.client:
            self.client.close()
            print("MongoDB connection closed.")

    async def upload_json_with_session(self, json_data: List[Dict[str, Any]]) -> str:
        """Upload JSON data to MongoDB with a generated session ID."""
        if self.collection is None:  # Check explicitly for None
            raise ValueError("MongoDB connection not established. Call connect() first.")

        session_id = str(uuid.uuid4())  # Generate a unique session ID

        try:
            # Add session_id to each item in the JSON data
            for item in json_data:
                item['session_id'] = session_id

            # Insert the data into MongoDB
            result = await self.collection.insert_many(json_data)
            print(f"Successfully uploaded {len(result.inserted_ids)} documents with session ID: {session_id}")
            return session_id
        except Exception as e:
            print(f"Error uploading JSON data: {str(e)}")
            raise

    async def fetch_json_by_session(self, session_id: str) -> List[Dict[str, Any]]:
        """Fetch JSON data from MongoDB based on the session ID."""
        if self.collection is None:  # Check explicitly for None
            raise ValueError("MongoDB connection not established. Call connect() first.")

        try:
            # Fetch documents with the given session_id
            cursor = self.collection.find({'session_id': session_id})
            
            # Convert cursor to list and remove MongoDB's _id field
            result = []
            async for doc in cursor:
                doc.pop('_id', None)  # Remove the _id field
                result.append(doc)

            print(f"Fetched {len(result)} documents for session ID: {session_id}")
            return result
        except Exception as e:
            print(f"Error fetching JSON data: {str(e)}")
            raise