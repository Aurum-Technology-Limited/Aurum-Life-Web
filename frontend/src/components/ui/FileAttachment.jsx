import React, { useState } from 'react';

// Minimal placeholder to satisfy imports and prevent runtime crashes
// Props: parentType ("task" | "project"), parentId, parentName
const FileAttachment = ({ parentType = 'task', parentId, parentName }) => {
  const [files, setFiles] = useState([]);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    try {
      const selected = Array.from(e.target.files || []);
      setFiles((prev) => [...prev, ...selected]);
    } catch (err) {
      setError(err?.message || 'Failed to add files');
    }
  };

  const removeFile = (idx) => {
    setFiles((prev) => prev.filter((_, i) => i !== idx));
  };

  return (
    <div className="mt-3 border border-gray-700 rounded-lg p-3 bg-gray-800">
      <div className="text-sm text-gray-300 font-medium mb-2">
        Attachments {parentName ? `for ${parentName}` : ''}
      </div>
      <div className="text-xs text-gray-400 mb-2">
        This is a lightweight placeholder. Upload handling will be added later.
      </div>
      <input
        type="file"
        multiple
        onChange={handleFileChange}
        className="text-xs text-gray-300"
      />
      {error && (
        <div className="mt-2 text-xs text-red-400">{error}</div>
      )}
      {files.length > 0 && (
        <div className="mt-3 space-y-1">
          {files.map((f, idx) => (
            <div key={idx} className="flex items-center justify-between text-xs text-gray-300 bg-gray-900 rounded px-2 py-1">
              <span className="truncate mr-2">{f.name}</span>
              <button
                type="button"
                onClick={() => removeFile(idx)}
                className="px-2 py-0.5 rounded bg-gray-700 hover:bg-gray-600 text-gray-200"
              >
                Remove
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
};

export default FileAttachment;
