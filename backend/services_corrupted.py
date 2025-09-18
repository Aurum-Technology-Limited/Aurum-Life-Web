@@
 class JournalService:
@@
     @staticmethod
     async def get_user_entries(user_id: str, skip: int = 0, limit: int = 20, 
                               mood_filter: Optional[str] = None,
                               tag_filter: Optional[str] = None,
                               date_from: Optional[datetime] = None,
                               date_to: Optional[datetime] = None) -> List[JournalEntryResponse]:
@@
         return responses
+
+    @staticmethod
+    async def get_deleted_entries(user_id: str, skip: int = 0, limit: int = 20) -> List[JournalEntryResponse]:
+        """List soft-deleted entries for Trash view"""
+        query = {"user_id": user_id, "deleted": True}
+        docs = await find_documents("journal_entries", query, skip=skip, limit=limit)
+        # Sort by deleted_at desc with fallback to created_at
+        def sort_key(x):
+            dt = x.get("deleted_at") or x.get("created_at")
+            try:
+                return dt if isinstance(dt, datetime) else datetime.fromisoformat(str(dt).replace('Z', '+00:00'))
+            except Exception:
+                return datetime.min
+        docs.sort(key=sort_key, reverse=True)
+        responses = []
+        for doc in docs:
+            responses.append(await JournalService._build_journal_entry_response(doc))
+        return responses
+
+    @staticmethod
+    async def purge_entry(user_id: str, entry_id: str) -> bool:
+        """Permanently delete a journal entry (Trash purge)"""
+        # Verify ownership first
+        doc = await find_document("journal_entries", {"id": entry_id, "user_id": user_id})
+        if not doc:
+            return False
+        return await delete_document("journal_entries", {"id": entry_id})