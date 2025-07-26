"""
Supabase Client Configuration for Aurum Life
Replaces MongoDB database.py
"""

import os
from typing import Optional, Dict, Any, List
from supabase import create_client, Client
from dotenv import load_dotenv
import logging

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
            result = self.client.table(table_name).insert(document).execute()
            return result.data[0]['id'] if result.data else None
        except Exception as e:
            logger.error(f"Create failed for table {table_name}: {e}")
            raise
    
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
            result = self.client.table(table_name).update(update).eq('id', document_id).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Update failed for table {table_name}: {e}")
            raise
    
    async def delete_document(self, table_name: str, document_id: str) -> bool:
        """Delete a document"""
        try:
            result = self.client.table(table_name).delete().eq('id', document_id).execute()
            return len(result.data) > 0
        except Exception as e:
            logger.error(f"Delete failed for table {table_name}: {e}")
            raise
    
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