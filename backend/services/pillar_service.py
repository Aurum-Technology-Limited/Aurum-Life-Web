"""
Pillar Service Layer for Aurum Life MVP v1.2
Handles all business logic for Pillar operations
"""

from typing import List, Optional, Dict
from datetime import datetime
from uuid import uuid4
from supabase import Client
from models_validated import PillarCreate, PillarUpdate, PillarResponse
from optimized_queries import OptimizedQueryService
import logging

logger = logging.getLogger(__name__)

class PillarService:
    """
    Service layer for Pillar operations
    Encapsulates all business logic and database interactions
    """
    
    def __init__(self, supabase_client: Client):
        self.client = supabase_client
        self.query_service = OptimizedQueryService(supabase_client)
        
    async def create_pillar(self, user_id: str, pillar_data: PillarCreate) -> PillarResponse:
        """
        Create a new pillar for a user
        
        Args:
            user_id: The user's ID
            pillar_data: Validated pillar creation data
            
        Returns:
            Created pillar with computed fields
            
        Raises:
            Exception: If creation fails
        """
        try:
            # Prepare pillar data
            pillar_dict = pillar_data.dict()
            pillar_dict.update({
                "id": str(uuid4()),
                "user_id": user_id,
                "created_at": datetime.utcnow(),
                "updated_at": datetime.utcnow(),
                "archived": False,
                "sort_order": await self._get_next_sort_order(user_id)
            })
            
            # Create in database
            response = await self.client.from_("pillars").insert(pillar_dict).execute()
            
            if not response.data:
                raise Exception("Failed to create pillar")
                
            # Get full pillar with stats
            created_pillar = await self.get_pillar_by_id(user_id, response.data[0]["id"])
            
            logger.info(f"Created pillar {created_pillar.id} for user {user_id}")
            return created_pillar
            
        except Exception as e:
            logger.error(f"Failed to create pillar: {e}")
            raise
    
    async def get_user_pillars(self, user_id: str, include_archived: bool = False) -> List[PillarResponse]:
        """
        Get all pillars for a user with statistics
        
        Args:
            user_id: The user's ID
            include_archived: Whether to include archived pillars
            
        Returns:
            List of pillars with computed statistics
        """
        try:
            # Use optimized query
            hierarchy = await self.query_service.get_user_hierarchy(user_id)
            
            pillars = []
            for pillar_data in hierarchy.get("pillars", []):
                if not include_archived and pillar_data.get("archived", False):
                    continue
                    
                # Calculate statistics
                stats = self._calculate_pillar_stats(pillar_data)
                
                pillar = PillarResponse(
                    **pillar_data,
                    **stats
                )
                pillars.append(pillar)
                
            return pillars
            
        except Exception as e:
            logger.error(f"Failed to get user pillars: {e}")
            return []
    
    async def get_pillar_by_id(self, user_id: str, pillar_id: str) -> Optional[PillarResponse]:
        """
        Get a single pillar with full statistics
        
        Args:
            user_id: The user's ID (for ownership verification)
            pillar_id: The pillar's ID
            
        Returns:
            Pillar with statistics or None if not found
        """
        try:
            # Get pillar with stats from optimized query
            pillar_data = await self.query_service.get_pillar_with_stats(user_id, pillar_id)
            
            if not pillar_data:
                return None
                
            return PillarResponse(**pillar_data)
            
        except Exception as e:
            logger.error(f"Failed to get pillar {pillar_id}: {e}")
            return None
    
    async def update_pillar(
        self, 
        user_id: str, 
        pillar_id: str, 
        update_data: PillarUpdate
    ) -> Optional[PillarResponse]:
        """
        Update a pillar
        
        Args:
            user_id: The user's ID (for ownership verification)
            pillar_id: The pillar's ID
            update_data: Validated update data
            
        Returns:
            Updated pillar or None if not found
        """
        try:
            # Verify ownership
            existing = await self.get_pillar_by_id(user_id, pillar_id)
            if not existing:
                return None
                
            # Prepare update
            update_dict = update_data.dict(exclude_unset=True)
            update_dict["updated_at"] = datetime.utcnow()
            
            # Execute update
            response = await self.client.from_("pillars").update(
                update_dict
            ).eq("id", pillar_id).eq("user_id", user_id).execute()
            
            if not response.data:
                raise Exception("Update failed")
                
            # Return updated pillar with stats
            return await self.get_pillar_by_id(user_id, pillar_id)
            
        except Exception as e:
            logger.error(f"Failed to update pillar {pillar_id}: {e}")
            return None
    
    async def delete_pillar(self, user_id: str, pillar_id: str) -> bool:
        """
        Delete a pillar (soft delete by archiving)
        
        Args:
            user_id: The user's ID (for ownership verification)
            pillar_id: The pillar's ID
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Soft delete by archiving
            response = await self.client.from_("pillars").update({
                "archived": True,
                "updated_at": datetime.utcnow()
            }).eq("id", pillar_id).eq("user_id", user_id).execute()
            
            success = len(response.data) > 0
            
            if success:
                logger.info(f"Archived pillar {pillar_id} for user {user_id}")
                
            return success
            
        except Exception as e:
            logger.error(f"Failed to delete pillar {pillar_id}: {e}")
            return False
    
    async def reorder_pillars(self, user_id: str, pillar_order: List[str]) -> bool:
        """
        Reorder user's pillars
        
        Args:
            user_id: The user's ID
            pillar_order: List of pillar IDs in desired order
            
        Returns:
            True if successful, False otherwise
        """
        try:
            # Update sort order for each pillar
            updates = []
            for index, pillar_id in enumerate(pillar_order):
                updates.append({
                    "id": pillar_id,
                    "sort_order": index,
                    "updated_at": datetime.utcnow()
                })
                
            # Batch update
            response = await self.client.from_("pillars").upsert(
                updates,
                on_conflict="id"
            ).eq("user_id", user_id).execute()
            
            return len(response.data) == len(updates)
            
        except Exception as e:
            logger.error(f"Failed to reorder pillars: {e}")
            return False
    
    # Private helper methods
    
    async def _get_next_sort_order(self, user_id: str) -> int:
        """Get the next sort order value for a new pillar"""
        try:
            response = await self.client.from_("pillars").select(
                "sort_order"
            ).eq("user_id", user_id).order(
                "sort_order", desc=True
            ).limit(1).execute()
            
            if response.data:
                return response.data[0]["sort_order"] + 1
            return 0
            
        except Exception:
            return 0
    
    def _calculate_pillar_stats(self, pillar_data: Dict) -> Dict:
        """Calculate statistics for a pillar from hierarchy data"""
        stats = {
            "area_count": 0,
            "project_count": 0,
            "task_count": 0,
            "completed_task_count": 0,
            "progress_percentage": 0.0
        }
        
        areas = pillar_data.get("areas", [])
        stats["area_count"] = len(areas)
        
        for area in areas:
            projects = area.get("projects", [])
            stats["project_count"] += len(projects)
            
            for project in projects:
                task_stats = project.get("task_stats", {})
                total = task_stats.get("total", 0)
                completed = task_stats.get("completed", 0)
                
                stats["task_count"] += total
                stats["completed_task_count"] += completed
        
        # Calculate progress
        if stats["task_count"] > 0:
            stats["progress_percentage"] = round(
                (stats["completed_task_count"] / stats["task_count"]) * 100, 
                2
            )
            
        return stats