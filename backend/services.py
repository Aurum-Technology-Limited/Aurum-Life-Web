import secrets
import hashlib
import os
from typing import List, Optional
from datetime import datetime, timedelta
from supabase_client import (
    create_document, find_document, find_documents,
    update_document, delete_document, count_documents, supabase_manager,
    atomic_update_document, aggregate_documents
)
from models import *
from auth import get_password_hash, verify_password
import json
import logging
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

logger = logging.getLogger(__name__)

class UserService:
    @staticmethod
    async def create_user(user_data: UserCreate) -> User:
        # Check if user already exists
        existing_user = await UserService.get_user_by_email(user_data.email)
        if existing_user:
            raise ValueError("User with this email already exists")
        
        # Hash the password
        password_hash = get_password_hash(user_data.password)
        
        # Create user without the plain password
        user_dict = user_data.dict()
        user_dict.pop('password')  # Remove plain password
        user_dict['password_hash'] = password_hash
        
        user = User(**user_dict)
        user_dict = user.dict()
        await create_document("users", user_dict)
        
        # Initialize user stats - with error handling
        try:
            stats = UserStats(user_id=user.id)
            stats_dict = stats.dict()
            # Remove any fields that might cause schema issues
            if 'last_updated' in stats_dict:
                stats_dict.pop('last_updated')
            await create_document("user_stats", stats_dict)
        except Exception as e:
            logger.warning(f"Failed to create user stats for {user.email}: {e}")
            # Don't fail user creation if stats creation fails
        
        return user

    @staticmethod
    async def authenticate_user(email: str, password: str) -> Optional[User]:
        user = await UserService.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    async def get_user_by_email(email: str) -> Optional[User]:
        user_doc = await find_document("users", {"email": email})
        return User(**user_doc) if user_doc else None

    @staticmethod
    async def get_user(user_id: str) -> Optional[User]:
        user_doc = await find_document("users", {"id": user_id})
        return User(**user_doc) if user_doc else None

    @staticmethod
    async def update_user(user_id: str, user_data: UserUpdate) -> bool:
        update_data = {k: v for k, v in user_data.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        return await update_document("users", {"id": user_id}, update_data)

    @staticmethod
    async def update_user_profile(user_id: str, first_name: str = None, last_name: str = None) -> bool:
        update_data = {"updated_at": datetime.utcnow()}
        if first_name is not None:
            update_data["first_name"] = first_name
        if last_name is not None:
            update_data["last_name"] = last_name
        return await update_document("users", {"id": user_id}, update_data)

    @staticmethod
    async def create_password_reset_token(email: str) -> Optional[str]:
        """
        Create a password reset token for the user
        Returns the token if user exists, None otherwise
        """
        # Check if user exists
        user = await UserService.get_user_by_email(email)
        if not user:
            return None
        
        # Generate secure reset token
        reset_token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(reset_token.encode()).hexdigest()
        
        # Calculate expiration time
        expiry_hours = int(os.getenv('RESET_TOKEN_EXPIRY_HOURS', 24))
        expires_at = datetime.utcnow() + timedelta(hours=expiry_hours)
        
        # Invalidate any existing reset tokens for this user
        existing_tokens = await find_documents("password_reset_tokens", 
                                              {"user_id": user.id, "is_used": False})
        for token_doc in existing_tokens:
            await update_document("password_reset_tokens", 
                                {"id": token_doc["id"]}, 
                                {"is_used": True})
        
        # Create new reset token
        reset_token_obj = PasswordResetToken(
            user_id=user.id,
            token=token_hash,
            expires_at=expires_at
        )
        
        await create_document("password_reset_tokens", reset_token_obj.dict())
        
        return reset_token  # Return the plain token, not the hash

    @staticmethod
    async def verify_reset_token(token: str) -> Optional[User]:
        """
        Verify password reset token and return associated user
        Returns User if token is valid, None otherwise
        """
        # Hash the provided token to match stored hash
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        # Find the token
        token_data = await find_document("password_reset_tokens", {
            "token": token_hash,
            "is_used": False
        })
        
        if not token_data:
            return None
        
        # Check if token has expired
        token_obj = PasswordResetToken(**token_data)
        if datetime.utcnow() > token_obj.expires_at:
            # Mark token as used (expired)
            await update_document("password_reset_tokens", 
                                {"token": token_hash}, 
                                {"is_used": True})
            return None
        
        # Get the user associated with this token
        return await UserService.get_user(token_obj.user_id)

    @staticmethod
    async def reset_password(token: str, new_password: str) -> bool:
        """
        Reset user password using the reset token
        Returns True if successful, False otherwise
        """
        # Verify token and get user
        user = await UserService.verify_reset_token(token)
        if not user:
            return False
        
        # Hash the provided token to mark as used
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        # Update user's password
        new_password_hash = get_password_hash(new_password)
        await update_document("users", {"id": user.id}, {"password_hash": new_password_hash})
        
        # Mark token as used
        await update_document("password_reset_tokens", 
                            {"token": token_hash}, 
                            {"is_used": True})
        
        return True

class GoogleAuthService:
    @staticmethod
    async def verify_google_token(token: str) -> Optional[dict]:
        """Verify Google ID token and return user info"""
        try:
            # Verify the token with Google
            idinfo = id_token.verify_oauth2_token(
                token, 
                google_requests.Request(), 
                os.environ.get('GOOGLE_CLIENT_ID')
            )
            
            # Validate the issuer
            if idinfo['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
                raise ValueError('Wrong issuer.')
            
            return {
                'google_id': idinfo['sub'],
                'email': idinfo['email'],
                'name': idinfo['name'],
                'picture': idinfo.get('picture', ''),
                'email_verified': idinfo.get('email_verified', False)
            }
        except ValueError as e:
            print(f"Google token verification failed: {e}")
            return None
    
    @staticmethod
    async def authenticate_or_create_user(google_user_info: dict) -> Optional[User]:
        """Find existing user or create new one from Google auth"""
        try:
            # Try to find existing user by email
            existing_user = await find_document("users", {"email": google_user_info['email']})
            
            if existing_user:
                # Update user's Google info if it's new
                update_data = {}
                if not existing_user.get('google_id'):
                    update_data['google_id'] = google_user_info['google_id']
                if not existing_user.get('profile_picture') and google_user_info.get('picture'):
                    update_data['profile_picture'] = google_user_info['picture']
                
                if update_data:
                    update_data['updated_at'] = datetime.utcnow()
                    await update_document("users", {"id": existing_user['id']}, update_data)
                    existing_user.update(update_data)
                
                return User(**existing_user)
            else:
                # Create new user from Google info
                name_parts = google_user_info['name'].split(' ', 1)
                first_name = name_parts[0]
                last_name = name_parts[1] if len(name_parts) > 1 else ''
                
                # Generate username from email
                username = google_user_info['email'].split('@')[0]
                # Make sure username is unique
                counter = 1
                original_username = username
                while await find_document("users", {"username": username}):
                    username = f"{original_username}{counter}"
                    counter += 1
                
                new_user = User(
                    email=google_user_info['email'],
                    username=username,
                    first_name=first_name,
                    last_name=last_name,
                    google_id=google_user_info['google_id'],
                    profile_picture=google_user_info.get('picture', ''),
                    is_active=True,
                    level=1,
                    total_points=0,
                    current_streak=0
                )
                
                user_dict = new_user.dict()
                await create_document("users", user_dict)
                return new_user
                
        except Exception as e:
            print(f"Error in Google auth user creation/retrieval: {e}")
            return None

class JournalService:
    @staticmethod
    async def _build_journal_entry_response(doc: dict) -> JournalEntryResponse:
        """Helper function to consistently build JournalEntryResponse objects"""
        # Set template_name to None by default
        doc["template_name"] = None
        
        # Get template name if template was used
        if doc.get("template_id"):
            template_doc = await find_document("journal_templates", {"id": doc["template_id"]})
            if template_doc:
                doc["template_name"] = template_doc["name"]
        
        return JournalEntryResponse(**doc)

    @staticmethod
    async def create_entry(user_id: str, entry_data: JournalEntryCreate) -> JournalEntry:
        # Calculate word count and reading time
        word_count = len(entry_data.content.split())
        reading_time_minutes = max(1, word_count // 200)  # Assume 200 words per minute
        
        entry = JournalEntry(
            user_id=user_id, 
            word_count=word_count,
            reading_time_minutes=reading_time_minutes,
            **entry_data.dict()
        )
        entry_dict = entry.dict()
        await create_document("journal_entries", entry_dict)
        
        # Update template usage count if template was used
        if entry_data.template_id:
            await atomic_update_document("journal_templates", 
                                        {"id": entry_data.template_id},
                                        {"$inc": {"usage_count": 1}})
        
        # Trigger achievement check for journal entry creation (performance-optimized)
        try:
            await AchievementService.trigger_journal_entry_created(user_id)
            # Also trigger custom achievements check
            await CustomAchievementService.trigger_custom_achievements_check(
                user_id, "journal_entry_created"
            )
        except Exception as e:
            print(f"Warning: Achievement trigger failed for journal entry creation: {e}")
        
        return entry

    @staticmethod
    async def get_user_entries(user_id: str, skip: int = 0, limit: int = 20, 
                              mood_filter: Optional[str] = None,
                              tag_filter: Optional[str] = None,
                              date_from: Optional[datetime] = None,
                              date_to: Optional[datetime] = None) -> List[JournalEntryResponse]:
        # Build query with filters
        query = {"user_id": user_id}
        
        if mood_filter:
            query["mood"] = mood_filter
            
        if tag_filter:
            query["tags"] = {"$in": [tag_filter]}
            
        if date_from or date_to:
            date_query = {}
            if date_from:
                date_query["$gte"] = date_from
            if date_to:
                date_query["$lte"] = date_to
            query["created_at"] = date_query
        
        entries_docs = await find_documents(
            "journal_entries", 
            query,
            skip=skip, 
            limit=limit
        )
        
        # Sort by created_at descending
        entries_docs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        
        # Build response objects with template names
        responses = []
        for doc in entries_docs:
            response = await JournalService._build_journal_entry_response(doc)
            responses.append(response)
        
        return responses

    @staticmethod
    async def update_entry(user_id: str, entry_id: str, entry_data: JournalEntryUpdate) -> bool:
        update_data = {k: v for k, v in entry_data.dict().items() if v is not None}
        
        # Recalculate word count and reading time if content changed
        if "content" in update_data:
            word_count = len(update_data["content"].split())
            reading_time_minutes = max(1, word_count // 200)
            update_data["word_count"] = word_count
            update_data["reading_time_minutes"] = reading_time_minutes
        
        update_data["updated_at"] = datetime.utcnow()
        return await update_document("journal_entries", {"id": entry_id, "user_id": user_id}, update_data)

    @staticmethod
    async def delete_entry(user_id: str, entry_id: str) -> bool:
        return await delete_document("journal_entries", {"id": entry_id, "user_id": user_id})

    @staticmethod
    async def search_entries(user_id: str, search_term: str, limit: int = 20) -> List[JournalEntryResponse]:
        """Search entries by title and content"""
        # Simple text search - in production, consider using full-text search
        entries_docs = await find_documents("journal_entries", {"user_id": user_id})
        
        matching_entries = []
        search_lower = search_term.lower()
        
        for doc in entries_docs:
            title_match = search_lower in doc.get("title", "").lower()
            content_match = search_lower in doc.get("content", "").lower()
            tag_match = any(search_lower in tag.lower() for tag in doc.get("tags", []))
            
            if title_match or content_match or tag_match:
                response = await JournalService._build_journal_entry_response(doc)
                matching_entries.append(response)
        
        # Sort by relevance (title matches first, then by date)
        matching_entries.sort(key=lambda x: (
            0 if search_lower in x.title.lower() else 1,
            -x.created_at.timestamp()
        ))
        
        return matching_entries[:limit]

    @staticmethod
    async def get_on_this_day(user_id: str, target_date: Optional[datetime] = None) -> List[OnThisDayEntry]:
        """Get journal entries from the same date in previous years"""
        if not target_date:
            target_date = datetime.now()
        
        # Get entries from same month/day in previous years
        month = target_date.month
        day = target_date.day
        current_year = target_date.year
        
        entries_docs = await find_documents("journal_entries", {"user_id": user_id})
        
        on_this_day_entries = []
        for doc in entries_docs:
            entry_date = doc.get("created_at")
            if (entry_date and 
                entry_date.month == month and 
                entry_date.day == day and 
                entry_date.year < current_year):
                
                years_ago = current_year - entry_date.year
                response = await JournalService._build_journal_entry_response(doc)
                
                on_this_day_entries.append(OnThisDayEntry(
                    entry=response,
                    years_ago=years_ago
                ))
        
        # Sort by years ago (most recent years first)
        on_this_day_entries.sort(key=lambda x: x.years_ago)
        
        return on_this_day_entries

    @staticmethod
    async def get_journal_insights(user_id: str) -> JournalInsights:
        """Get comprehensive journal analytics and insights"""
        entries_docs = await find_documents("journal_entries", {"user_id": user_id})
        
        if not entries_docs:
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
        
        # Sort entries by date
        entries_docs.sort(key=lambda x: x.get("created_at", datetime.min))
        
        # Calculate current streak
        current_streak = await JournalService._calculate_journal_streak(user_id)
        
        # Mood analysis
        mood_counts = {}
        energy_levels = []
        all_tags = []
        total_words = 0
        
        # Prepare last 30 days data
        thirty_days_ago = datetime.now() - timedelta(days=30)
        mood_trend = []
        energy_trend = []
        
        for doc in entries_docs:
            # Mood counting
            mood = doc.get("mood", "reflective")
            mood_counts[mood] = mood_counts.get(mood, 0) + 1
            
            # Energy levels
            energy_map = {
                "very_low": 1, "low": 2, "moderate": 3, "high": 4, "very_high": 5
            }
            energy = doc.get("energy_level", "moderate")
            energy_levels.append(energy_map.get(energy, 3))
            
            # Tags
            all_tags.extend(doc.get("tags", []))
            
            # Word count
            total_words += doc.get("word_count", 0)
            
            # Trend data (last 30 days)
            created_at = doc.get("created_at")
            if created_at and created_at >= thirty_days_ago:
                mood_trend.append({
                    "date": created_at.date().isoformat(),
                    "mood": mood,
                    "mood_score": {"optimistic": 5, "inspired": 5, "excited": 5, "grateful": 4, 
                                  "motivated": 4, "peaceful": 4, "reflective": 3, "challenging": 2, 
                                  "frustrated": 2, "anxious": 1}.get(mood, 3)
                })
                energy_trend.append({
                    "date": created_at.date().isoformat(),
                    "energy_level": energy,
                    "energy_score": energy_map.get(energy, 3)
                })
        
        # Most common mood
        most_common_mood = max(mood_counts.items(), key=lambda x: x[1])[0] if mood_counts else "reflective"
        
        # Average energy level
        average_energy = sum(energy_levels) / len(energy_levels) if energy_levels else 3.0
        
        # Most used tags
        tag_counts = {}
        for tag in all_tags:
            tag_counts[tag] = tag_counts.get(tag, 0) + 1
        
        most_used_tags = [
            {"tag": tag, "count": count} 
            for tag, count in sorted(tag_counts.items(), key=lambda x: x[1], reverse=True)[:10]
        ]
        
        # Writing statistics
        writing_stats = {
            "total_words": total_words,
            "average_words_per_entry": total_words / len(entries_docs) if entries_docs else 0,
            "total_reading_time_minutes": sum(doc.get("reading_time_minutes", 0) for doc in entries_docs),
            "entries_this_month": len([doc for doc in entries_docs 
                                     if doc.get("created_at", datetime.min).month == datetime.now().month]),
            "longest_entry_words": max((doc.get("word_count", 0) for doc in entries_docs), default=0)
        }
        
        return JournalInsights(
            total_entries=len(entries_docs),
            current_streak=current_streak,
            most_common_mood=most_common_mood,
            average_energy_level=round(average_energy, 1),
            most_used_tags=most_used_tags,
            mood_trend=mood_trend,
            energy_trend=energy_trend,
            writing_stats=writing_stats
        )

    @staticmethod
    async def _calculate_journal_streak(user_id: str) -> int:
        """Calculate current consecutive days of journaling"""
        entries_docs = await find_documents("journal_entries", {"user_id": user_id})
        
        if not entries_docs:
            return 0
        
        # Get unique dates of entries
        entry_dates = set()
        for doc in entries_docs:
            created_at = doc.get("created_at")
            if created_at:
                entry_dates.add(created_at.date())
        
        # Check consecutive days starting from today
        current_date = datetime.now().date()
        streak = 0
        
        while current_date in entry_dates:
            streak += 1
            current_date -= timedelta(days=1)
        
        return streak

    # Journal Template Methods
    @staticmethod
    async def create_template(user_id: str, template_data: JournalTemplateCreate) -> JournalTemplate:
        template = JournalTemplate(user_id=user_id, **template_data.dict())
        template_dict = template.dict()
        await create_document("journal_templates", template_dict)
        return template

    @staticmethod
    async def get_user_templates(user_id: str) -> List[JournalTemplate]:
        # Get user's custom templates and default system templates
        user_templates_docs = await find_documents("journal_templates", {"user_id": user_id})
        default_templates_docs = await find_documents("journal_templates", {"is_default": True})
        
        all_templates = user_templates_docs + default_templates_docs
        all_templates.sort(key=lambda x: (not x.get("is_default", False), x.get("name", "")))
        
        return [JournalTemplate(**doc) for doc in all_templates]

    @staticmethod
    async def get_template(template_id: str) -> Optional[JournalTemplate]:
        template_doc = await find_document("journal_templates", {"id": template_id})
        return JournalTemplate(**template_doc) if template_doc else None

    @staticmethod
    async def update_template(user_id: str, template_id: str, template_data: JournalTemplateUpdate) -> bool:
        update_data = {k: v for k, v in template_data.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        # Only allow users to update their own templates (not default ones)
        return await update_document("journal_templates", {
            "id": template_id, 
            "user_id": user_id,
            "is_default": False
        }, update_data)

    @staticmethod
    async def delete_template(user_id: str, template_id: str) -> bool:
        # Only allow users to delete their own templates (not default ones)
        return await delete_document("journal_templates", {
            "id": template_id, 
            "user_id": user_id,
            "is_default": False
        })

    @staticmethod
    async def initialize_default_templates():
        """Initialize default journal templates - Disabled during Supabase migration"""
        # TODO: Re-enable after fixing foreign key constraints between auth.users and public.users
        logger.info("⚠️ Default journal templates initialization skipped during Supabase migration")
        return
        default_templates = [
            {
                "name": "Daily Reflection",
                "description": "Reflect on your day with guided prompts",
                "template_type": "daily_reflection",
                "prompts": [
                    "What went well today?",
                    "What challenges did you face?",
                    "What did you learn?",
                    "What are you grateful for?",
                    "How do you want to improve tomorrow?"
                ],
                "default_tags": ["daily", "reflection"],
                "icon": "🌅",
                "color": "#F4B400"
            },
            {
                "name": "Gratitude Journal",
                "description": "Practice gratitude with daily appreciation",
                "template_type": "gratitude",
                "prompts": [
                    "What are three things you're grateful for today?",
                    "Who made a positive impact on your day?",
                    "What small moment brought you joy?",
                    "What about yourself are you grateful for?"
                ],
                "default_tags": ["gratitude", "positivity"],
                "icon": "🙏",
                "color": "#10b981"
            },
            {
                "name": "Goal Setting",
                "description": "Plan and track your goals and aspirations",
                "template_type": "goal_setting",
                "prompts": [
                    "What goal do you want to focus on?",
                    "Why is this goal important to you?",
                    "What steps will you take this week?",
                    "What obstacles might you face?",
                    "How will you measure progress?"
                ],
                "default_tags": ["goals", "planning"],
                "icon": "🎯",
                "color": "#8b5cf6"
            },
            {
                "name": "Weekly Review",
                "description": "Comprehensive weekly reflection and planning",
                "template_type": "weekly_review",
                "prompts": [
                    "What were your biggest wins this week?",
                    "What didn't go as planned?",
                    "What patterns do you notice?",
                    "What are your priorities for next week?",
                    "How are you feeling about your progress?"
                ],
                "default_tags": ["weekly", "review", "planning"],
                "icon": "📊",
                "color": "#f59e0b"
            },
            {
                "name": "Learning Log",
                "description": "Document your learning journey and insights",
                "template_type": "learning_log",
                "prompts": [
                    "What new thing did you learn today?",
                    "How will you apply this knowledge?",
                    "What questions do you still have?",
                    "What resources were most helpful?"
                ],
                "default_tags": ["learning", "growth"],
                "icon": "📚",
                "color": "#3b82f6"
            }
        ]
        
        for template_data in default_templates:
            existing = await find_document("journal_templates", {
                "name": template_data["name"],
                "is_default": True
            })
            
            if not existing:
                template = JournalTemplate(
                    user_id="00000000-0000-0000-0000-000000000000",  # System UUID
                    is_default=True,
                    usage_count=0,
                    **template_data
                )
                await create_document("journal_templates", template.dict())

    @staticmethod
    async def fix_existing_journal_entries():
        """Migration function to fix existing journal entries that might be missing template_name field"""
        try:
            # This function is safe to run multiple times
            # It just ensures consistency in the database
            from pymongo import MongoClient
            import os
            
            # Get MongoDB connection details from environment
            mongo_url = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
            
            # This is just a safety check - we don't actually modify anything here
            # The _build_journal_entry_response helper handles the missing field issue
            print("Journal entries migration check completed successfully")
            
        except Exception as e:
            print(f"Journal entries migration check failed: {e}")
            # Don't raise the exception as this is not critical

class ProjectTemplateService:
    @staticmethod
    async def create_template(user_id: str, template_data: ProjectTemplateCreate) -> ProjectTemplate:
        template = ProjectTemplate(user_id=user_id, **template_data.dict(exclude={'tasks'}))
        template_dict = template.dict()
        await create_document("project_templates", template_dict)
        
        # Create task templates
        for i, task_data in enumerate(template_data.tasks):
            task_template = TaskTemplate(
                template_id=template.id,
                user_id=user_id,
                sort_order=i + 1,
                **task_data.dict()
            )
            await create_document("task_templates", task_template.dict())
        
        return template

    @staticmethod
    async def get_user_templates(user_id: str) -> List[ProjectTemplateResponse]:
        templates_docs = await find_documents("project_templates", {"user_id": user_id})
        templates = []
        
        for doc in templates_docs:
            template_response = ProjectTemplateResponse(**doc)
            
            # Get task templates for this template
            task_templates_docs = await find_documents("task_templates", {"template_id": template_response.id})
            task_templates_docs.sort(key=lambda x: x.get("sort_order", 0))
            template_response.tasks = [TaskTemplate(**task_doc) for task_doc in task_templates_docs]
            template_response.task_count = len(task_templates_docs)
            
            templates.append(template_response)
        
        return templates

    @staticmethod
    async def get_template(user_id: str, template_id: str) -> Optional[ProjectTemplateResponse]:
        template_doc = await find_document("project_templates", {"id": template_id, "user_id": user_id})
        if not template_doc:
            return None
            
        template_response = ProjectTemplateResponse(**template_doc)
        
        # Get task templates
        task_templates_docs = await find_documents("task_templates", {"template_id": template_id})
        task_templates_docs.sort(key=lambda x: x.get("sort_order", 0))
        template_response.tasks = [TaskTemplate(**task_doc) for task_doc in task_templates_docs]
        template_response.task_count = len(task_templates_docs)
        
        return template_response

    @staticmethod
    async def update_template(user_id: str, template_id: str, template_data: ProjectTemplateUpdate) -> bool:
        update_data = {k: v for k, v in template_data.dict(exclude={'tasks'}).items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        # Update the template
        success = await update_document("project_templates", {"id": template_id, "user_id": user_id}, update_data)
        
        # Update task templates if provided
        if template_data.tasks is not None:
            # Delete existing task templates
            await delete_document("task_templates", {"template_id": template_id})
            
            # Create new task templates
            for i, task_data in enumerate(template_data.tasks):
                task_template = TaskTemplate(
                    template_id=template_id,
                    user_id=user_id,
                    sort_order=i + 1,
                    **task_data.dict()
                )
                await create_document("task_templates", task_template.dict())
        
        return success

    @staticmethod
    async def delete_template(user_id: str, template_id: str) -> bool:
        # First delete all task templates
        await delete_document("task_templates", {"template_id": template_id})
        
        # Then delete the project template
        return await delete_document("project_templates", {"id": template_id, "user_id": user_id})

    @staticmethod
    async def use_template(user_id: str, template_id: str, project_data: ProjectCreate) -> Project:
        """Create a new project from a template"""
        # Get the template
        template = await ProjectTemplateService.get_template(user_id, template_id)
        if not template:
            raise ValueError("Template not found")
        
        # Create the project
        project = await ProjectService.create_project(user_id, project_data)
        
        # Create tasks from template
        for task_template in template.tasks:
            task_data = TaskCreate(
                name=task_template.name,
                description=task_template.description,
                priority=task_template.priority,
                estimated_duration=task_template.estimated_duration,
                project_id=project.id
            )
            await TaskService.create_task(user_id, task_data)
        
        # Increment usage count
        await update_document(
            "project_templates", 
            {"id": template_id, "user_id": user_id}, 
            {"usage_count": template.usage_count + 1, "updated_at": datetime.utcnow()}
        )
        
        return project


class AreaService:
    @staticmethod
    async def create_area(user_id: str, area_data: AreaCreate) -> Area:
        # Get the current max sort_order
        areas = await find_documents("areas", {"user_id": user_id})
        max_sort_order = max([area.get("sort_order", 0) for area in areas] + [0])
        
        area = Area(user_id=user_id, sort_order=max_sort_order + 1, **area_data.dict())
        area_dict = area.dict()
        await create_document("areas", area_dict)
        return area

    @staticmethod
    async def get_user_areas(user_id: str, include_projects: bool = False, include_archived: bool = False) -> List[AreaResponse]:
        query = {"user_id": user_id}
        if not include_archived:
            query["archived"] = {"$ne": True}
            
        areas_docs = await find_documents("areas", query)
        areas_docs.sort(key=lambda x: x.get("sort_order", 0))
        
        areas = []
        for doc in areas_docs:
            area_response = await AreaService._build_area_response(doc, include_projects)
            areas.append(area_response)
        
        return areas

    @staticmethod
    async def get_area(user_id: str, area_id: str) -> Optional[AreaResponse]:
        area_doc = await find_document("areas", {"id": area_id, "user_id": user_id})
        if not area_doc:
            return None
            
        return await AreaService._build_area_response(area_doc, include_projects=True)

    @staticmethod
    async def update_area(user_id: str, area_id: str, area_data: AreaUpdate) -> bool:
        # Validate pillar_id if being set
        if area_data.pillar_id:
            pillar_doc = await find_document("pillars", {"id": area_data.pillar_id, "user_id": user_id})
            if not pillar_doc:
                raise ValueError("Pillar not found")
        
        update_data = {k: v for k, v in area_data.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        return await update_document("areas", {"id": area_id, "user_id": user_id}, update_data)

    @staticmethod
    async def archive_area(user_id: str, area_id: str) -> bool:
        update_data = {"archived": True, "updated_at": datetime.utcnow()}
        return await update_document("areas", {"id": area_id, "user_id": user_id}, update_data)
    
    @staticmethod
    async def unarchive_area(user_id: str, area_id: str) -> bool:
        update_data = {"archived": False, "updated_at": datetime.utcnow()}
        return await update_document("areas", {"id": area_id, "user_id": user_id}, update_data)

    @staticmethod
    async def _build_area_response(area_doc: dict, include_projects: bool = False) -> AreaResponse:
        """Build area response with pillar name and project data"""
        area_response = AreaResponse(**area_doc)
        
        # Get pillar name if area is linked to a pillar
        if area_response.pillar_id:
            pillar_doc = await find_document("pillars", {"id": area_response.pillar_id})
            if pillar_doc:
                area_response.pillar_name = pillar_doc["name"]
        
        if include_projects:
            # Get projects for this area
            projects = await ProjectService.get_area_projects(area_response.id, include_archived=False)
            area_response.projects = projects
            area_response.project_count = len(projects)
            area_response.completed_project_count = len([p for p in projects if p.status == "Completed"])
            
            # Calculate task counts
            total_tasks = sum([p.task_count or 0 for p in projects])
            completed_tasks = sum([p.completed_task_count or 0 for p in projects])
            area_response.total_task_count = total_tasks
            area_response.completed_task_count = completed_tasks
        else:
            # Just get counts (exclude archived projects unless specifically requested)
            project_query = {"user_id": area_response.user_id, "area_id": area_response.id, "archived": {"$ne": True}}
            projects_docs = await find_documents("projects", project_query)
            area_response.project_count = len(projects_docs)
            area_response.completed_project_count = len([p for p in projects_docs if p.get("status") == "Completed"])
        
        return area_response

    @staticmethod
    async def delete_area(user_id: str, area_id: str) -> bool:
        # First delete all projects (which will delete their tasks)  
        projects = await find_documents("projects", {"user_id": user_id, "area_id": area_id})
        for project in projects:
            await ProjectService.delete_project(user_id, project["id"])
        
        # Then delete the area
        return await delete_document("areas", {"id": area_id, "user_id": user_id})

class ProjectService:
    @staticmethod
    async def create_project(user_id: str, project_data: ProjectCreate) -> Project:
        # Get the current max sort_order for this area
        projects = await find_documents("projects", {"user_id": user_id, "area_id": project_data.area_id})
        max_sort_order = max([project.get("sort_order", 0) for project in projects] + [0])
        
        project = Project(user_id=user_id, sort_order=max_sort_order + 1, **project_data.dict())
        project_dict = project.dict()
        await create_document("projects", project_dict)
        return project

    @staticmethod
    async def get_area_projects(area_id: str, include_archived: bool = False) -> List[ProjectResponse]:
        query = {"area_id": area_id}
        if not include_archived:
            query["archived"] = {"$ne": True}
            
        projects_docs = await find_documents("projects", query)
        projects_docs.sort(key=lambda x: x.get("sort_order", 0))
        
        projects = []
        for doc in projects_docs:
            project = await ProjectService._build_project_response(doc)
            projects.append(project)
        
        return projects

    @staticmethod
    async def get_user_projects(user_id: str, area_id: str = None, include_archived: bool = False) -> List[ProjectResponse]:
        query = {"user_id": user_id}
        if area_id:
            query["area_id"] = area_id
        if not include_archived:
            query["archived"] = {"$ne": True}
            
        projects_docs = await find_documents("projects", query)
        projects_docs.sort(key=lambda x: x.get("sort_order", 0))
        
        projects = []
        for doc in projects_docs:
            project = await ProjectService._build_project_response(doc)
            projects.append(project)
        
        return projects

    @staticmethod
    async def get_project(user_id: str, project_id: str, include_tasks: bool = False) -> Optional[ProjectResponse]:
        project_doc = await find_document("projects", {"id": project_id, "user_id": user_id})
        if not project_doc:
            return None
            
        return await ProjectService._build_project_response(project_doc, include_tasks)

    @staticmethod
    async def _build_project_response(project_doc: dict, include_tasks: bool = False) -> ProjectResponse:
        project_response = ProjectResponse(**project_doc)
        
        # Get task counts - FIXED: Filter by user_id to ensure data consistency
        tasks_docs = await find_documents("tasks", {
            "project_id": project_response.id,
            "user_id": project_doc["user_id"]  # Add user_id filter
        })
        project_response.task_count = len(tasks_docs)
        project_response.completed_task_count = len([t for t in tasks_docs if t.get("completed", False)])
        project_response.active_task_count = len([t for t in tasks_docs if not t.get("completed", False)])
        
        # Calculate completion percentage
        if project_response.task_count > 0:
            project_response.completion_percentage = (project_response.completed_task_count / project_response.task_count) * 100
        
        # Check if overdue
        if project_response.deadline and project_response.status != "Completed":
            project_response.is_overdue = project_response.deadline < datetime.utcnow()
        
        # Get area name
        area_doc = await find_document("areas", {"id": project_response.area_id})
        if area_doc:
            project_response.area_name = area_doc.get("name")
        
        # Include tasks if requested
        if include_tasks:
            tasks = await TaskService.get_project_tasks(project_response.id)
            project_response.tasks = tasks
        
        return project_response

    @staticmethod
    async def update_project(user_id: str, project_id: str, project_data: ProjectUpdate) -> bool:
        update_data = {k: v for k, v in project_data.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        success = await update_document("projects", {"id": project_id, "user_id": user_id}, update_data)
        
        # Check if project was marked as completed and trigger achievement check
        if success and "status" in update_data:
            status_value = update_data["status"].value if hasattr(update_data["status"], 'value') else update_data["status"]
            if status_value == "Completed":
                try:
                    await AchievementService.trigger_project_completed(user_id)
                    # Also trigger custom achievements check
                    await CustomAchievementService.trigger_custom_achievements_check(
                        user_id, "project_completed", project_id
                    )
                except Exception as e:
                    print(f"Warning: Achievement trigger failed for project completion: {e}")
        
        return success

    @staticmethod
    async def archive_project(user_id: str, project_id: str) -> bool:
        """Archive a project"""
        return await update_document(
            "projects", 
            {"id": project_id, "user_id": user_id}, 
            {"archived": True, "updated_at": datetime.utcnow()}
        )
    
    @staticmethod
    async def unarchive_project(user_id: str, project_id: str) -> bool:
        """Unarchive a project"""
        return await update_document(
            "projects", 
            {"id": project_id, "user_id": user_id}, 
            {"archived": False, "updated_at": datetime.utcnow()}
        )

    @staticmethod
    async def delete_project(user_id: str, project_id: str) -> bool:
        # First delete all tasks in this project
        await delete_document("tasks", {"project_id": project_id, "user_id": user_id})
        
        # Then delete the project
        return await delete_document("projects", {"id": project_id, "user_id": user_id})

class RecurringTaskService:
    @staticmethod
    async def create_recurring_task(user_id: str, task_data: RecurringTaskCreate) -> RecurringTaskTemplate:
        """Create a new recurring task template"""
        # Validate project exists
        project = await find_document("projects", {"id": task_data.project_id, "user_id": user_id})
        if not project:
            raise ValueError("Project not found")
        
        # Calculate next due date based on pattern
        next_due = RecurringTaskService._calculate_next_due_date(
            task_data.recurrence_pattern, 
            datetime.now()
        )
        
        template = RecurringTaskTemplate(
            user_id=user_id,
            next_due=next_due,
            **task_data.dict()
        )
        
        await create_document("recurring_task_templates", template.dict())
        return template

    @staticmethod
    async def get_user_recurring_tasks(user_id: str) -> List[RecurringTaskResponse]:
        """Get all recurring task templates for a user"""
        templates_docs = await find_documents("recurring_task_templates", {"user_id": user_id})
        
        responses = []
        for doc in templates_docs:
            template_response = RecurringTaskResponse(**doc)
            
            # Get project name
            if template_response.project_id:
                project = await find_document("projects", {"id": template_response.project_id})
                if project:
                    template_response.project_name = project["name"]
            
            # Calculate statistics
            instances = await find_documents("recurring_task_instances", {
                "template_id": template_response.id
            })
            
            template_response.total_instances = len(instances)
            template_response.completed_instances = len([i for i in instances if i.get("completed")])
            
            if template_response.total_instances > 0:
                template_response.completion_rate = (
                    template_response.completed_instances / template_response.total_instances * 100
                )
            
            responses.append(template_response)
        
        return responses

    @staticmethod
    async def update_recurring_task(user_id: str, template_id: str, task_data: RecurringTaskUpdate) -> bool:
        """Update a recurring task template"""
        update_data = {k: v for k, v in task_data.dict().items() if v is not None}
        
        # If recurrence pattern changed, recalculate next due date
        if "recurrence_pattern" in update_data:
            next_due = RecurringTaskService._calculate_next_due_date(
                update_data["recurrence_pattern"], 
                datetime.now()
            )
            update_data["next_due"] = next_due
        
        update_data["updated_at"] = datetime.utcnow()
        
        return await update_document("recurring_task_templates", {
            "id": template_id, 
            "user_id": user_id
        }, update_data)

    @staticmethod
    async def delete_recurring_task(user_id: str, template_id: str) -> bool:
        """Delete a recurring task template and all its instances"""
        # Delete all instances first
        await delete_document("recurring_task_instances", {"template_id": template_id})
        
        # Delete the template
        return await delete_document("recurring_task_templates", {
            "id": template_id, 
            "user_id": user_id
        })

    @staticmethod
    async def generate_recurring_task_instances():
        """Scheduled job to generate recurring task instances"""
        try:
            now = datetime.now()
            
            # Find templates that need new instances
            templates_docs = await find_documents("recurring_task_templates", {
                "is_active": True,
                "$or": [
                    {"next_due": {"$lte": now}},
                    {"next_due": None}
                ]
            })
            
            for template_doc in templates_docs:
                template = RecurringTaskTemplate(**template_doc)
                
                # Check if we should create instances for this template
                if await RecurringTaskService._should_generate_instances(template, now):
                    instances = await RecurringTaskService._generate_instances_for_template(
                        template, now
                    )
                    
                    # Create the instances
                    for instance in instances:
                        await create_document("recurring_task_instances", instance.dict())
                    
                    # Update template's last_generated and next_due
                    next_due = RecurringTaskService._calculate_next_due_date(
                        template.recurrence_pattern, 
                        now
                    )
                    
                    await update_document("recurring_task_templates", {
                        "id": template.id
                    }, {
                        "last_generated": now,
                        "next_due": next_due
                    })
                    
                    print(f"Generated {len(instances)} instances for template {template.name}")
            
        except Exception as e:
            print(f"Error generating recurring task instances: {e}")

    @staticmethod
    async def _should_generate_instances(template: RecurringTaskTemplate, now: datetime) -> bool:
        """Check if we should generate new instances for a template"""
        if not template.is_active:
            return False
        
        # Check if we've reached max instances
        if template.recurrence_pattern.max_instances:
            existing_count = len(await find_documents("recurring_task_instances", {
                "template_id": template.id
            }))
            if existing_count >= template.recurrence_pattern.max_instances:
                return False
        
        # Check if we've passed end date
        if template.recurrence_pattern.end_date and now > template.recurrence_pattern.end_date:
            return False
        
        return True

    @staticmethod
    async def _generate_instances_for_template(template: RecurringTaskTemplate, now: datetime) -> List[RecurringTaskInstance]:
        """Generate task instances for a template"""
        instances = []
        pattern = template.recurrence_pattern
        
        # Generate instances for the next period (next 30 days max)
        end_date = min(
            now + timedelta(days=30),
            pattern.end_date or now + timedelta(days=365)
        )
        
        current_date = template.next_due or now
        
        while current_date <= end_date:
            # Don't create instances too far in the past
            if current_date >= now - timedelta(days=1):
                instance = RecurringTaskInstance(
                    user_id=template.user_id,
                    template_id=template.id,
                    name=template.name,
                    description=template.description,
                    priority=template.priority,
                    project_id=template.project_id,
                    category=template.category,
                    estimated_duration=template.estimated_duration,
                    due_date=current_date
                )
                instances.append(instance)
            
            # Calculate next occurrence
            current_date = RecurringTaskService._calculate_next_occurrence(
                current_date, pattern
            )
            
            # Prevent infinite loops
            if len(instances) >= 100:
                break
        
        return instances

    @staticmethod
    def _calculate_next_due_date(pattern: RecurrencePattern, from_date: datetime) -> datetime:
        """Calculate the next due date based on recurrence pattern"""
        if pattern.type == RecurrenceEnum.none:
            return from_date
        
        return RecurringTaskService._calculate_next_occurrence(from_date, pattern)

    @staticmethod
    def _calculate_next_occurrence(from_date: datetime, pattern: RecurrencePattern) -> datetime:
        """Calculate next occurrence based on recurrence pattern"""
        if pattern.type == RecurrenceEnum.daily:
            return from_date + timedelta(days=pattern.interval)
        
        elif pattern.type == RecurrenceEnum.weekly:
            if pattern.weekdays:
                # Find next occurrence on specified weekdays
                current_weekday = from_date.weekday()  # 0 = Monday
                target_weekdays = [
                    ["monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday"].index(day.value)
                    for day in pattern.weekdays
                ]
                target_weekdays.sort()
                
                # Find next target weekday
                next_weekday = None
                for weekday in target_weekdays:
                    if weekday > current_weekday:
                        next_weekday = weekday
                        break
                
                if next_weekday is None:
                    # Go to first weekday of next week
                    next_weekday = target_weekdays[0]
                    days_ahead = 7 - current_weekday + next_weekday
                else:
                    days_ahead = next_weekday - current_weekday
                
                return from_date + timedelta(days=days_ahead)
            else:
                return from_date + timedelta(weeks=pattern.interval)
        
        elif pattern.type == RecurrenceEnum.monthly:
            # Add months (approximate - may need adjustment for day overflow)
            next_month = from_date.month + pattern.interval
            next_year = from_date.year + (next_month - 1) // 12
            next_month = ((next_month - 1) % 12) + 1
            
            # Handle day overflow (e.g., Jan 31 -> Feb 28)
            day = pattern.month_day or from_date.day
            try:
                return from_date.replace(year=next_year, month=next_month, day=day)
            except ValueError:
                # Day doesn't exist in target month, use last day of month
                import calendar
                last_day = calendar.monthrange(next_year, next_month)[1]
                return from_date.replace(year=next_year, month=next_month, day=last_day)
        
        # Default fallback
        return from_date + timedelta(days=1)

    @staticmethod
    async def get_recurring_task_instances(user_id: str, template_id: Optional[str] = None, 
                                          start_date: Optional[datetime] = None,
                                          end_date: Optional[datetime] = None) -> List[RecurringTaskInstance]:
        """Get recurring task instances with optional filtering"""
        query = {"user_id": user_id}
        
        if template_id:
            query["template_id"] = template_id
        
        if start_date or end_date:
            date_query = {}
            if start_date:
                date_query["$gte"] = start_date
            if end_date:
                date_query["$lte"] = end_date
            query["due_date"] = date_query
        
        instances_docs = await find_documents("recurring_task_instances", query)
        instances_docs.sort(key=lambda x: x.get("due_date", datetime.min))
        
        return [RecurringTaskInstance(**doc) for doc in instances_docs]

    @staticmethod
    async def complete_recurring_task_instance(user_id: str, instance_id: str) -> bool:
        """Mark a recurring task instance as complete"""
        return await update_document("recurring_task_instances", {
            "id": instance_id,
            "user_id": user_id
        }, {
            "completed": True,
            "completed_at": datetime.utcnow(),
            "status": TaskStatusEnum.completed,
            "kanban_column": "done"
        })

    @staticmethod
    async def skip_recurring_task_instance(user_id: str, instance_id: str) -> bool:
        """Skip a recurring task instance"""
        return await update_document("recurring_task_instances", {
            "id": instance_id,
            "user_id": user_id
        }, {
            "skipped": True,
            "status": TaskStatusEnum.completed  # Consider it done but skipped
        })


class TaskService:
    @staticmethod
    async def create_task(user_id: str, task_data: TaskCreate) -> Task:
        # Validate that the project exists and belongs to the user
        project = await find_document("projects", {"id": task_data.project_id, "user_id": user_id})
        if not project:
            raise ValueError(f"Project with ID {task_data.project_id} not found or does not belong to user")
        
        # Get the current max sort_order for this project
        tasks = await find_documents("tasks", {"user_id": user_id, "project_id": task_data.project_id, "parent_task_id": task_data.parent_task_id})
        max_sort_order = max([task.get("sort_order", 0) for task in tasks] + [0])
        
        task = Task(user_id=user_id, sort_order=max_sort_order + 1, **task_data.dict())
        
        # Set initial kanban column based on status
        if task.status == TaskStatusEnum.in_progress:
            task.kanban_column = "in_progress"
        elif task.status == TaskStatusEnum.review:
            task.kanban_column = "review"
        elif task.status == TaskStatusEnum.completed:
            task.kanban_column = "done"
            task.completed = True
            task.completed_at = datetime.utcnow()
        else:
            task.kanban_column = "to_do"
        
        task_dict = task.dict()
        await create_document("tasks", task_dict)
        
        # Schedule reminders if task has due date
        if task.due_date and not task.completed:
            try:
                # Import here to avoid circular imports
                from notification_service import notification_service
                
                await notification_service.schedule_task_reminders_for_task(
                    user_id=user_id,
                    task_id=task.id,
                    task_name=task.name,
                    due_date=task.due_date,
                    due_time=task.due_time,
                    project_name=project.get("name")
                )
            except Exception as e:
                # Don't fail task creation if notification scheduling fails
                print(f"Warning: Failed to schedule reminders for task {task.id}: {e}")
        
        return task

    @staticmethod
    async def get_project_tasks(project_id: str, include_subtasks: bool = True) -> List[TaskResponse]:
        # Get main tasks (no parent)
        tasks_docs = await find_documents("tasks", {"project_id": project_id, "parent_task_id": None})
        tasks_docs.sort(key=lambda x: x.get("sort_order", 0))
        
        tasks = []
        for doc in tasks_docs:
            task = await TaskService._build_task_response(doc, include_subtasks)
            tasks.append(task)
        
        return tasks

    @staticmethod
    async def get_user_tasks(user_id: str, project_id: str = None) -> List[TaskResponse]:
        query = {"user_id": user_id}
        if project_id:
            query["project_id"] = project_id
            
        tasks_docs = await find_documents("tasks", query)
        tasks = []
        
        for doc in tasks_docs:
            task = await TaskService._build_task_response(doc, include_subtasks=False)
            tasks.append(task)
        
        return tasks

    @staticmethod
    async def get_today_tasks(user_id: str) -> List[TaskResponse]:
        """Get tasks for today's view - due today or overdue"""
        try:
            today = datetime.now().date()
            today_start = datetime.combine(today, datetime.min.time())
            today_end = datetime.combine(today, datetime.max.time())
            
            # Get all tasks for the user (we'll filter on the client side)
            all_tasks = await find_documents("tasks", {"user_id": user_id})
            
            if not all_tasks:
                return []
            
            # Filter tasks on the client side (due today or overdue and not completed)
            filtered_tasks = []
            for task in all_tasks:
                is_completed = task.get("completed", False)
                due_date = task.get("due_date")
                
                # Skip completed tasks
                if is_completed:
                    continue
                    
                # Include if due today or overdue
                if due_date:
                    if isinstance(due_date, str):
                        due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                    
                    if due_date.date() <= today:
                        filtered_tasks.append(task)
                        
            # Sort by priority and due date
            filtered_tasks.sort(key=lambda x: (
                0 if x.get("priority") == "high" else 1 if x.get("priority") == "medium" else 2,
                x.get("due_date") or datetime.max.isoformat()
            ))
            
            # Build task responses
            tasks = []
            for doc in filtered_tasks[:20]:  # Limit to 20 tasks
                task = await TaskService._build_task_response(doc, include_subtasks=False)
                tasks.append(task)
                
            return tasks
            
        except Exception as e:
            logger.error(f"Error getting today tasks: {e}")
            return []
            
            return tasks

    @staticmethod
    async def get_available_tasks_for_today(user_id: str) -> List[TaskResponse]:
        """Get tasks that can be added to today's view (simplified without daily_tasks table)"""
        try:
            # Get all tasks for the user
            all_tasks = await find_documents("tasks", {"user_id": user_id})
            
            if not all_tasks:
                return []
            
            # Filter incomplete tasks on the client side
            incomplete_tasks = []
            for task in all_tasks:
                is_completed = task.get("completed", False)
                if not is_completed:
                    incomplete_tasks.append(task)
            
            # Sort by priority and due date
            incomplete_tasks.sort(key=lambda x: (
                0 if x.get("priority") == "high" else 1 if x.get("priority") == "medium" else 2,
                x.get("due_date") or datetime.max.isoformat()
            ))
            
            # Build task responses (limit to 20)
            tasks = []
            for doc in incomplete_tasks[:20]:
                task = await TaskService._build_task_response(doc, include_subtasks=False)
                tasks.append(task)
            
            return tasks
            
        except Exception as e:
            logger.error(f"Error getting available tasks for today: {e}")
            return []

    @staticmethod
    async def add_task_to_today(user_id: str, task_id: str) -> bool:
        """Add a task to today's curated list (simplified - functionality not available without daily_tasks table)"""
        # This functionality requires the daily_tasks table which wasn't migrated
        logger.warning("Add task to today functionality not available - daily_tasks table missing")
        return False

    @staticmethod
    async def remove_task_from_today(user_id: str, task_id: str) -> bool:
        """Remove a task from today's curated list (simplified - functionality not available without daily_tasks table)"""
        # This functionality requires the daily_tasks table which wasn't migrated
        logger.warning("Remove task from today functionality not available - daily_tasks table missing")
        return False

    @staticmethod
    async def reorder_daily_tasks(user_id: str, task_ids: List[str]) -> bool:
        """Reorder tasks in today's view (simplified - functionality not available without daily_tasks table)"""
        # This functionality requires the daily_tasks table which wasn't migrated
        logger.warning("Reorder daily tasks functionality not available - daily_tasks table missing")
        return False

    @staticmethod
    async def reorder_project_tasks(user_id: str, project_id: str, task_ids: List[str]) -> bool:
        """Reorder tasks within a project"""
        # Verify project exists and belongs to user
        project_doc = await find_document("projects", {"id": project_id, "user_id": user_id})
        if not project_doc:
            raise ValueError("Project not found")
        
        # Verify all tasks exist and belong to the project
        tasks_docs = await find_documents("tasks", {
            "id": {"$in": task_ids},
            "user_id": user_id,
            "project_id": project_id
        })
        
        found_task_ids = [task["id"] for task in tasks_docs]
        missing_task_ids = [task_id for task_id in task_ids if task_id not in found_task_ids]
        
        if missing_task_ids:
            raise ValueError(f"Tasks not found in project: {', '.join(missing_task_ids)}")
        
        # Update sort order for each task
        for i, task_id in enumerate(task_ids):
            await update_document("tasks", {
                "id": task_id,
                "user_id": user_id,
                "project_id": project_id
            }, {
                "sort_order": i + 1,
                "updated_at": datetime.utcnow()
            })
        
        return True

    @staticmethod
    async def _build_task_response(task_doc: dict, include_subtasks: bool = True) -> TaskResponse:
        task_response = TaskResponse(**task_doc)
        
        # Map status to kanban column for consistent kanban view
        status_to_column = {
            "todo": "to_do",
            "in_progress": "in_progress", 
            "review": "review",
            "completed": "done"
        }
        
        # Set kanban_column based on status, fallback to existing kanban_column
        if task_response.status:
            task_response.kanban_column = status_to_column.get(task_response.status.value, task_response.kanban_column or "to_do")
        elif not task_response.kanban_column:
            task_response.kanban_column = "to_do"
        
        # Check if overdue
        if task_response.due_date and not task_response.completed:
            task_response.is_overdue = task_response.due_date < datetime.utcnow()
        
        # Check if task can start (dependencies met)
        if task_response.dependency_task_ids:
            dependency_docs = await find_documents("tasks", {"id": {"$in": task_response.dependency_task_ids}})
            task_response.can_start = all([dep.get("completed", False) for dep in dependency_docs])
            task_response.dependency_tasks = [TaskResponse(**dep) for dep in dependency_docs]
        else:
            task_response.can_start = True
        
        # Get subtasks if requested
        if include_subtasks:
            subtasks_docs = await find_documents("tasks", {"parent_task_id": task_response.id})
            subtasks_docs.sort(key=lambda x: x.get("sort_order", 0))
            task_response.sub_tasks = [await TaskService._build_task_response(sub, False) for sub in subtasks_docs]
        
        return task_response

    @staticmethod
    async def get_task_with_dependencies(user_id: str, task_id: str) -> Optional[TaskResponse]:
        """Get a task with its dependencies populated"""
        return await TaskService.get_task_with_subtasks(user_id, task_id)

    @staticmethod
    async def update_task_dependencies(user_id: str, task_id: str, dependency_ids: List[str]) -> bool:
        """Update the dependency list for a task"""
        # Validate that the task exists
        task_doc = await find_document("tasks", {"id": task_id, "user_id": user_id})
        if not task_doc:
            return False
        
        # Validate that all dependency tasks exist and belong to the user
        if dependency_ids:
            dependency_docs = await find_documents("tasks", {
                "id": {"$in": dependency_ids}, 
                "user_id": user_id
            })
            
            found_ids = [doc["id"] for doc in dependency_docs]
            missing_ids = [dep_id for dep_id in dependency_ids if dep_id not in found_ids]
            
            if missing_ids:
                raise ValueError(f"The following dependency tasks were not found: {', '.join(missing_ids)}")
            
            # Prevent circular dependencies
            if task_id in dependency_ids:
                raise ValueError("A task cannot depend on itself")
        
        # Update the task with new dependencies
        return await update_document("tasks", {"id": task_id, "user_id": user_id}, {
            "dependency_task_ids": dependency_ids,
            "updated_at": datetime.utcnow()
        })

    @staticmethod
    async def get_available_dependency_tasks(user_id: str, project_id: str, exclude_task_id: Optional[str] = None) -> List[dict]:
        """Get tasks that can be used as dependencies for a specific task"""
        query = {
            "user_id": user_id,
            "project_id": project_id,
            "parent_task_id": None  # Only main tasks can be dependencies
        }
        
        # Exclude the current task to prevent self-dependency
        if exclude_task_id:
            query["id"] = {"$ne": exclude_task_id}
        
        tasks_docs = await find_documents("tasks", query)
        
        # Return simplified task data for dependency selection
        return [
            {
                "id": task["id"],
                "name": task["name"],
                "status": task.get("status", "todo"),
                "completed": task.get("completed", False),
                "priority": task.get("priority", "medium")
            }
            for task in tasks_docs
        ]

    @staticmethod
    async def _validate_task_dependencies(current_task: dict, update_data: dict, user_id: str):
        """
        Validate task dependencies before allowing status changes (FR-1.1.2)
        Raises ValueError if dependencies are not met
        """
        dependency_task_ids = current_task.get("dependency_task_ids", [])
        if not dependency_task_ids:
            return  # No dependencies to check
        
        # Check what status/completion we're trying to set
        new_status = None
        new_completed = None
        
        if "status" in update_data:
            status_value = update_data["status"].value if hasattr(update_data["status"], 'value') else update_data["status"]
            new_status = status_value
        
        if "completed" in update_data:
            new_completed = update_data["completed"]
        
        # Only validate if trying to move beyond 'todo' status
        blocked_statuses = ["in_progress", "review", "completed"]
        if new_status in blocked_statuses or new_completed is True:
            # Get dependency tasks to check their completion status
            dependency_docs = await find_documents("tasks", {
                "id": {"$in": dependency_task_ids}, 
                "user_id": user_id
            })
            
            # Check if all dependencies are completed
            incomplete_dependencies = []
            for dep_id in dependency_task_ids:
                dep_task = next((d for d in dependency_docs if d["id"] == dep_id), None)
                if not dep_task:
                    incomplete_dependencies.append(f"Task {dep_id} (not found)")
                elif not dep_task.get("completed", False):
                    incomplete_dependencies.append(dep_task.get("name", f"Task {dep_id}"))
            
            # If there are incomplete dependencies, block the status change (FR-1.1.3)
            if incomplete_dependencies:
                incomplete_list = ", ".join(incomplete_dependencies)
                raise ValueError(f"Cannot update task status. The following prerequisite tasks must be completed first: {incomplete_list}")

    @staticmethod
    async def update_task(user_id: str, task_id: str, task_data: TaskUpdate) -> bool:
        # First, get the current task to check dependencies
        current_task = await find_document("tasks", {"id": task_id, "user_id": user_id})
        if not current_task:
            raise ValueError(f"Task with ID {task_id} not found or does not belong to user")
        
        update_data = {k: v for k, v in task_data.dict().items() if v is not None}
        
        # Validate dependencies before allowing status changes (FR-1.1.2)
        if "status" in update_data or "completed" in update_data:
            await TaskService._validate_task_dependencies(current_task, update_data, user_id)
        
        # Handle status changes
        if "status" in update_data:
            status_to_column = {
                "todo": "to_do",
                "in_progress": "in_progress",
                "review": "review", 
                "completed": "done"
            }
            
            status_value = update_data["status"].value if hasattr(update_data["status"], 'value') else update_data["status"]
            update_data["kanban_column"] = status_to_column.get(status_value, "to_do")
            
            if status_value == "completed":
                update_data["completed"] = True
                update_data["completed_at"] = datetime.utcnow()
                
        # Handle completion toggle
        if "completed" in update_data:
            if update_data["completed"]:
                update_data["completed_at"] = datetime.utcnow()
                update_data["status"] = TaskStatusEnum.completed
                update_data["kanban_column"] = "done"
            else:
                update_data["completed_at"] = None
                update_data["status"] = TaskStatusEnum.todo
                update_data["kanban_column"] = "to_do"
        
        update_data["updated_at"] = datetime.utcnow()
        
        # Update the task
        success = await update_document("tasks", {"id": task_id, "user_id": user_id}, update_data)
        
        if success:
            # Get the updated task to check for parent task completion logic
            updated_task = await find_document("tasks", {"id": task_id, "user_id": user_id})
            if updated_task:
                # Check if task was completed and trigger achievement check
                if update_data.get("completed") or (
                    "status" in update_data and 
                    (update_data["status"] == TaskStatusEnum.completed or 
                     (hasattr(update_data["status"], 'value') and update_data["status"].value == "completed"))
                ):
                    # Trigger achievement check for task completion (performance-optimized)
                    try:
                        await AchievementService.trigger_task_completed(user_id)
                        # Also trigger custom achievements check
                        await CustomAchievementService.trigger_custom_achievements_check(
                            user_id, "task_completed", updated_task.get("project_id")
                        )
                    except Exception as e:
                        print(f"Warning: Achievement trigger failed for task completion: {e}")
                    
                    # Check for tasks that become unblocked due to this completion
                    try:
                        await TaskService._check_and_notify_unblocked_tasks(user_id, task_id)
                    except Exception as e:
                        print(f"Warning: Unblocked task notification failed: {e}")
                
                # If this is a sub-task, check if parent task completion should be updated
                if updated_task.get("parent_task_id"):
                    await TaskService._update_parent_task_completion(updated_task["parent_task_id"], user_id)
                    
                # If this task has sub_task_completion_required and we're marking it complete,
                # check if all sub-tasks are complete first
                if (updated_task.get("sub_task_completion_required") and 
                    update_data.get("completed") and 
                    not await TaskService._all_subtasks_completed(task_id)):
                    # Revert the completion if not all sub-tasks are done
                    await update_document("tasks", {"id": task_id, "user_id": user_id}, {
                        "completed": False,
                        "completed_at": None,
                        "status": TaskStatusEnum.in_progress,
                        "kanban_column": "in_progress"
                    })
                    return False
        
        return success

    @staticmethod
    async def _update_parent_task_completion(parent_task_id: str, user_id: str):
        """Update parent task completion status based on sub-tasks"""
        parent_task = await find_document("tasks", {"id": parent_task_id, "user_id": user_id})
        if not parent_task or not parent_task.get("sub_task_completion_required"):
            return
        
        # Check if all sub-tasks are completed
        all_subtasks_complete = await TaskService._all_subtasks_completed(parent_task_id)
        
        if all_subtasks_complete and not parent_task.get("completed"):
            # Mark parent as complete
            await update_document("tasks", {"id": parent_task_id, "user_id": user_id}, {
                "completed": True,
                "completed_at": datetime.utcnow(),
                "status": TaskStatusEnum.completed,
                "kanban_column": "done",
                "updated_at": datetime.utcnow()
            })
        elif not all_subtasks_complete and parent_task.get("completed"):
            # Mark parent as incomplete
            await update_document("tasks", {"id": parent_task_id, "user_id": user_id}, {
                "completed": False,
                "completed_at": None,
                "status": TaskStatusEnum.in_progress,
                "kanban_column": "in_progress",
                "updated_at": datetime.utcnow()
            })

    @staticmethod
    async def _all_subtasks_completed(parent_task_id: str) -> bool:
        """Check if all sub-tasks of a parent task are completed"""
        subtasks = await find_documents("tasks", {"parent_task_id": parent_task_id})
        if not subtasks:
            return True  # No sub-tasks means parent can be completed
        
        return all(subtask.get("completed", False) for subtask in subtasks)

    @staticmethod
    async def get_task_with_subtasks(user_id: str, task_id: str) -> Optional[TaskResponse]:
        """Get a task with all its sub-tasks"""
        task_doc = await find_document("tasks", {"id": task_id, "user_id": user_id})
        if not task_doc:
            return None
        
        return await TaskService._build_task_response(task_doc, include_subtasks=True)

    @staticmethod
    async def create_subtask(user_id: str, parent_task_id: str, subtask_data: TaskCreate) -> Task:
        """Create a sub-task under a parent task"""
        # Validate that the parent task exists and belongs to the user
        parent_task = await find_document("tasks", {"id": parent_task_id, "user_id": user_id})
        if not parent_task:
            raise ValueError(f"Parent task with ID {parent_task_id} not found or does not belong to user")
        
        # Set the parent_task_id and inherit project_id from parent
        subtask_data.parent_task_id = parent_task_id
        subtask_data.project_id = parent_task["project_id"]
        
        # Create the sub-task
        return await TaskService.create_task(user_id, subtask_data)

    @staticmethod
    async def delete_task(user_id: str, task_id: str) -> bool:
        # First delete all subtasks
        await delete_document("tasks", {"parent_task_id": task_id, "user_id": user_id})
        
        # Then delete the task
        return await delete_document("tasks", {"id": task_id, "user_id": user_id})

    @staticmethod
    async def _check_and_notify_unblocked_tasks(user_id: str, completed_task_id: str):
        """Check for tasks that are now unblocked due to the completion of a dependency task and send notifications"""
        try:
            # Find all tasks that have the completed task as a dependency
            dependent_tasks = await find_documents("tasks", {
                "user_id": user_id,
                "dependency_task_ids": completed_task_id,
                "completed": False  # Only consider incomplete tasks
            })
            
            if not dependent_tasks:
                return  # No dependent tasks found
            
            # For each dependent task, check if all its dependencies are now complete
            for dependent_task in dependent_tasks:
                all_dependencies_complete = True
                dependency_task_ids = dependent_task.get("dependency_task_ids", [])
                
                if dependency_task_ids:
                    # Check if all dependency tasks are completed
                    for dep_task_id in dependency_task_ids:
                        dep_task = await find_document("tasks", {
                            "id": dep_task_id, 
                            "user_id": user_id
                        })
                        if not dep_task or not dep_task.get("completed", False):
                            all_dependencies_complete = False
                            break
                
                # If all dependencies are complete, send unblocked notification
                if all_dependencies_complete:
                    # Get project name for context
                    project_doc = await find_document("projects", {
                        "id": dependent_task.get("project_id"),
                        "user_id": user_id
                    })
                    project_name = project_doc.get("name", "Unknown Project") if project_doc else "Unknown Project"
                    
                    # Get the completed task name
                    completed_task_doc = await find_document("tasks", {
                        "id": completed_task_id,
                        "user_id": user_id
                    })
                    completed_task_name = completed_task_doc.get("name", "Unknown Task") if completed_task_doc else "Unknown Task"
                    
                    # Create notification
                    from notification_service import notification_service
                    await notification_service.create_notification({
                        "user_id": user_id,
                        "type": NotificationTypeEnum.unblocked_task,
                        "title": "✅ Task Unblocked",
                        "message": f"'{completed_task_name}' is complete. You can now begin '{dependent_task.get('name', 'Unknown Task')}'.",
                        "related_task_id": dependent_task.get("id"),
                        "related_project_id": dependent_task.get("project_id"),
                        "project_name": project_name,
                        "priority": dependent_task.get("priority", "medium"),
                        "created_at": datetime.utcnow(),
                        "is_read": False,
                        "channels": ["browser"]  # Default to browser notifications
                    })
                    
        except Exception as e:
            print(f"Error in _check_and_notify_unblocked_tasks: {e}")

    @staticmethod
    async def get_kanban_board(user_id: str, project_id: str) -> KanbanBoard:
        project_doc = await find_document("projects", {"id": project_id, "user_id": user_id})
        if not project_doc:
            raise ValueError("Project not found")
        
        tasks_docs = await find_documents("tasks", {"project_id": project_id, "parent_task_id": None})
        
        columns = {
            "to_do": [],
            "in_progress": [],
            "review": [],
            "done": []
        }
        
        for doc in tasks_docs:
            task = await TaskService._build_task_response(doc, include_subtasks=True)
            column = task.kanban_column or "to_do"
            if column in columns:
                columns[column].append(task)
        
        # Sort each column by sort_order
        for column in columns.values():
            column.sort(key=lambda x: x.sort_order)
        
        return KanbanBoard(
            project_id=project_id,
            project_name=project_doc.get("name", ""),
            columns=columns
        )

    @staticmethod
    async def move_task_column(user_id: str, task_id: str, new_column: str) -> bool:
        """Move task between kanban columns"""
        valid_columns = ["to_do", "in_progress", "review", "done"]
        if new_column not in valid_columns:
            return False
        
        update_data = {"kanban_column": new_column, "updated_at": datetime.utcnow()}
        
        # Update status based on column
        if new_column == "done":
            update_data["status"] = TaskStatusEnum.completed
            update_data["completed"] = True
            update_data["completed_at"] = datetime.utcnow()
        elif new_column == "in_progress":
            update_data["status"] = TaskStatusEnum.in_progress
            update_data["completed"] = False
            update_data["completed_at"] = None
        else:  # to_do
            update_data["status"] = TaskStatusEnum.not_started
            update_data["completed"] = False
            update_data["completed_at"] = None
        
        return await update_document("tasks", {"id": task_id, "user_id": user_id}, update_data)


class ChatService:
    @staticmethod
    async def create_message(user_id: str, message_data: ChatMessageCreate) -> ChatMessage:
        message = ChatMessage(user_id=user_id, **message_data.dict())
        message_dict = message.dict()
        await create_document("chat_messages", message_dict)
        return message

    @staticmethod
    async def get_session_messages(user_id: str, session_id: str) -> List[ChatMessage]:
        messages_docs = await find_documents(
            "chat_messages", 
            {"user_id": user_id, "session_id": session_id}
        )
        # Sort by timestamp ascending
        messages_docs.sort(key=lambda x: x.get("timestamp", ""))
        return [ChatMessage(**doc) for doc in messages_docs]

    @staticmethod
    async def generate_ai_response(user_message: str) -> str:
        """Simple AI response generator - can be enhanced with real LLM integration"""
        responses = [
            "That's a great insight! Building self-awareness is the first step toward meaningful change. Have you considered setting specific daily practices to reinforce this?",
            "I understand your perspective. It's normal to feel overwhelmed sometimes. Let's break this down into smaller, manageable steps.",
            "Your commitment to growth is inspiring! Based on what you've shared, I'd recommend focusing on consistency rather than perfection.",
            "That's a common challenge many people face. What if we explored some mindfulness techniques that could help you navigate these situations?",
            "I can sense you're making real progress. Remember, growth isn't always linear - every step forward counts, even the small ones.",
            "Your reflection shows deep self-awareness. How do you think you could apply this insight to other areas of your life?",
            "That's a wonderful goal! Let's create a specific action plan that aligns with your values and current habits.",
            "I appreciate your honesty. Vulnerability is actually a strength and shows you're ready for genuine growth."
        ]
        import random
        return random.choice(responses)

class CourseService:
    @staticmethod
    async def get_all_courses() -> List[CourseResponse]:
        courses_docs = await find_documents("courses", {})
        return [CourseResponse(**doc) for doc in courses_docs]

    @staticmethod
    async def get_user_courses(user_id: str) -> List[CourseResponse]:
        # Get user's enrolled courses with progress
        pipeline = [
            {"$match": {"user_id": user_id}},
            {"$lookup": {
                "from": "courses",
                "localField": "course_id",
                "foreignField": "id",
                "as": "course"
            }},
            {"$unwind": "$course"},
            {"$project": {
                "course_id": 1,
                "progress_percentage": 1,
                "course.title": 1,
                "course.description": 1,
                "course.instructor": 1,
                "course.duration": 1,
                "course.category": 1,
                "course.image_url": 1
            }}
        ]
        
        progress_docs = await aggregate_documents("user_course_progress", pipeline)
        courses = []
        
        for doc in progress_docs:
            course_data = doc["course"]
            course_data["progress_percentage"] = doc["progress_percentage"]
            course_data["is_enrolled"] = True
            courses.append(CourseResponse(**course_data))
        
        return courses

    @staticmethod
    async def enroll_user(user_id: str, course_id: str) -> UserCourseProgress:
        # Check if already enrolled
        existing = await find_document("user_course_progress", {"user_id": user_id, "course_id": course_id})
        if existing:
            return UserCourseProgress(**existing)
        
        enrollment = UserCourseProgress(user_id=user_id, course_id=course_id)
        enrollment_dict = enrollment.dict()
        await create_document("user_course_progress", enrollment_dict)
        return enrollment

class InsightsService:
    @staticmethod
    async def get_insights_data(user_id: str, date_range: str = "all_time") -> dict:
        """Get comprehensive insights data for the user"""
        
        # Get basic stats
        stats = await StatsService.get_user_stats(user_id)
        
        # Get areas with project data for insights
        areas = await AreaService.get_user_areas(user_id, include_projects=True)
        
        # Calculate task status breakdown
        task_status_breakdown = {
            "completed": 0,
            "in_progress": 0,
            "todo": 0,
            "overdue": 0
        }
        
        # Get all tasks to calculate status breakdown
        from database import find_documents
        all_tasks = await find_documents("tasks", {"user_id": user_id})
        
        for task_doc in all_tasks:
            status = task_doc.get("status", "todo")
            if status == "completed":
                task_status_breakdown["completed"] += 1
            elif status == "in_progress":
                task_status_breakdown["in_progress"] += 1
            elif status == "review":
                # Map 'review' to 'in_progress' for frontend compatibility
                task_status_breakdown["in_progress"] += 1
            else:  # todo and any other status
                task_status_breakdown["todo"] += 1
            
            # Check for overdue tasks (simplified logic)
            due_date = task_doc.get("due_date")
            if due_date and not task_doc.get("completed", False):
                from datetime import datetime
                try:
                    if isinstance(due_date, str):
                        due_date = datetime.fromisoformat(due_date.replace('Z', '+00:00'))
                    if due_date < datetime.utcnow():
                        task_status_breakdown["overdue"] += 1
                        # Remove from other categories to avoid double counting
                        if status == "completed":
                            task_status_breakdown["completed"] -= 1
                        elif status in ["in_progress", "review"]:
                            task_status_breakdown["in_progress"] -= 1
                        else:
                            task_status_breakdown["todo"] -= 1
                except:
                    pass  # Skip invalid dates
        
        # Build insights payload
        insights = {
            "overview": {
                "total_areas": stats.total_areas,
                "total_projects": stats.total_projects,
                "completed_projects": stats.completed_projects,
                "total_tasks": stats.total_tasks,
                "completed_tasks": stats.tasks_completed,
                "completion_rate": (stats.tasks_completed / stats.total_tasks * 100) if stats.total_tasks > 0 else 0
            },
            "overall_stats": {
                "total_tasks": stats.total_tasks,
                "completed_tasks": stats.tasks_completed,
                "in_progress_tasks": task_status_breakdown["in_progress"],
                "todo_tasks": task_status_breakdown["todo"],
                "overdue_tasks": task_status_breakdown["overdue"],
                "completion_rate": (stats.tasks_completed / stats.total_tasks * 100) if stats.total_tasks > 0 else 0
            },
            "task_status_breakdown": task_status_breakdown,
            "areas": []
        }
        
        # Add area-level insights
        for area in areas:
            area_insight = {
                "id": area.id,
                "name": area.name,
                "color": area.color,
                "icon": area.icon,
                "project_count": area.project_count,
                "completed_project_count": area.completed_project_count,
                "total_task_count": area.total_task_count,
                "completed_task_count": area.completed_task_count,
                "completion_rate": (area.completed_task_count / area.total_task_count * 100) if area.total_task_count > 0 else 0,
                "projects": [],
                # Add compatibility fields for frontend
                "total_tasks": area.total_task_count,
                "completed_tasks": area.completed_task_count
            }
            
            # Add project-level data if available
            if area.projects:
                for project in area.projects:
                    project_insight = {
                        "id": project.id,
                        "name": project.name,
                        "status": project.status,
                        "priority": project.priority,
                        "task_count": project.task_count or 0,
                        "completed_task_count": project.completed_task_count or 0,
                        "completion_percentage": project.completion_percentage or 0
                    }
                    area_insight["projects"].append(project_insight)
            
            insights["areas"].append(area_insight)
        
        return insights
    
    @staticmethod
    async def get_area_drill_down(user_id: str, area_id: str, date_range: str = "all_time") -> dict:
        """Get detailed breakdown for a specific area"""
        
        # Get the area with projects
        area = await AreaService.get_area(user_id, area_id)
        if not area:
            raise ValueError("Area not found")
        
        # Build drill-down data
        drill_down = {
            "area": {
                "id": area.id,
                "name": area.name,
                "description": area.description,
                "color": area.color,
                "icon": area.icon
            },
            "summary": {
                "project_count": area.project_count,
                "completed_project_count": area.completed_project_count,
                "total_task_count": area.total_task_count,
                "completed_task_count": area.completed_task_count,
                "completion_rate": (area.completed_task_count / area.total_task_count * 100) if area.total_task_count > 0 else 0
            },
            "projects": []
        }
        
        # Add detailed project information
        if area.projects:
            for project in area.projects:
                project_detail = {
                    "id": project.id,
                    "name": project.name,
                    "description": project.description,
                    "status": project.status,
                    "priority": project.priority,
                    "deadline": project.deadline.isoformat() if project.deadline else None,
                    "task_count": project.task_count or 0,
                    "completed_task_count": project.completed_task_count or 0,
                    "active_task_count": project.active_task_count or 0,
                    "completion_percentage": project.completion_percentage or 0,
                    "created_at": project.created_at.isoformat()
                }
                drill_down["projects"].append(project_detail)
        
        return drill_down
    
    @staticmethod
    async def get_project_drill_down(user_id: str, project_id: str, date_range: str = "all_time") -> dict:
        """Get detailed task breakdown for a specific project"""
        
        # Get the project
        project = await ProjectService.get_project(user_id, project_id, include_tasks=True)
        if not project:
            raise ValueError("Project not found")
        
        # Get area information
        area = await AreaService.get_area(user_id, project.area_id) if project.area_id else None
        
        # Build drill-down data
        drill_down = {
            "project": {
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "status": project.status,
                "priority": project.priority,
                "deadline": project.deadline.isoformat() if project.deadline else None,
                "area_name": area.name if area else None
            },
            "summary": {
                "task_count": project.task_count or 0,
                "completed_task_count": project.completed_task_count or 0,
                "active_task_count": project.active_task_count or 0,
                "completion_percentage": project.completion_percentage or 0
            },
            "tasks": []
        }
        
        # Add detailed task information
        if project.tasks:
            for task in project.tasks:
                task_detail = {
                    "id": task.id,
                    "name": task.name,
                    "description": task.description,
                    "status": task.status,
                    "priority": task.priority,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "due_time": task.due_time,
                    "completed": task.completed,
                    "completed_at": task.completed_at.isoformat() if task.completed_at else None,
                    "is_overdue": task.is_overdue,
                    "created_at": task.created_at.isoformat()
                }
                drill_down["tasks"].append(task_detail)
        
        return drill_down

class PillarService:
    @staticmethod
    async def create_pillar(user_id: str, pillar_data: PillarCreate) -> Pillar:
        """Create a new pillar"""
        # Get current max sort_order for user's pillars
        pillars = await find_documents("pillars", {"user_id": user_id})
        max_sort_order = max([pillar.get("sort_order", 0) for pillar in pillars] + [0])
        
        pillar = Pillar(
            user_id=user_id, 
            sort_order=max_sort_order + 1, 
            **pillar_data.dict()
        )
        pillar_dict = pillar.dict()
        await create_document("pillars", pillar_dict)
        return pillar
    
    @staticmethod
    async def get_user_pillars(user_id: str, include_areas: bool = False, include_archived: bool = False) -> List[PillarResponse]:
        """Get all pillars for a user"""
        query = {"user_id": user_id}
        if not include_archived:
            query["archived"] = {"$ne": True}
        
        pillars_docs = await find_documents("pillars", query)
        pillars_docs.sort(key=lambda x: x.get("sort_order", 0))
        
        pillars = []
        for doc in pillars_docs:
            pillar_response = await PillarService._build_pillar_response(doc, include_areas)
            pillars.append(pillar_response)
        
        return pillars
    
    @staticmethod
    async def get_pillar(user_id: str, pillar_id: str, include_areas: bool = False) -> Optional[PillarResponse]:
        """Get a specific pillar by ID"""
        pillar_doc = await find_document("pillars", {"id": pillar_id, "user_id": user_id})
        if not pillar_doc:
            return None
        
        return await PillarService._build_pillar_response(pillar_doc, include_areas)
    
    @staticmethod
    async def update_pillar(user_id: str, pillar_id: str, pillar_data: PillarUpdate) -> bool:
        """Update a pillar"""        
        update_data = {k: v for k, v in pillar_data.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        return await update_document("pillars", {"id": pillar_id, "user_id": user_id}, update_data)
    
    @staticmethod
    async def archive_pillar(user_id: str, pillar_id: str) -> bool:
        """Archive a pillar (and optionally its sub-pillars)"""
        update_data = {"archived": True, "updated_at": datetime.utcnow()}
        return await update_document("pillars", {"id": pillar_id, "user_id": user_id}, update_data)
    
    @staticmethod
    async def unarchive_pillar(user_id: str, pillar_id: str) -> bool:
        """Unarchive a pillar"""
        update_data = {"archived": False, "updated_at": datetime.utcnow()}
        return await update_document("pillars", {"id": pillar_id, "user_id": user_id}, update_data)
    
    @staticmethod
    async def delete_pillar(user_id: str, pillar_id: str) -> bool:
        """Delete a pillar and unlink associated areas"""
        # First, unlink all areas from this pillar
        await update_document("areas", {"pillar_id": pillar_id, "user_id": user_id}, {"pillar_id": None})
        
        # Delete the pillar itself
        return await delete_document("pillars", {"id": pillar_id, "user_id": user_id})
    
    @staticmethod
    async def _build_pillar_response(pillar_doc: dict, include_areas: bool = False) -> PillarResponse:
        """Build a comprehensive pillar response with progress data"""
        pillar_response = PillarResponse(**pillar_doc)
        
        # Get linked areas and calculate progress
        areas_docs = await find_documents("areas", {
            "pillar_id": pillar_response.id,
            "user_id": pillar_response.user_id,
            "archived": {"$ne": True}
        })
        
        pillar_response.area_count = len(areas_docs)
        
        # Calculate project and task statistics
        total_projects = 0
        total_tasks = 0
        completed_tasks = 0
        
        areas = []
        for area_doc in areas_docs:
            area_response = await AreaService._build_area_response(area_doc, include_projects=True)
            areas.append(area_response)
            
            total_projects += area_response.project_count
            total_tasks += area_response.total_task_count
            completed_tasks += area_response.completed_task_count
        
        pillar_response.project_count = total_projects
        pillar_response.task_count = total_tasks
        pillar_response.completed_task_count = completed_tasks
        pillar_response.progress_percentage = (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
        
        # Include areas if requested
        if include_areas:
            pillar_response.areas = areas
        
        return pillar_response

class StatsService:
    @staticmethod
    async def get_user_stats(user_id: str) -> UserStats:
        stats_doc = await find_document("user_stats", {"user_id": user_id})
        if not stats_doc:
            # Create default stats
            stats = UserStats(user_id=user_id)
            await create_document("user_stats", stats.dict())
            return stats
        return UserStats(**stats_doc)

    @staticmethod
    async def update_user_stats(user_id: str) -> UserStats:
        """Recalculate and update user statistics"""
        try:
            # Get current counts (removed habits references)
            total_journal_entries = await count_documents("journal_entries", {"user_id": user_id})
            
            # Updated task counts to work with projects
            total_tasks = await count_documents("tasks", {"user_id": user_id})
            tasks_completed = await count_documents("tasks", {"user_id": user_id, "completed": True})
            
            # New counts for areas and projects
            total_areas = await count_documents("areas", {"user_id": user_id})
            total_projects = await count_documents("projects", {"user_id": user_id})
            completed_projects = await count_documents("projects", {"user_id": user_id, "status": "Completed"})
            
            # Only query tables that exist (courses and badges may not exist)
            courses_enrolled = 0
            courses_completed = 0 
            badges_earned = 0
            
            try:
                courses_enrolled = await count_documents("user_course_progress", {"user_id": user_id})
                courses_completed = await count_documents("user_course_progress", {"user_id": user_id, "progress_percentage": 100})
            except Exception:
                # Course tables don't exist - ignore
                pass
                
            try:
                badges_earned = await count_documents("user_badges", {"user_id": user_id, "earned": True})
            except Exception:
                # Badge tables don't exist - ignore 
                pass
            
            # Calculate current streak (use journal streak instead of habits)
            current_streak = 0
            try:
                current_streak = await JournalService._calculate_journal_streak(user_id)
            except Exception:
                # Journal streak calculation failed - use 0
                pass
            
            stats_data = {
                "user_id": user_id,
                "total_journal_entries": total_journal_entries,
                "total_tasks": total_tasks,
                "tasks_completed": tasks_completed,
                "total_areas": total_areas,
                "total_projects": total_projects,
                "completed_projects": completed_projects,
                "courses_enrolled": courses_enrolled,
                "courses_completed": courses_completed,
                "badges_earned": badges_earned
            }
            
            # Update or create stats
            existing_stats = await find_document("user_stats", {"user_id": user_id})
            if existing_stats:
                await update_document("user_stats", {"user_id": user_id}, stats_data)
            else:
                stats = UserStats(**stats_data)
                await create_document("user_stats", stats.dict())
            
            # Update user's current streak and total points (removed habits from calculation)
            total_points = (tasks_completed * 15) + (badges_earned * 50) + (courses_completed * 100) + (completed_projects * 25)
            await update_document("users", {"id": user_id}, {
                "current_streak": current_streak,
                "total_points": total_points,
                "updated_at": datetime.utcnow()
            })
            
            return UserStats(**stats_data)
            
        except Exception as e:
            logger.error(f"Error updating user stats: {e}")
            # Return default stats if everything fails
            default_stats = UserStats(user_id=user_id)
            return default_stats

    @staticmethod
    async def get_dashboard_data(user_id: str) -> UserDashboard:
        """Get all dashboard data for a user"""
        try:
            # Update stats first
            stats = await StatsService.update_user_stats(user_id)
            
            # Get user data
            user = await UserService.get_user(user_id)
            if not user:
                raise ValueError("User not found")
            
            # Get recent data (handle missing services)
            recent_tasks = await TaskService.get_user_tasks(user_id)
            today_tasks = await TaskService.get_today_tasks(user_id)
            
            # Get courses if available, otherwise empty list
            recent_courses = []
            try:
                recent_courses = await CourseService.get_user_courses(user_id)
            except Exception as e:
                logger.warning(f"Course service not available: {e}")
            
            # Get areas with projects
            areas = await AreaService.get_user_areas(user_id, include_projects=True)
            
            # Get badges (placeholder for now)
            recent_achievements = []
            
            return UserDashboard(
                user=user,
                stats=stats,
                recent_tasks=recent_tasks[:5] if recent_tasks else [],
                recent_courses=recent_courses[:3] if recent_courses else [],
                recent_achievements=recent_achievements,
                areas=areas if areas else [],
                today_tasks=today_tasks if today_tasks else []
            )
            
        except Exception as e:
            logger.error(f"Error getting dashboard data: {e}")
            raise

    @staticmethod
    async def get_today_view(user_id: str) -> TodayView:
        """Get today's focused view with curated tasks"""
        today_tasks = await TaskService.get_today_tasks(user_id)
        available_tasks = await TaskService.get_available_tasks_for_today(user_id)
        
        # Calculate totals
        total_tasks = len(today_tasks)
        completed_tasks = len([t for t in today_tasks if t.completed])
        estimated_duration = sum([t.estimated_duration or 0 for t in today_tasks])
        
        return TodayView(
            date=datetime.now(),
            tasks=today_tasks,
            available_tasks=available_tasks,
            total_tasks=total_tasks,
            completed_tasks=completed_tasks,
            estimated_duration=estimated_duration,
            pomodoro_sessions=0  # TODO: Implement pomodoro session tracking
        )

class AchievementService:
    """Service for handling dynamic achievement tracking and unlocking"""
    
    @staticmethod
    async def get_user_achievements(user_id: str) -> List[Dict]:
        """Get all achievements for a user with progress"""
        # Get all available badges
        badges_docs = await find_documents("badges", {})
        
        # Get user's badge progress
        user_badges_docs = await find_documents("user_badges", {"user_id": user_id})
        user_badges_map = {ub["badge_id"]: ub for ub in user_badges_docs}
        
        achievements = []
        for badge_doc in badges_docs:
            badge = Badge(**badge_doc)
            user_badge = user_badges_map.get(badge.id)
            
            # Calculate current progress
            progress = await AchievementService._calculate_achievement_progress(
                user_id, badge.category, badge.requirements
            )
            
            achievement = {
                "id": badge.id,
                "name": badge.name,
                "description": badge.description,
                "icon": badge.icon,
                "rarity": badge.rarity,
                "category": badge.category,
                "requirements": badge.requirements,
                "earned": user_badge.get("earned", False) if user_badge else False,
                "earned_date": user_badge.get("earned_date") if user_badge else None,
                "progress": min(progress, 100)  # Cap at 100%
            }
            achievements.append(achievement)
        
        return achievements
    
    @staticmethod
    async def _calculate_achievement_progress(user_id: str, category: str, requirements: Dict) -> int:
        """Calculate progress towards an achievement based on requirements"""
        try:
            # Get user stats for calculations
            stats_doc = await find_document("user_stats", {"user_id": user_id})
            if not stats_doc:
                return 0
            
            stats = UserStats(**stats_doc)
            
            # Handle different requirement types
            for req_key, req_value in requirements.items():
                if req_key == "tasks_completed":
                    return min(int((stats.tasks_completed / req_value) * 100), 100)
                
                elif req_key == "journal_entries":
                    return min(int((stats.total_journal_entries / req_value) * 100), 100)
                
                elif req_key == "courses_completed":
                    return min(int((stats.courses_completed / req_value) * 100), 100)
                
                elif req_key == "projects_completed":
                    return min(int((stats.completed_projects / req_value) * 100), 100)
                
                elif req_key == "login_streak":
                    # For login streak, check user's current streak
                    user_doc = await find_document("users", {"id": user_id})
                    if user_doc:
                        current_streak = user_doc.get("current_streak", 0)
                        return min(int((current_streak / req_value) * 100), 100)
                
                elif req_key == "habit_streak":
                    # Calculate based on current streak (simplified for now)
                    user_doc = await find_document("users", {"id": user_id})
                    if user_doc:
                        current_streak = user_doc.get("current_streak", 0)
                        return min(int((current_streak / req_value) * 100), 100)
                
                elif req_key == "meditation_sessions":
                    # For meditation, use a simplified calculation
                    return min(int((stats.total_journal_entries / req_value) * 50), 100)  # Simplified
            
            return 0
            
        except Exception as e:
            print(f"Error calculating achievement progress: {e}")
            return 0
    
    @staticmethod
    async def check_and_unlock_achievements(user_id: str, trigger_action: str = None):
        """Check if user has unlocked any new achievements and unlock them"""
        try:
            # Get all badges that user hasn't earned yet
            earned_badge_ids = []
            user_badges_docs = await find_documents("user_badges", {"user_id": user_id, "earned": True})
            earned_badge_ids = [ub["badge_id"] for ub in user_badges_docs]
            
            # Get unearned badges
            badges_docs = await find_documents("badges", {"id": {"$nin": earned_badge_ids}})
            
            newly_unlocked = []
            
            for badge_doc in badges_docs:
                badge = Badge(**badge_doc)
                
                # Check if user meets requirements
                if await AchievementService._check_achievement_requirements(user_id, badge.requirements):
                    # Unlock the achievement
                    await AchievementService._unlock_achievement(user_id, badge.id)
                    newly_unlocked.append(badge)
                    
                    # Create notification for achievement unlock
                    await AchievementService._create_achievement_notification(user_id, badge)
            
            return newly_unlocked
            
        except Exception as e:
            print(f"Error checking achievements: {e}")
            return []
    
    @staticmethod
    async def _check_achievement_requirements(user_id: str, requirements: Dict) -> bool:
        """Check if user meets the requirements for an achievement"""
        try:
            # Get user stats
            stats_doc = await find_document("user_stats", {"user_id": user_id})
            if not stats_doc:
                return False
            
            stats = UserStats(**stats_doc)
            
            # Check each requirement
            for req_key, req_value in requirements.items():
                if req_key == "tasks_completed":
                    if stats.tasks_completed < req_value:
                        return False
                
                elif req_key == "journal_entries":
                    if stats.total_journal_entries < req_value:
                        return False
                
                elif req_key == "courses_completed":
                    if stats.courses_completed < req_value:
                        return False
                
                elif req_key == "projects_completed":
                    if stats.completed_projects < req_value:
                        return False
                
                elif req_key == "login_streak":
                    user_doc = await find_document("users", {"id": user_id})
                    if not user_doc or user_doc.get("current_streak", 0) < req_value:
                        return False
                
                elif req_key == "habit_streak":
                    user_doc = await find_document("users", {"id": user_id})
                    if not user_doc or user_doc.get("current_streak", 0) < req_value:
                        return False
                
                elif req_key == "meditation_sessions":
                    # Simplified check for meditation sessions
                    if stats.total_journal_entries < req_value / 2:  # Simplified calculation
                        return False
            
            return True
            
        except Exception as e:
            print(f"Error checking achievement requirements: {e}")
            return False
    
    @staticmethod
    async def _unlock_achievement(user_id: str, badge_id: str):
        """Unlock an achievement for a user"""
        try:
            # Check if user badge already exists
            existing_badge = await find_document("user_badges", {
                "user_id": user_id,
                "badge_id": badge_id
            })
            
            if existing_badge:
                # Update existing badge to earned
                await update_document("user_badges", {
                    "user_id": user_id,
                    "badge_id": badge_id
                }, {
                    "earned": True,
                    "earned_date": datetime.utcnow()
                })
            else:
                # Create new user badge
                user_badge = UserBadge(
                    user_id=user_id,
                    badge_id=badge_id,
                    earned=True,
                    earned_date=datetime.utcnow()
                )
                await create_document("user_badges", user_badge.dict())
            
            # Update user stats
            await atomic_update_document("user_stats", {"user_id": user_id}, {
                "$inc": {"badges_earned": 1}
            })
            
            print(f"✅ Achievement unlocked for user {user_id}: {badge_id}")
            
        except Exception as e:
            print(f"Error unlocking achievement: {e}")
    
    @staticmethod
    async def _create_achievement_notification(user_id: str, badge: Badge):
        """Create a notification for achievement unlock"""
        try:
            # Import here to avoid circular imports
            from notification_service import notification_service
            
            notification_data = {
                "user_id": user_id,
                "type": "achievement_unlocked",
                "title": f"🎉 Achievement Unlocked!",
                "message": f"Congratulations! You've earned the '{badge.name}' badge: {badge.description}",
                "data": {
                    "badge_id": badge.id,
                    "badge_name": badge.name,
                    "badge_icon": badge.icon,
                    "badge_rarity": badge.rarity
                }
            }
            
            # Create browser notification
            await notification_service.create_notification(notification_data)
            
        except Exception as e:
            print(f"Error creating achievement notification: {e}")
    
    # PERFORMANCE-OPTIMIZED TRIGGER FUNCTIONS
    # These are called from other services when relevant actions occur
    
    @staticmethod
    async def trigger_task_completed(user_id: str):
        """Efficient trigger when a task is completed"""
        try:
            # Only check task-related achievements to minimize database calls
            task_badges = await find_documents("badges", {
                "$or": [
                    {"requirements.tasks_completed": {"$exists": True}},
                    {"category": "productivity"}
                ]
            })
            
            # Get current user stats to check thresholds
            stats_doc = await find_document("user_stats", {"user_id": user_id})
            if not stats_doc:
                return
            
            stats = UserStats(**stats_doc)
            
            # Check only relevant badges that might be close to unlocking
            for badge_doc in task_badges:
                badge = Badge(**badge_doc)
                
                # Skip already earned badges
                existing_badge = await find_document("user_badges", {
                    "user_id": user_id,
                    "badge_id": badge.id,
                    "earned": True
                })
                if existing_badge:
                    continue
                
                # Check if this completion might unlock the badge
                req_value = badge.requirements.get("tasks_completed")
                if req_value and stats.tasks_completed >= req_value:
                    await AchievementService._unlock_achievement(user_id, badge.id)
                    await AchievementService._create_achievement_notification(user_id, badge)
            
        except Exception as e:
            print(f"Error in task completion trigger: {e}")
    
    @staticmethod
    async def trigger_project_completed(user_id: str):
        """Efficient trigger when a project is completed"""
        try:
            project_badges = await find_documents("badges", {
                "$or": [
                    {"requirements.projects_completed": {"$exists": True}},
                    {"category": "productivity"}
                ]
            })
            
            stats_doc = await find_document("user_stats", {"user_id": user_id})
            if not stats_doc:
                return
            
            stats = UserStats(**stats_doc)
            
            for badge_doc in project_badges:
                badge = Badge(**badge_doc)
                
                existing_badge = await find_document("user_badges", {
                    "user_id": user_id,
                    "badge_id": badge.id,
                    "earned": True
                })
                if existing_badge:
                    continue
                
                req_value = badge.requirements.get("projects_completed")
                if req_value and stats.completed_projects >= req_value:
                    await AchievementService._unlock_achievement(user_id, badge.id)
                    await AchievementService._create_achievement_notification(user_id, badge)
            
        except Exception as e:
            print(f"Error in project completion trigger: {e}")
    
    @staticmethod
    async def trigger_journal_entry_created(user_id: str):
        """Efficient trigger when a journal entry is created"""
        try:
            journal_badges = await find_documents("badges", {
                "$or": [
                    {"requirements.journal_entries": {"$exists": True}},
                    {"category": "reflection"}
                ]
            })
            
            stats_doc = await find_document("user_stats", {"user_id": user_id})
            if not stats_doc:
                return
            
            stats = UserStats(**stats_doc)
            
            for badge_doc in journal_badges:
                badge = Badge(**badge_doc)
                
                existing_badge = await find_document("user_badges", {
                    "user_id": user_id,
                    "badge_id": badge.id,
                    "earned": True
                })
                if existing_badge:
                    continue
                
                req_value = badge.requirements.get("journal_entries")
                if req_value and stats.total_journal_entries >= req_value:
                    await AchievementService._unlock_achievement(user_id, badge.id)
                    await AchievementService._create_achievement_notification(user_id, badge)
            
        except Exception as e:
            print(f"Error in journal entry trigger: {e}")
    
    @staticmethod
    async def trigger_course_completed(user_id: str):
        """Efficient trigger when a course is completed"""
        try:
            course_badges = await find_documents("badges", {
                "$or": [
                    {"requirements.courses_completed": {"$exists": True}},
                    {"category": "learning"}
                ]
            })
            
            stats_doc = await find_document("user_stats", {"user_id": user_id})
            if not stats_doc:
                return
            
            stats = UserStats(**stats_doc)
            
            for badge_doc in course_badges:
                badge = Badge(**badge_doc)
                
                existing_badge = await find_document("user_badges", {
                    "user_id": user_id,
                    "badge_id": badge.id,
                    "earned": True
                })
                if existing_badge:
                    continue
                
                req_value = badge.requirements.get("courses_completed")
                if req_value and stats.courses_completed >= req_value:
                    await AchievementService._unlock_achievement(user_id, badge.id)
                    await AchievementService._create_achievement_notification(user_id, badge)
            
        except Exception as e:
            print(f"Error in course completion trigger: {e}")

class CustomAchievementService:
    """Service for managing user-defined custom achievements"""
    
    @staticmethod
    async def create_custom_achievement(user_id: str, achievement_data: CustomAchievementCreate) -> CustomAchievement:
        """Create a new custom achievement for the user"""
        try:
            # Validate target if specific ID is provided
            if achievement_data.target_id:
                await CustomAchievementService._validate_target(user_id, achievement_data.target_type, achievement_data.target_id)
            
            custom_achievement = CustomAchievement(
                user_id=user_id,
                **achievement_data.dict()
            )
            
            await create_document("custom_achievements", custom_achievement.dict())
            return custom_achievement
            
        except Exception as e:
            print(f"Error creating custom achievement: {e}")
            raise ValueError(f"Failed to create custom achievement: {str(e)}")
    
    @staticmethod
    async def get_user_custom_achievements(user_id: str, include_completed: bool = True) -> List[CustomAchievementResponse]:
        """Get all custom achievements for a user"""
        try:
            query = {"user_id": user_id}
            if not include_completed:
                query["is_completed"] = False
            
            achievements_docs = await find_documents("custom_achievements", query)
            
            responses = []
            for doc in achievements_docs:
                response = await CustomAchievementService._build_custom_achievement_response(doc)
                responses.append(response)
            
            # Sort by completion status and creation date
            responses.sort(key=lambda x: (x.is_completed, -x.created_date.timestamp()))
            return responses
            
        except Exception as e:
            print(f"Error getting custom achievements: {e}")
            return []
    
    @staticmethod
    async def _build_custom_achievement_response(doc: dict) -> CustomAchievementResponse:
        """Build a custom achievement response with contextual information"""
        response = CustomAchievementResponse(**doc)
        
        # Calculate progress percentage
        if response.target_count > 0:
            response.progress_percentage = min((response.current_progress / response.target_count) * 100, 100)
        else:
            response.progress_percentage = 0
        
        # Get target name if applicable
        if response.target_id:
            target_name = await CustomAchievementService._get_target_name(response.target_type, response.target_id)
            response.target_name = target_name
        
        return response
    
    @staticmethod
    async def _get_target_name(target_type: CustomAchievementTargetTypeEnum, target_id: str) -> Optional[str]:
        """Get the name of the target entity"""
        try:
            if target_type == CustomAchievementTargetTypeEnum.complete_project:
                project_doc = await find_document("projects", {"id": target_id})
                return project_doc.get("name") if project_doc else None
            
            elif target_type == CustomAchievementTargetTypeEnum.complete_courses:
                course_doc = await find_document("courses", {"id": target_id})
                return course_doc.get("title") if course_doc else None
            
            return None
            
        except Exception as e:
            print(f"Error getting target name: {e}")
            return None
    
    @staticmethod
    async def update_custom_achievement(user_id: str, achievement_id: str, achievement_data: CustomAchievementUpdate) -> bool:
        """Update a custom achievement"""
        try:
            update_data = {k: v for k, v in achievement_data.dict().items() if v is not None}
            update_data["updated_at"] = datetime.utcnow()
            
            return await update_document("custom_achievements", {
                "id": achievement_id,
                "user_id": user_id
            }, update_data)
            
        except Exception as e:
            print(f"Error updating custom achievement: {e}")
            return False
    
    @staticmethod
    async def delete_custom_achievement(user_id: str, achievement_id: str) -> bool:
        """Delete a custom achievement"""
        try:
            return await delete_document("custom_achievements", {
                "id": achievement_id,
                "user_id": user_id
            })
            
        except Exception as e:
            print(f"Error deleting custom achievement: {e}")
            return False
    
    @staticmethod
    async def check_custom_achievements_progress(user_id: str):
        """Check and update progress for all active custom achievements"""
        try:
            # Get all active custom achievements for user
            active_achievements = await find_documents("custom_achievements", {
                "user_id": user_id,
                "is_active": True,
                "is_completed": False
            })
            
            newly_completed = []
            
            for achievement_doc in active_achievements:
                achievement = CustomAchievement(**achievement_doc)
                
                # Calculate current progress
                current_progress = await CustomAchievementService._calculate_custom_achievement_progress(
                    user_id, achievement.target_type, achievement.target_id
                )
                
                # Update progress if changed
                if current_progress != achievement.current_progress:
                    update_data = {"current_progress": current_progress}
                    
                    # Check if achievement is now completed
                    if current_progress >= achievement.target_count and not achievement.is_completed:
                        update_data.update({
                            "is_completed": True,
                            "completed_date": datetime.utcnow()
                        })
                        newly_completed.append(achievement)
                    
                    await update_document("custom_achievements", {"id": achievement.id}, update_data)
            
            # Create notifications for newly completed custom achievements
            for achievement in newly_completed:
                await CustomAchievementService._create_custom_achievement_notification(user_id, achievement)
            
            return newly_completed
            
        except Exception as e:
            print(f"Error checking custom achievements progress: {e}")
            return []
    
    @staticmethod
    async def _calculate_custom_achievement_progress(user_id: str, target_type: CustomAchievementTargetTypeEnum, target_id: Optional[str] = None) -> int:
        """Calculate current progress for a custom achievement"""
        try:
            if target_type == CustomAchievementTargetTypeEnum.complete_project:
                if target_id:
                    # Check if specific project is completed
                    project_doc = await find_document("projects", {"id": target_id, "user_id": user_id})
                    return 1 if project_doc and project_doc.get("status") == "Completed" else 0
                else:
                    # Count total completed projects
                    return await count_documents("projects", {"user_id": user_id, "status": "Completed"})
            
            elif target_type == CustomAchievementTargetTypeEnum.complete_tasks:
                if target_id:
                    # Count completed tasks in specific project
                    return await count_documents("tasks", {
                        "user_id": user_id,
                        "project_id": target_id,
                        "completed": True
                    })
                else:
                    # Count total completed tasks
                    return await count_documents("tasks", {"user_id": user_id, "completed": True})
            
            elif target_type == CustomAchievementTargetTypeEnum.write_journal_entries:
                return await count_documents("journal_entries", {"user_id": user_id})
            
            elif target_type == CustomAchievementTargetTypeEnum.complete_courses:
                if target_id:
                    # Check if specific course is completed
                    progress_doc = await find_document("user_course_progress", {
                        "user_id": user_id,
                        "course_id": target_id,
                        "progress_percentage": 100
                    })
                    return 1 if progress_doc else 0
                else:
                    # Count total completed courses
                    return await count_documents("user_course_progress", {
                        "user_id": user_id,
                        "progress_percentage": 100
                    })
            
            elif target_type == CustomAchievementTargetTypeEnum.maintain_streak:
                # Get user's current streak
                user_doc = await find_document("users", {"id": user_id})
                return user_doc.get("current_streak", 0) if user_doc else 0
            
            elif target_type == CustomAchievementTargetTypeEnum.reach_level:
                # Get user's current level
                user_doc = await find_document("users", {"id": user_id})
                return user_doc.get("level", 1) if user_doc else 1
            
            elif target_type == CustomAchievementTargetTypeEnum.earn_points:
                # Get user's total points
                user_doc = await find_document("users", {"id": user_id})
                return user_doc.get("total_points", 0) if user_doc else 0
            
            return 0
            
        except Exception as e:
            print(f"Error calculating custom achievement progress: {e}")
            return 0
    
    @staticmethod
    async def _validate_target(user_id: str, target_type: CustomAchievementTargetTypeEnum, target_id: str):
        """Validate that the target entity exists and belongs to the user"""
        try:
            if target_type == CustomAchievementTargetTypeEnum.complete_project:
                project_doc = await find_document("projects", {"id": target_id, "user_id": user_id})
                if not project_doc:
                    raise ValueError("Project not found or does not belong to user")
            
            elif target_type == CustomAchievementTargetTypeEnum.complete_tasks:
                project_doc = await find_document("projects", {"id": target_id, "user_id": user_id})
                if not project_doc:
                    raise ValueError("Project not found or does not belong to user")
            
            elif target_type == CustomAchievementTargetTypeEnum.complete_courses:
                course_doc = await find_document("courses", {"id": target_id})
                if not course_doc:
                    raise ValueError("Course not found")
            
        except Exception as e:
            print(f"Error validating target: {e}")
            raise
    
    @staticmethod
    async def _create_custom_achievement_notification(user_id: str, achievement: CustomAchievement):
        """Create a notification for custom achievement completion"""
        try:
            from notification_service import notification_service
            
            notification_data = {
                "user_id": user_id,
                "type": "achievement_unlocked",
                "title": f"🎉 Custom Goal Achieved!",
                "message": f"Congratulations! You've completed your custom goal: {achievement.name}",
                "data": {
                    "achievement_id": achievement.id,
                    "achievement_name": achievement.name,
                    "achievement_icon": achievement.icon,
                    "achievement_type": "custom"
                }
            }
            
            await notification_service.create_notification(notification_data)
            
        except Exception as e:
            print(f"Error creating custom achievement notification: {e}")
    
    # TRIGGER FUNCTIONS FOR CUSTOM ACHIEVEMENTS
    # These are called from existing services when actions occur
    
    @staticmethod
    async def trigger_custom_achievements_check(user_id: str, action_type: str, entity_id: str = None):
        """Efficient trigger to check custom achievements when actions occur"""
        try:
            # Only check custom achievements that might be affected by this action
            query = {"user_id": user_id, "is_active": True, "is_completed": False}
            
            # Filter by relevant target types based on action
            if action_type == "task_completed":
                query["target_type"] = {"$in": ["complete_tasks"]}
            elif action_type == "project_completed":
                query["target_type"] = {"$in": ["complete_project"]}
            elif action_type == "journal_entry_created":
                query["target_type"] = {"$in": ["write_journal_entries"]}
            elif action_type == "course_completed":
                query["target_type"] = {"$in": ["complete_courses"]}
            
            relevant_achievements = await find_documents("custom_achievements", query)
            
            # Check progress for each relevant achievement
            for achievement_doc in relevant_achievements:
                achievement = CustomAchievement(**achievement_doc)
                
                # Skip if this achievement is for a different entity
                if achievement.target_id and entity_id and achievement.target_id != entity_id:
                    continue
                
                # Calculate new progress
                current_progress = await CustomAchievementService._calculate_custom_achievement_progress(
                    user_id, achievement.target_type, achievement.target_id
                )
                
                # Update if progress changed
                if current_progress != achievement.current_progress:
                    update_data = {"current_progress": current_progress}
                    
                    # Check if completed
                    if current_progress >= achievement.target_count:
                        update_data.update({
                            "is_completed": True,
                            "completed_date": datetime.utcnow()
                        })
                        
                        # Create notification
                        await CustomAchievementService._create_custom_achievement_notification(user_id, achievement)
                    
                    await update_document("custom_achievements", {"id": achievement.id}, update_data)
            
        except Exception as e:
            print(f"Error in custom achievements trigger: {e}")

class ResourceService:
    """Service for managing file resources and attachments"""
    
    @staticmethod
    async def create_resource(user_id: str, resource_data: ResourceCreate) -> Resource:
        """Create a new file resource with contextual attachment support"""
        import base64
        import magic
        from datetime import datetime, timedelta
        
        # Validate parent entity if provided
        if resource_data.parent_id and resource_data.parent_type:
            await ResourceService._validate_parent_entity(user_id, resource_data.parent_id, resource_data.parent_type)
        
        # Validate file content is proper base64
        try:
            file_bytes = base64.b64decode(resource_data.file_content)
            
            # Detect MIME type if not provided or verify provided type
            mime = magic.Magic(mime=True)
            detected_mime = mime.from_buffer(file_bytes)
            
            # Update mime_type if detection is more accurate
            if detected_mime and detected_mime != "application/octet-stream":
                resource_data.mime_type = detected_mime
                
        except Exception as e:
            raise ValueError(f"Invalid file content: {e}")
        
        # Validate file size (limit to 10MB as per requirements)
        max_file_size = 10 * 1024 * 1024  # 10MB
        if resource_data.file_size > max_file_size:
            raise ValueError(f"File size exceeds maximum limit of {max_file_size // (1024*1024)}MB")
        
        # Determine file type based on MIME type
        detected_file_type = ResourceService._determine_file_type(resource_data.mime_type)
        
        # Create resource data dict and update file_type if detection is more accurate
        resource_dict = resource_data.dict()
        if detected_file_type != FileTypeEnum.other:
            resource_dict['file_type'] = detected_file_type
        
        resource = Resource(
            user_id=user_id,
            **resource_dict
        )
        
        resource_dict = resource.dict()
        await create_document("resources", resource_dict)
        return resource
    
    @staticmethod
    async def _validate_parent_entity(user_id: str, parent_id: str, parent_type: str):
        """Validate that parent entity exists and belongs to user"""
        entity_collections = {
            "task": "tasks",
            "project": "projects", 
            "area": "areas",
            "pillar": "pillars",
            "journal_entry": "journal_entries"
        }
        
        if parent_type not in entity_collections:
            raise ValueError(f"Invalid parent type: {parent_type}. Must be one of: {', '.join(entity_collections.keys())}")
        
        collection_name = entity_collections[parent_type]
        entity_doc = await find_document(collection_name, {"id": parent_id, "user_id": user_id})
        if not entity_doc:
            raise ValueError(f"Parent {parent_type} with ID {parent_id} not found or does not belong to user")
    
    @staticmethod
    def _determine_file_type(mime_type: str) -> FileTypeEnum:
        """Determine file type from MIME type"""
        mime_lower = mime_type.lower()
        
        if any(doc_type in mime_lower for doc_type in ['pdf', 'msword', 'wordprocessingml', 'text/plain', 'rtf']):
            return FileTypeEnum.document
        elif any(img_type in mime_lower for img_type in ['image/', 'png', 'jpg', 'jpeg', 'gif', 'svg']):
            return FileTypeEnum.image
        elif any(sheet_type in mime_lower for sheet_type in ['spreadsheet', 'excel', 'csv']):
            return FileTypeEnum.spreadsheet
        elif any(pres_type in mime_lower for pres_type in ['presentation', 'powerpoint']):
            return FileTypeEnum.presentation
        elif any(arch_type in mime_lower for arch_type in ['zip', 'rar', 'tar', 'gzip']):
            return FileTypeEnum.archive
        else:
            return FileTypeEnum.other
    
    @staticmethod
    async def get_user_resources(
        user_id: str, 
        category: Optional[str] = None,
        file_type: Optional[str] = None,
        folder_path: Optional[str] = None,
        include_archived: bool = False,
        search_query: Optional[str] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[ResourceResponse]:
        """Get user's resources with filtering and pagination"""
        
        # Build query
        query = {"user_id": user_id}
        
        if not include_archived:
            query["is_archived"] = {"$ne": True}
        
        if category:
            query["category"] = category
            
        if file_type:
            query["file_type"] = file_type
            
        if folder_path:
            query["folder_path"] = folder_path
        
        # Search functionality
        if search_query:
            search_regex = {"$regex": search_query, "$options": "i"}
            query["$or"] = [
                {"filename": search_regex},
                {"original_filename": search_regex},
                {"description": search_regex},
                {"tags": {"$in": [search_query]}}
            ]
        
        # Get resources with pagination
        resources_docs = await find_documents("resources", query)
        
        # Sort by upload_date descending
        resources_docs.sort(key=lambda x: x.get("upload_date", datetime.min), reverse=True)
        
        # Apply pagination
        paginated_resources = resources_docs[skip:skip + limit]
        
        # Build response objects
        responses = []
        for doc in paginated_resources:
            response = await ResourceService._build_resource_response(doc)
            responses.append(response)
        
        return responses
    
    @staticmethod
    async def get_resource(user_id: str, resource_id: str, track_access: bool = True) -> Optional[ResourceResponse]:
        """Get a specific resource by ID"""
        resource_doc = await find_document("resources", {"id": resource_id, "user_id": user_id})
        if not resource_doc:
            return None
        
        # Track access if requested
        if track_access:
            await ResourceService._track_resource_access(resource_id)
        
        return await ResourceService._build_resource_response(resource_doc)
    
    @staticmethod
    async def get_resource_content(user_id: str, resource_id: str) -> Optional[dict]:
        """Get resource file content for viewing/downloading"""
        resource_doc = await find_document("resources", {"id": resource_id, "user_id": user_id})
        if not resource_doc:
            return None
        
        # Track access
        await ResourceService._track_resource_access(resource_id)
        
        return {
            "id": resource_doc["id"],
            "filename": resource_doc["filename"],
            "mime_type": resource_doc["mime_type"],
            "file_size": resource_doc["file_size"],
            "file_content": resource_doc["file_content"]  # Base64 content
        }
    
    @staticmethod
    async def _track_resource_access(resource_id: str):
        """Track when a resource is accessed"""
        # Update last_accessed timestamp
        await update_document(
            "resources",
            {"id": resource_id},
            {"last_accessed": datetime.utcnow()}
        )
        
        # Increment access_count using atomic operation
        await atomic_update_document(
            "resources",
            {"id": resource_id},
            {"$inc": {"access_count": 1}}
        )
    
    @staticmethod
    async def update_resource(user_id: str, resource_id: str, resource_data: ResourceUpdate) -> bool:
        """Update a resource"""
        update_data = {k: v for k, v in resource_data.dict().items() if v is not None}
        update_data["updated_at"] = datetime.utcnow()
        
        return await update_document("resources", {"id": resource_id, "user_id": user_id}, update_data)
    
    @staticmethod
    async def delete_resource(user_id: str, resource_id: str) -> bool:
        """Delete a resource and clean up attachments"""
        # Remove resource from all attachments
        await ResourceService._cleanup_resource_attachments(resource_id)
        
        # Delete the resource document
        return await delete_document("resources", {"id": resource_id, "user_id": user_id})
    
    @staticmethod
    async def attach_resource_to_entity(
        user_id: str, 
        resource_id: str, 
        entity_type: str, 
        entity_id: str
    ) -> bool:
        """Attach a resource to an entity (task, project, area, pillar, journal_entry)"""
        
        # Validate entity exists and belongs to user
        entity_collections = {
            "task": "tasks",
            "project": "projects", 
            "area": "areas",
            "pillar": "pillars",
            "journal_entry": "journal_entries"
        }
        
        if entity_type not in entity_collections:
            raise ValueError(f"Invalid entity type: {entity_type}")
        
        collection_name = entity_collections[entity_type]
        entity_doc = await find_document(collection_name, {"id": entity_id, "user_id": user_id})
        if not entity_doc:
            raise ValueError(f"Entity {entity_type} not found")
        
        # Check if resource exists and belongs to user
        resource_doc = await find_document("resources", {"id": resource_id, "user_id": user_id})
        if not resource_doc:
            raise ValueError("Resource not found")
        
        # Add attachment relationship  
        attachment_field = f"attached_to_{entity_type}s"
        if entity_type == "journal_entry":
            attachment_field = "attached_to_journal_entries"
        
        # Use atomic operation to add to array if not exists
        await atomic_update_document(
            "resources",
            {"id": resource_id, "user_id": user_id},
            {"$addToSet": {attachment_field: entity_id}}
        )
        
        return True
    
    @staticmethod
    async def detach_resource_from_entity(
        user_id: str,
        resource_id: str,
        entity_type: str, 
        entity_id: str
    ) -> bool:
        """Detach a resource from an entity"""
        
        attachment_field = f"attached_to_{entity_type}s"
        if entity_type == "journal_entry":
            attachment_field = "attached_to_journal_entries"
        
        # Remove from attachment array
        await atomic_update_document(
            "resources",
            {"id": resource_id, "user_id": user_id},
            {"$pull": {attachment_field: entity_id}}
        )
        
        return True
    
    @staticmethod
    async def get_entity_resources(user_id: str, entity_type: str, entity_id: str) -> List[ResourceResponse]:
        """Get all resources attached to a specific entity (legacy method)"""
        
        attachment_field = f"attached_to_{entity_type}s"
        if entity_type == "journal_entry":
            attachment_field = "attached_to_journal_entries"
        
        query = {
            "user_id": user_id,
            attachment_field: entity_id,
            "is_archived": {"$ne": True}
        }
        
        resources_docs = await find_documents("resources", query)
        resources_docs.sort(key=lambda x: x.get("upload_date", datetime.min), reverse=True)
        
        responses = []
        for doc in resources_docs:
            response = await ResourceService._build_resource_response(doc)
            responses.append(response)
        
        return responses
    
    @staticmethod
    async def get_parent_resources(user_id: str, parent_type: str, parent_id: str) -> List[ResourceResponse]:
        """Get all resources attached to a specific parent entity (contextual attachments)"""
        
        # Validate parent type
        valid_parent_types = ["task", "project", "area", "pillar", "journal_entry"]
        if parent_type not in valid_parent_types:
            raise ValueError(f"Invalid parent type: {parent_type}. Must be one of: {', '.join(valid_parent_types)}")
        
        query = {
            "user_id": user_id,
            "parent_type": parent_type,
            "parent_id": parent_id,
            "is_archived": {"$ne": True}
        }
        
        resources_docs = await find_documents("resources", query)
        resources_docs.sort(key=lambda x: x.get("upload_date", datetime.min), reverse=True)
        
        responses = []
        for doc in resources_docs:
            response = await ResourceService._build_resource_response(doc)
            responses.append(response)
        
        return responses
    
    @staticmethod
    async def _cleanup_resource_attachments(resource_id: str):
        """Remove resource ID from all entity attachment lists"""
        # This would be more efficient with a background cleanup task
        # For now, we'll leave the attachment references (they're just IDs)
        # A periodic cleanup job could remove dangling references
        pass
    
    @staticmethod
    async def _build_resource_response(resource_doc: dict) -> ResourceResponse:
        """Build a comprehensive resource response"""
        response = ResourceResponse(**resource_doc)
        
        # Calculate file size in MB
        response.file_size_mb = round(response.file_size / (1024 * 1024), 2)
        
        # Count total attachments
        response.attachments_count = (
            len(response.attached_to_tasks) +
            len(response.attached_to_projects) +
            len(response.attached_to_areas) +
            len(response.attached_to_pillars) +
            len(response.attached_to_journal_entries)
        )
        
        return response

# Import magic library error handling
try:
    import python_magic as magic
except ImportError:
    try:
        import magic
    except ImportError:
        # Fallback without MIME type detection
        class MockMagic:
            def __init__(self, mime=True):
                pass
            def from_buffer(self, buffer):
                return "application/octet-stream"
        magic = MockMagic