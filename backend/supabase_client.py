"""
Supabase Client Configuration for Aurum Life
Replaces MongoDB database.py
"""

import os
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from dotenv import load_dotenv
import logging
from datetime import datetime

# Load environment variables from main .env file
load_dotenv('.env')

logger = logging.getLogger(__name__)

class SupabaseManager:
    """Manages Supabase client connections and operations"""
    
    def __init__(self):
        self.client: Optional[Client] = None
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Supabase client"""
        try:
            url = os.getenv('SUPABASE_URL')
            key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
            
            if not url or not key:
                raise ValueError("Supabase credentials not found in environment")
            
            self.client = create_client(url, key)
            logger.info("✅ Supabase client initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase client: {e}")
            raise
    
    def get_client(self) -> Client:
        """Get the Supabase client instance"""
        if not self.client:
            self._initialize_client()
        return self.client
    
    # CRUD Operations
    async def create_document(self, table_name: str, document: Dict[str, Any]) -> str:
        """Create a new document in the specified table"""
        try:
            # Convert datetime objects to ISO string format
            document = self._serialize_document(document)
            
            result = self.client.table(table_name).insert(document).execute()
            return result.data[0]['id'] if result.data else None
        except Exception as e:
            logger.error(f"Create failed for table {table_name}: {e}")
            raise
    
    def _serialize_document(self, doc: Dict[str, Any]) -> Dict[str, Any]:
        """Convert datetime objects to ISO string format for JSON serialization"""
        serialized = {}
        for key, value in doc.items():
            if isinstance(value, datetime):
                serialized[key] = value.isoformat()
            elif isinstance(value, dict):
                serialized[key] = self._serialize_document(value)
            elif isinstance(value, list):
                serialized[key] = [
                    self._serialize_document(item) if isinstance(item, dict)
                    else item.isoformat() if isinstance(item, datetime)
                    else item
                    for item in value
                ]
            else:
                serialized[key] = value
        return serialized
    
    async def find_document(self, table_name: str, query: Dict[str, Any]) -> Optional[Dict]:
        """Find a single document"""
        try:
            # Build query
            query_builder = self.client.table(table_name).select('*')
            
            # Apply filters
            for key, value in query.items():
                query_builder = query_builder.eq(key, value)
            
            result = query_builder.limit(1).execute()
            return result.data[0] if result.data else None
            
        except Exception as e:
            logger.error(f"Find failed for table {table_name}: {e}")
            raise
    
    async def find_documents(self, table_name: str, query: Dict[str, Any] = None, 
                           skip: int = 0, limit: int = 100, 
                           order_by: str = None, ascending: bool = True) -> List[Dict]:
        """Find multiple documents"""
        try:
            query_builder = self.client.table(table_name).select('*')
            
            # Apply filters
            if query:
                for key, value in query.items():
                    if isinstance(value, list):
                        query_builder = query_builder.in_(key, value)
                    else:
                        query_builder = query_builder.eq(key, value)
            
            # Apply ordering
            if order_by:
                query_builder = query_builder.order(order_by, desc=not ascending)
            
            # Apply pagination
            if skip > 0:
                query_builder = query_builder.range(skip, skip + limit - 1)
            else:
                query_builder = query_builder.limit(limit)
            
            result = query_builder.execute()
            return result.data or []
            
        except Exception as e:
            logger.error(f"Find documents failed for table {table_name}: {e}")
            raise
    
    async def update_document(self, table_name: str, document_id: str, 
                            update: Dict[str, Any]) -> bool:
        """Update a document"""
        try:
            # Convert datetime objects to ISO string format
            update = self._serialize_document(update)
            
            result = self.client.table(table_name).update(update).eq('id', document_id).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Update failed for table {table_name}: {e}")
            raise
    
    async def delete_document(self, table_name: str, document_id: str) -> bool:
        """Delete a document"""
        try:
            result = self.client.table(table_name).delete().eq('id', document_id).execute()
            # Supabase delete returns empty data on success, so we check if no error occurred
            return True  # If no exception was raised, deletion was successful
        except Exception as e:
            logger.error(f"Delete failed for table {table_name}: {e}")
            # Check if it's a "not found" error vs actual failure
            if "PGRST116" in str(e) or "no rows" in str(e).lower():
                return False  # Document not found
            raise  # Re-raise other exceptions
    
    async def count_documents(self, table_name: str, query: Dict[str, Any] = None) -> int:
        """Count documents matching query"""
        try:
            query_builder = self.client.table(table_name).select('id', count='exact')
            
            if query:
                for key, value in query.items():
                    query_builder = query_builder.eq(key, value)
            
            result = query_builder.execute()
            return result.count or 0
            
        except Exception as e:
            logger.error(f"Count failed for table {table_name}: {e}")
            raise

    async def bulk_update_documents(self, table_name: str, query: Dict[str, Any], update: Dict[str, Any]) -> int:
        """Update multiple documents matching query"""
        try:
            # Convert datetime objects to ISO string format
            update = self._serialize_document(update)
            
            query_builder = self.client.table(table_name).update(update)
            
            # Apply query filters
            if query:
                for key, value in query.items():
                    query_builder = query_builder.eq(key, value)
            
            result = query_builder.execute()
            return len(result.data) if result.data else 0
            
        except Exception as e:
            logger.error(f"Bulk update failed for table {table_name}: {e}")
            raise

    async def bulk_delete_documents(self, table_name: str, query: Dict[str, Any]) -> int:
        """Delete multiple documents matching query"""
        try:
            query_builder = self.client.table(table_name).delete()
            
            # Apply query filters
            if query:
                for key, value in query.items():
                    query_builder = query_builder.eq(key, value)
            
            result = query_builder.execute()
            return len(result.data) if result.data else 0
            
        except Exception as e:
            logger.error(f"Bulk delete failed for table {table_name}: {e}")
            raise

    async def atomic_update_document(self, table_name: str, query: Dict[str, Any], update: Dict[str, Any]):
        """Atomic update - for Supabase, this is just a regular update with RLS protection"""
        document_id = query.get('id')
        if not document_id:
            # Find document first if only other fields provided
            docs = await self.find_documents(table_name, query, limit=1)
            if docs:
                document_id = docs[0]['id']
            else:
                raise ValueError("Document not found for atomic update")
        
        return await self.update_document(table_name, document_id, update)

    async def aggregate_documents(self, table_name: str, pipeline: List[Dict]) -> List[Dict]:
        """
        Simplified aggregation for Supabase - handles basic grouping and filtering
        Note: This is a simplified version. Complex MongoDB aggregations may need to be rewritten.
        """
        try:
            # For now, return basic query results - complex aggregations need to be rewritten
            # This is a placeholder to prevent immediate errors
            logger.warning(f"Aggregation pipeline not fully supported for {table_name}, returning basic query")
            return await self.find_documents(table_name, {}, limit=100)
            
        except Exception as e:
            logger.error(f"Aggregation failed for table {table_name}: {e}")
            raise

# Global instance
supabase_manager = SupabaseManager()

# Helper functions for compatibility with existing code
async def get_supabase_client():
    """Get the Supabase client - replaces get_database()"""
    return supabase_manager.get_client()

# CRUD helpers - compatible with existing database.py interface
async def create_document(table_name: str, document: Dict[str, Any]):
    """Create a new document"""
    return await supabase_manager.create_document(table_name, document)

async def find_document(table_name: str, query: Dict[str, Any]):
    """Find a single document"""
    return await supabase_manager.find_document(table_name, query)

async def find_documents(table_name: str, query: Dict[str, Any] = None, 
                        skip: int = 0, limit: int = 100, 
                        sort: List[tuple] = None):
    """Find multiple documents"""
    # Convert sort format if provided
    order_by = None
    ascending = True
    if sort and len(sort) > 0:
        field, direction = sort[0]
        order_by = field
        ascending = direction == 1
    
    return await supabase_manager.find_documents(table_name, query, skip, limit, order_by, ascending)

async def update_document(table_name: str, query: Dict[str, Any], update: Dict[str, Any]):
    """Update a document - modified to work with Supabase"""
    # Assume query contains 'id' for Supabase
    document_id = query.get('id')
    if not document_id:
        raise ValueError("Document ID required for Supabase updates")
    
    return await supabase_manager.update_document(table_name, document_id, update)

async def delete_document(table_name: str, query: Dict[str, Any]):
    """Delete a document"""
    document_id = query.get('id')
    if not document_id:
        raise ValueError("Document ID required for Supabase deletes")
    
    return await supabase_manager.delete_document(table_name, document_id)

async def count_documents(table_name: str, query: Dict[str, Any] = None):
    """Count documents matching query"""
    return await supabase_manager.count_documents(table_name, query)

async def atomic_update_document(table_name: str, query: Dict[str, Any], update: Dict[str, Any]):
    """Atomic update document"""
    return await supabase_manager.atomic_update_document(table_name, query, update)

async def aggregate_documents(table_name: str, pipeline: List[Dict]) -> List[Dict]:
    """Aggregate documents - simplified for Supabase"""
    return await supabase_manager.aggregate_documents(table_name, pipeline)

async def bulk_update_documents(table_name: str, query: Dict[str, Any], update: Dict[str, Any]) -> int:
    """Update multiple documents matching query"""
    return await supabase_manager.bulk_update_documents(table_name, query, update)

async def bulk_delete_documents(table_name: str, query: Dict[str, Any]) -> int:
    """Delete multiple documents matching query"""
    return await supabase_manager.bulk_delete_documents(table_name, query)

async def delete_documents(table_name: str, query: Dict[str, Any]) -> int:
    """Delete multiple documents matching query (alias for bulk_delete_documents)"""
    return await bulk_delete_documents(table_name, query)