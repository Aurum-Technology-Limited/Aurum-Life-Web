from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from models import *
from supabase_client import find_document, find_documents, create_document, update_document, delete_document
import logging

logger = logging.getLogger(__name__)

class JournalService:
    @staticmethod
    async def create_entry(user_id: str, entry_data: JournalEntryCreate) -> JournalEntry:
        """Create a new journal entry"""
        # Calculate word count and reading time
        word_count = len(entry_data.content.split())
        reading_time_minutes = max(1, word_count // 200)  # Assume 200 words per minute
        
        entry_dict = entry_data.dict()
        entry_dict.update({
            "user_id": user_id,
            "word_count": word_count,
            "reading_time_minutes": reading_time_minutes,
            "created_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        })
        
        # Create the entry
        entry_id = await create_document("journal_entries", entry_dict)
        if entry_id:
            entry_dict["id"] = entry_id
            return JournalEntry(**entry_dict)
        else:
            raise Exception("Failed to create journal entry - no ID returned")
    
    @staticmethod
    async def get_user_entries(user_id: str, skip: int = 0, limit: int = 20, 
                              mood_filter: Optional[str] = None,
                              tag_filter: Optional[str] = None,
                              date_from: Optional[datetime] = None,
                              date_to: Optional[datetime] = None) -> List[JournalEntryResponse]:
        """Get journal entries for user (all entries since soft delete not implemented yet)"""
        # For now, get all entries since soft delete columns don't exist in Supabase table
        docs = await find_documents("journal_entries", {"user_id": user_id}, skip=skip, limit=limit, sort=[("created_at", -1)])
        responses = []
        for doc in docs:
            responses.append(await JournalService._build_journal_entry_response(doc))
        return responses
    
    @staticmethod
    async def get_deleted_entries(user_id: str, skip: int = 0, limit: int = 20) -> List[JournalEntryResponse]:
        """List soft-deleted entries for Trash view"""
        query = {"user_id": user_id, "deleted": True}
        docs = await find_documents("journal_entries", query, skip=skip, limit=limit)
        
        # Sort by deleted_at desc with fallback to created_at
        def sort_key(x):
            dt = x.get("deleted_at") or x.get("created_at")
            try:
                return dt if isinstance(dt, datetime) else datetime.fromisoformat(str(dt).replace('Z', '+00:00'))
            except Exception:
                return datetime.min
        docs.sort(key=sort_key, reverse=True)
        
        responses = []
        for doc in docs:
            responses.append(await JournalService._build_journal_entry_response(doc))
        return responses
    
    @staticmethod
    async def soft_delete_entry(user_id: str, entry_id: str) -> bool:
        """Soft delete a journal entry"""
        query = {"id": entry_id, "user_id": user_id}
        update_data = {
            "deleted": True,
            "deleted_at": datetime.utcnow(),
            "updated_at": datetime.utcnow()
        }
        return await update_document("journal_entries", query, update_data)
    
    @staticmethod
    async def restore_entry(user_id: str, entry_id: str) -> bool:
        """Restore a soft-deleted journal entry"""
        query = {"id": entry_id, "user_id": user_id, "deleted": True}
        update_data = {
            "deleted": False,
            "deleted_at": None,
            "updated_at": datetime.utcnow()
        }
        return await update_document("journal_entries", query, update_data)
    
    @staticmethod
    async def purge_entry(user_id: str, entry_id: str) -> bool:
        """Permanently delete a journal entry (Trash purge)"""
        # Verify ownership and that it's soft-deleted first
        doc = await find_document("journal_entries", {"id": entry_id, "user_id": user_id, "deleted": True})
        if not doc:
            return False
        return await delete_document("journal_entries", {"id": entry_id})
    
    @staticmethod
    async def update_entry(user_id: str, entry_id: str, entry_data: JournalEntryUpdate) -> bool:
        """Update a journal entry"""
        query = {"id": entry_id, "user_id": user_id, "deleted": {"$ne": True}}
        
        update_dict = entry_data.dict(exclude_unset=True)
        if update_dict:
            # Recalculate word count and reading time if content changed
            if "content" in update_dict:
                word_count = len(update_dict["content"].split())
                update_dict["word_count"] = word_count
                update_dict["reading_time_minutes"] = max(1, word_count // 200)
            
            update_dict["updated_at"] = datetime.utcnow()
            return await update_document("journal_entries", query, update_dict)
        return False
    
    @staticmethod
    async def get_entry_by_id(user_id: str, entry_id: str) -> Optional[JournalEntryResponse]:
        """Get a specific journal entry by ID"""
        doc = await find_document("journal_entries", {"id": entry_id, "user_id": user_id, "deleted": {"$ne": True}})
        if doc:
            return await JournalService._build_journal_entry_response(doc)
        return None
    
    @staticmethod
    async def search_entries(user_id: str, query: str, limit: int = 20) -> List[JournalEntryResponse]:
        """Search journal entries by content"""
        search_query = {
            "user_id": user_id,
            "deleted": {"$ne": True},
            "$or": [
                {"title": {"$regex": query, "$options": "i"}},
                {"content": {"$regex": query, "$options": "i"}},
                {"tags": {"$in": [query]}}
            ]
        }
        
        docs = await find_documents("journal_entries", search_query, limit=limit, sort=[("created_at", -1)])
        responses = []
        for doc in docs:
            responses.append(await JournalService._build_journal_entry_response(doc))
        return responses
    
    @staticmethod
    async def get_on_this_day(user_id: str, date: datetime) -> List[OnThisDayEntry]:
        """Get journal entries from the same date in previous years"""
        # Get entries from the same month/day in previous years
        entries = []
        for year_offset in range(1, 6):  # Look back 5 years
            target_date = date.replace(year=date.year - year_offset)
            start_date = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
            end_date = start_date + timedelta(days=1)
            
            query = {
                "user_id": user_id,
                "deleted": {"$ne": True},
                "created_at": {"$gte": start_date, "$lt": end_date}
            }
            
            docs = await find_documents("journal_entries", query, sort=[("created_at", -1)])
            for doc in docs:
                entries.append(OnThisDayEntry(
                    id=doc["id"],
                    title=doc["title"],
                    content=doc["content"][:200] + "..." if len(doc["content"]) > 200 else doc["content"],
                    created_at=doc["created_at"],
                    years_ago=year_offset
                ))
        
        return entries
    
    @staticmethod
    async def get_journal_insights(user_id: str) -> JournalInsights:
        """Get comprehensive journal analytics and insights"""
        # Get all non-deleted entries
        all_entries = await find_documents("journal_entries", {"user_id": user_id, "deleted": {"$ne": True}})
        
        if not all_entries:
            return JournalInsights(
                total_entries=0,
                current_streak=0,
                most_common_mood="reflective",
                average_energy_level=3.0,
                most_used_tags=[],
                mood_trend=[],
                energy_trend=[],
                writing_stats={}
            )
        
        # Calculate insights
        total_entries = len(all_entries)
        
        # Calculate current streak
        current_streak = await JournalService._calculate_streak(all_entries)
        
        # Most common mood
        mood_counts = {}
        energy_levels = []
        all_tags = []
        total_words = 0
        
        for entry in all_entries:
            mood = entry.get("mood", "reflective")
            mood_counts[mood] = mood_counts.get(mood, 0) + 1
            
            energy_level = entry.get("energy_level", "moderate")
            energy_map = {"very_low": 1, "low": 2, "moderate": 3, "high": 4, "very_high": 5}
            energy_levels.append(energy_map.get(energy_level, 3))
            
            all_tags.extend(entry.get("tags", []))
            total_words += entry.get("word_count", 0)
        
        most_common_mood = max(mood_counts, key=mood_counts.get) if mood_counts else "reflective"
        average_energy_level = sum(energy_levels) / len(energy_levels) if energy_levels else 3.0
        
        # Most used tags
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        most_used_tags = [{"tag": tag, "count": count} for tag, count in 
                         sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]]
        
        return JournalInsights(
            total_entries=total_entries,
            current_streak=current_streak,
            most_common_mood=most_common_mood,
            average_energy_level=average_energy_level,
            most_used_tags=most_used_tags,
            mood_trend=[],  # Could implement trend analysis
            energy_trend=[],  # Could implement trend analysis
            writing_stats={
                "total_words": total_words,
                "average_words_per_entry": total_words / total_entries if total_entries > 0 else 0,
                "total_reading_time_minutes": sum(entry.get("reading_time_minutes", 0) for entry in all_entries)
            }
        )
    
    @staticmethod
    async def _build_journal_entry_response(doc: dict) -> JournalEntryResponse:
        """Build a JournalEntryResponse from a document"""
        return JournalEntryResponse(
            id=doc["id"],
            user_id=doc["user_id"],
            title=doc["title"],
            content=doc["content"],
            mood=doc.get("mood", "reflective"),
            energy_level=doc.get("energy_level", "moderate"),
            tags=doc.get("tags", []),
            template_id=doc.get("template_id"),
            template_name=None,  # Could be populated if needed
            template_responses=doc.get("template_responses", {}),
            weather=doc.get("weather"),
            location=doc.get("location"),
            word_count=doc.get("word_count", 0),
            reading_time_minutes=doc.get("reading_time_minutes", 0),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"]
        )
    
    @staticmethod
    async def _calculate_streak(entries: List[dict]) -> int:
        """Calculate current writing streak"""
        if not entries:
            return 0
        
        # Sort entries by date
        entries.sort(key=lambda x: x["created_at"], reverse=True)
        
        streak = 0
        current_date = datetime.utcnow().date()
        
        # Check if there's an entry today or yesterday to start the streak
        latest_entry_date = entries[0]["created_at"].date()
        if (current_date - latest_entry_date).days > 1:
            return 0
        
        # Count consecutive days
        for i, entry in enumerate(entries):
            entry_date = entry["created_at"].date()
            expected_date = current_date - timedelta(days=i)
            
            if entry_date == expected_date:
                streak += 1
            else:
                break
        
        return streak
    
    @staticmethod
    async def initialize_default_templates():
        """Initialize default journal templates - placeholder implementation"""
        # This is a placeholder to prevent startup errors
        # Could be implemented to create default templates
        pass


# Placeholder service classes to satisfy imports
class UserService:
    pass

class TaskService:
    pass

class CourseService:
    pass

class RecurringTaskService:
    pass

class InsightsService:
    pass

class ResourceService:
    pass

class StatsService:
    pass

class PillarService:
    pass

class AreaService:
    pass

class ProjectService:
    pass

class ProjectTemplateService:
    pass

class GoogleAuthService:
    pass