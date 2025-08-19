import React, { useState, useMemo } from 'react';
import { uploadsAPI, handleApiError } from '../../services/api';

const CHUNK_SIZE = 1024 * 1024; // 1MB

const FileAttachment = ({ parentType = 'task', parentId = null, parentName = '' }) => {
  const [items, setItems] = useState([]); // {file, progress, status, error, url, uploadId}
  const [error, setError] = useState(null);

  const canUpload = useMemo(() => true, []);

  const onFilesSelected = async (e) => {
    const files = Array.from(e.target.files || []);
    for (const file of files) {
      await startUpload(file);
    }
    e.target.value = '';
  };

  const startUpload = async (file) => {
    const entry = { file, progress: 0, status: 'initiating', error: null, url: null, uploadId: null };
    setItems((prev) => [...prev, entry]);
    try {
      const initResp = await uploadsAPI.initiate({ filename: file.name, size: file.size, parentType, parentId });
      const { upload_id, chunk_size, total_chunks } = initResp.data;
      entry.uploadId = upload_id;
      entry.status = 'uploading';
      setItems((prev) => [...prev]);

      const chunkSize = chunk_size || CHUNK_SIZE;
      const total = total_chunks || Math.max(1, Math.ceil(file.size / chunkSize));

      for (let index = 0; index < total; index++) {
        const start = index * chunkSize;
        const end = Math.min(file.size, start + chunkSize);
        const blob = file.slice(start, end);
        await uploadsAPI.uploadChunk({ uploadId: upload_id, index, total, blob });
        entry.progress = Math.round(((index + 1) / total) * 100);
        setItems((prev) => [...prev]);
      }

      const completeResp = await uploadsAPI.complete({ uploadId: upload_id });
      entry.status = 'completed';
      entry.url = (completeResp.data && completeResp.data.file_url) || null;
      setItems((prev) => [...prev]);
    } catch (err) {
      entry.status = 'error';
      entry.error = handleApiError(err, 'Upload failed');
      setItems((prev) => [...prev]);
      setError(entry.error);
    }
  };

  const removeItem = (idx) => {
    setItems((prev) => prev.filter((_, i) => i !== idx));
  };

  return (
    <div className="mt-3 border border-gray-700 rounded-lg p-3 bg-gray-800">
      <div className="flex items-center justify-between">
        <div className="text-sm text-gray-300 font-medium">Attachments {parentName ? `for ${parentName}` : ''}</div>
      </div>
      <div className="text-xs text-gray-400 mb-2">
        Chunked uploads enabled (1MB). Files are stored temporarily on the server in this demo.
      </div>
      <input type="file" multiple onChange={onFilesSelected} className="text-xs text-gray-300" disabled={!canUpload} />
      {error && (
        <div className="mt-2 text-xs text-red-400">{error}</div>
      )}
      {items.length > 0 && (
        <div className="mt-3 space-y-2">
          {items.map((it, idx) => (
            <div key={idx} className="bg-gray-900 rounded p-2 text-xs text-gray-300 border border-gray-700">
              <div className="flex items-center justify-between">
                <span className="truncate mr-2">{it.file?.name}</span>
                <button onClick={() => removeItem(idx)} className="px-2 py-0.5 rounded bg-gray-700 hover:bg-gray-600 text-gray-200">Remove</button>
              </div>
              <div className="h-2 mt-2 bg-gray-700 rounded">
                <div className="h-2 bg-yellow-500 rounded" style={{ width: `${it.progress || 0}%` }} />
              </div>
              <div className="mt-1 text-gray-400">{it.status}{it.url ? ` • Ready: ${it.url}` : ''}{it.error ? ` • ${it.error}` : ''}</div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FileAttachment;