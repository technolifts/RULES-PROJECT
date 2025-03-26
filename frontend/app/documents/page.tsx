'use client';

import { useState, useEffect } from 'react';
import ProtectedRoute from '@/components/ProtectedRoute';
import { useAuth } from '@/contexts/AuthContext';
import DocumentUpload from '@/components/DocumentUpload';
import DocumentList from '@/components/DocumentList';
import axios from 'axios';

export default function Documents() {
  const { user, token, logout } = useAuth();
  const [documents, setDocuments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showUploadModal, setShowUploadModal] = useState(false);

  const fetchDocuments = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.get('http://localhost:8000/documents/', {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      setDocuments(response.data);
    } catch (err) {
      setError('Failed to load documents');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    if (token) {
      fetchDocuments();
    }
  }, [token]);

  const handleDocumentUpload = () => {
    fetchDocuments();
    setShowUploadModal(false);
  };

  const handleDeleteDocument = async (documentId) => {
    try {
      await axios.delete(`http://localhost:8000/documents/${documentId}`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      // Refresh document list
      fetchDocuments();
    } catch (err) {
      setError('Failed to delete document');
      console.error(err);
    }
  };

  return (
    <ProtectedRoute>
      <div className="min-h-screen bg-gray-100">
        <nav className="bg-white shadow-sm">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <div className="flex justify-between h-16">
              <div className="flex">
                <div className="flex-shrink-0 flex items-center">
                  <h1 className="text-xl font-bold">DocSecure</h1>
                </div>
              </div>
              <div className="flex items-center">
                <span className="text-gray-700 mr-4">Welcome, {user?.username}</span>
                <button
                  onClick={logout}
                  className="inline-flex items-center px-3 py-1.5 border border-transparent text-xs font-medium rounded-md shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                >
                  Logout
                </button>
              </div>
            </div>
          </div>
        </nav>

        <div className="py-10">
          <header>
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 flex justify-between items-center">
              <h1 className="text-3xl font-bold leading-tight text-gray-900">Documents</h1>
              <button
                onClick={() => setShowUploadModal(true)}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
              >
                Upload Document
              </button>
            </div>
          </header>
          <main>
            <div className="max-w-7xl mx-auto sm:px-6 lg:px-8">
              <div className="px-4 py-8 sm:px-0">
                {error && (
                  <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
                    <span className="block sm:inline">{error}</span>
                  </div>
                )}
                
                {loading ? (
                  <div className="flex justify-center items-center h-64">
                    <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
                  </div>
                ) : documents.length > 0 ? (
                  <DocumentList documents={documents} onDelete={handleDeleteDocument} />
                ) : (
                  <div className="border-4 border-dashed border-gray-200 rounded-lg h-64 flex items-center justify-center">
                    <p className="text-gray-500">No documents yet. Upload your first document.</p>
                  </div>
                )}
              </div>
            </div>
          </main>
        </div>
        
        {showUploadModal && (
          <DocumentUpload 
            onClose={() => setShowUploadModal(false)} 
            onUploadSuccess={handleDocumentUpload}
          />
        )}
      </div>
    </ProtectedRoute>
  );
}
