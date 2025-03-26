'use client';

import { useState } from 'react';
import { formatDistanceToNow } from 'date-fns';

export default function DocumentList({ documents, onDelete }) {
  const [confirmDelete, setConfirmDelete] = useState(null);

  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString);
      return formatDistanceToNow(date, { addSuffix: true });
    } catch (error) {
      return dateString;
    }
  };

  const handleDeleteClick = (documentId) => {
    setConfirmDelete(documentId);
  };

  const confirmDeleteDocument = () => {
    if (confirmDelete) {
      onDelete(confirmDelete);
      setConfirmDelete(null);
    }
  };

  const cancelDelete = () => {
    setConfirmDelete(null);
  };

  const getFileIcon = (contentType) => {
    if (contentType.includes('pdf')) {
      return '📄';
    } else if (contentType.includes('word') || contentType.includes('document')) {
      return '📝';
    } else if (contentType.includes('excel') || contentType.includes('spreadsheet')) {
      return '📊';
    } else if (contentType.includes('powerpoint') || contentType.includes('presentation')) {
      return '📑';
    } else if (contentType.includes('image')) {
      return '🖼️';
    } else if (contentType.includes('text')) {
      return '📃';
    } else {
      return '📁';
    }
  };

  return (
    <div className="bg-white shadow overflow-hidden sm:rounded-md">
      <ul className="divide-y divide-gray-200">
        {documents.map((document) => (
          <li key={document.id}>
            <div className="px-4 py-4 sm:px-6">
              <div className="flex items-center justify-between">
                <div className="flex items-center">
                  <span className="text-2xl mr-3">{getFileIcon(document.content_type)}</span>
                  <p className="text-sm font-medium text-blue-600 truncate">
                    {document.original_filename}
                  </p>
                </div>
                <div className="ml-2 flex-shrink-0 flex">
                  {confirmDelete === document.id ? (
                    <div className="flex space-x-2">
                      <button
                        onClick={confirmDeleteDocument}
                        className="inline-flex items-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                      >
                        Confirm
                      </button>
                      <button
                        onClick={cancelDelete}
                        className="inline-flex items-center px-2.5 py-1.5 border border-gray-300 text-xs font-medium rounded text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                      >
                        Cancel
                      </button>
                    </div>
                  ) : (
                    <button
                      onClick={() => handleDeleteClick(document.id)}
                      className="inline-flex items-center px-2.5 py-1.5 border border-transparent text-xs font-medium rounded text-red-700 bg-red-100 hover:bg-red-200 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                    >
                      Delete
                    </button>
                  )}
                </div>
              </div>
              <div className="mt-2 sm:flex sm:justify-between">
                <div className="sm:flex">
                  <p className="flex items-center text-sm text-gray-500">
                    {document.description || 'No description'}
                  </p>
                </div>
                <div className="mt-2 flex items-center text-sm text-gray-500 sm:mt-0">
                  <p>
                    Uploaded {formatDate(document.created_at)}
                  </p>
                </div>
              </div>
            </div>
          </li>
        ))}
      </ul>
    </div>
  );
}
