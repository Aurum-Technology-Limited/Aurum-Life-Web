import React from 'react';

const FileAttachment = ({ 
  parentType, 
  parentId, 
  parentName = 'item',
  className = ''
}) => {
  return (
    <div className={`file-attachment ${className}`}>
      <div className="bg-gray-800 rounded-lg p-4 mt-4">
        <div className="text-white">
          <h4 className="text-md font-medium mb-2">
            FileAttachment Component Test
          </h4>
          <p className="text-sm text-gray-300">
            Parent Type: {parentType}
          </p>
          <p className="text-sm text-gray-300">
            Parent ID: {parentId}
          </p>
          <p className="text-sm text-gray-300">
            Parent Name: {parentName}
          </p>
        </div>
      </div>
    </div>
  );
};

export default FileAttachment;