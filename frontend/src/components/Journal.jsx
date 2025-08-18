@@
-  const [currentView, setCurrentView] = useState('entries'); // 'entries', 'insights', 'templates'
+  const [currentView, setCurrentView] = useState('entries'); // 'entries', 'insights', 'templates', 'trash'
   const [searchTerm, setSearchTerm] = useState('');
   const [selectedMoodFilter, setSelectedMoodFilter] = useState('');
   const [selectedTagFilter, setSelectedTagFilter] = useState('');
   const [showFilters, setShowFilters] = useState(false);
+  const [trashEntries, setTrashEntries] = useState([]);
@@
   const fetchTemplatesWithFallback = async () => {
@@
   };
+
+  const fetchTrash = async () => {
+    try {
+      const response = await journalAPI.getTrash();
+      const data = response.data || [];
+      setTrashEntries(Array.isArray(data) ? data : []);
+    } catch (err) {
+      console.warn('⚠️ Journal trash endpoint not available:', err.message);
+      setTrashEntries([]);
+    }
+  };
@@
   const handleDeleteEntry = async (entryId) => {
     if (!window.confirm('Are you sure you want to delete this journal entry?')) return;
     
     try {
       setIsSyncing(true);
       await journalAPI.deleteEntry(entryId);
       setEntries(prev => prev.filter(entry => entry.id !== entryId));
       setViewingEntry(null);
+      // Refresh trash to include this entry if server marks as deleted
+      fetchTrash();
     } catch (err) {
       setError(handleApiError(err, 'Failed to delete entry'));
     }
   };
+
+  const handleRestoreEntry = async (entryId) => {
+    try {
+      setIsSyncing(true);
+      await journalAPI.restoreEntry(entryId);
+      // Move from trash to entries by refetching lists
+      await fetchEntriesWithFallback();
+      setTrashEntries(prev => prev.filter(e => e.id !== entryId));
+    } catch (err) {
+      setError(handleApiError(err, 'Failed to restore entry'));
+    } finally {
+      setIsSyncing(false);
+    }
+  };
+
+  const handlePurgeEntry = async (entryId) => {
+    if (!window.confirm('Permanently delete this entry? This cannot be undone.')) return;
+    try {
+      setIsSyncing(true);
+      await journalAPI.purgeEntry(entryId);
+      setTrashEntries(prev => prev.filter(e => e.id !== entryId));
+    } catch (err) {
+      setError(handleApiError(err, 'Failed to permanently delete entry'));
+    } finally {
+      setIsSyncing(false);
+    }
+  };
@@
   return (
     <div className="space-y-8">
@@
       {/* Navigation Tabs */}
       <div className="flex items-center space-x-1 bg-gray-800/50 p-1 rounded-lg">
         <button
           onClick={() => setCurrentView('entries')}
@@
         </button>
         <button
           onClick={() => setCurrentView('insights')}
@@
         </button>
         <button
           onClick={() => setCurrentView('templates')}
@@
         </button>
+        <button
+          onClick={() => {
+            setCurrentView('trash');
+            fetchTrash();
+          }}
+          className={`flex items-center space-x-2 px-4 py-2 rounded-md transition-colors ${
+            currentView === 'trash' 
+              ? 'bg-yellow-400 text-gray-900' 
+              : 'text-gray-400 hover:text-white hover:bg-gray-700'
+          }`}
+        >
+          <RotateCcw size={16} />
+          <span>Trash</span>
+        </button>
       </div>
@@
-      {/* Informational message when journal backend is not fully available */}
-      {entries.length === 0 && templates.length > 0 && !loading && !error && (
-        <div className="p-4 rounded-lg bg-blue-900/20 border border-blue-500/30 flex items-center space-x-2">
-          <AlertCircle size={20} className="text-blue-400" />
-          <span className="text-blue-400">
-            Journal backend endpoints are being set up. You can use the templates and create entries locally for now.
-          </span>
-        </div>
-      )}
+      {/* Info banner removed as backend is now fully set up */}
@@
       {/* Render different views based on currentView */}
       {currentView === 'entries' &amp;&amp; renderEntriesView()}
       {currentView === 'insights' &amp;&amp; renderInsightsView()}
       {currentView === 'templates' &amp;&amp; renderTemplatesView()}
+      {currentView === 'trash' &amp;&amp; (
+        <div className="space-y-6">
+          {trashEntries.length > 0 ? (
+            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
+              {trashEntries.map((entry) => (
+                <div key={entry.id} className="p-6 rounded-xl border border-gray-800 bg-gradient-to-br from-gray-900/50 to-gray-800/30">
+                  <div className="flex items-center justify-between mb-2">
+                    <h3 className="text-lg font-semibold text-white">{entry.title}</h3>
+                    <span className="text-xs text-gray-500">Deleted {new Date(entry.deleted_at || entry.updated_at || entry.created_at).toLocaleString()}</span>
+                  </div>
+                  <p className="text-gray-300 text-sm mb-4 line-clamp-3">{entry.content}</p>
+                  <div className="flex items-center gap-3">
+                    <button onClick={() => handleRestoreEntry(entry.id)} className="px-3 py-2 rounded bg-green-600 text-white hover:bg-green-500 transition-colors">Restore</button>
+                    <button onClick={() => handlePurgeEntry(entry.id)} className="px-3 py-2 rounded bg-red-600 text-white hover:bg-red-500 transition-colors">Delete Forever</button>
+                  </div>
+                </div>
+              ))}
+            </div>
+          ) : (
+            <div className="text-center py-12">
+              <div className="w-16 h-16 rounded-lg bg-yellow-400/20 flex items-center justify-center mx-auto mb-4">
+                <RotateCcw size={32} className="text-yellow-400" />
+              </div>
+              <h3 className="text-xl font-semibold text-white mb-2">Trash is empty</h3>
+              <p className="text-gray-400">Deleted entries will appear here for review.</p>
+            </div>
+          )}
+        </div>
+      )}
@@
     </div>
   );