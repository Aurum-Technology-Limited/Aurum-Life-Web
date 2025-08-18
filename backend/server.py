@@
-from database import connect_to_mongo, close_mongo_connection, update_document
+from database import connect_to_mongo, close_mongo_connection, update_document, ensure_indexes
@@
 @app.on_event("startup")
 async def on_startup():
     try:
         await connect_to_mongo()
+        try:
+            await ensure_indexes()
+        except Exception as e:
+            logger.warning(f"Mongo ensure_indexes warning: {e}")
     except Exception as e:
         logger.error(f"Mongo startup failed: {e}")
@@
 @api_router.post('/journal/{entry_id}/restore')
 async def api_restore_journal(entry_id: str, current_user: User = Depends(get_current_active_user_hybrid)):
@@
     return { 'success': True }
+
+# Trash endpoints for Journal
+@api_router.get('/journal/trash')
+async def api_journal_trash(current_user: User = Depends(get_current_active_user_hybrid), skip: int = Query(0, ge=0), limit: int = Query(20, ge=1, le=100)):
+    try:
+        entries = await JournalService.get_deleted_entries(str(current_user.id), skip, limit)
+        return entries
+    except Exception as e:
+        logger.error(f'Journal trash list error: {e}')
+        raise HTTPException(status_code=500, detail='Failed to load trash entries')
+
+@api_router.delete('/journal/{entry_id}/purge')
+async def api_journal_purge(entry_id: str, current_user: User = Depends(get_current_active_user_hybrid)):
+    try:
+        ok = await JournalService.purge_entry(str(current_user.id), entry_id)
+        if not ok:
+            raise HTTPException(status_code=404, detail='Journal entry not found')
+        return { 'success': True }
+    except HTTPException:
+        raise
+    except Exception as e:
+        logger.error(f'Journal purge error: {e}')
+        raise HTTPException(status_code=500, detail='Failed to permanently delete entry')