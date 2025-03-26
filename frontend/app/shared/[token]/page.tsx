'use client';

import { useState, useEffect } from 'react';
import { useParams } from 'next/navigation';
import axios from 'axios';
import { format } from 'date-fns';
import Link from 'next/link';

export default function SharedDocument() {
  const params = useParams();
  const token = params.token;
  
  const [document, setDocument] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchSharedDocument();
  }, [token]);

  const fetchSharedDocument = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await axios.get(`http://localhost:8000/public/documents/${token}`);
      setDocument(response.data);
    } catch (err) {
      setError('This share link is invalid or has expired');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDownload = () => {
    window.location.href = `http://localhost:8000/public/documents/${token}/download`;
  };

  const formatDate = (dateString) => {
    try {
      const date = new Date(dateString);
      return format(date, 'PPP');
    } catch (error) {
      return dateString;
    }
  };

  const getFileIcon = (contentType) => {
    if (!contentType) return '📁';
    
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
    <div className="min-h-screen bg-gray-100 flex flex-col">
      <nav className="bg-white shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between h-16">
            <div className="flex">
              <div className="flex-shrink-0 flex items-center">
                <Link href="/" className="text-xl font-bold">DocSecure</Link>
              </div>
            </div>
          </div>
        </div>
      </nav>

      <div className="flex-grow flex items-center justify-center p-4">
        <div className="max-w-md w-full bg-white shadow-lg rounded-lg overflow-hidden">
          <div className="px-6 py-8">
            <div className="text-center mb-8">
              <h1 className="text-2xl font-bold text-gray-800">Shared Document</h1>
            </div>
            
            {loading ? (
              <div className="flex justify-center items-center h-32">
                <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-blue-500"></div>
              </div>
            ) : error ? (
              <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative" role="alert">
                <p className="text-center">{error}</p>
              </div>
            ) : document ? (
              <div>
                <div className="flex justify-center mb-6">
                  <span className="text-6xl">{getFileIcon(document.content_type)}</span>
                </div>
                
                <div className="mb-6">
                  <h2 className="text-xl font-semibold text-center text-gray-800 mb-2">
                    {document.original_filename}
                  </h2>
                  <p className="text-gray-600 text-center">
                    {document.description || 'No description'}
                  </p>
                </div>
                
                <div className="space-y-2 text-sm text-gray-600 mb-8">
                  <p>Shared by: {document.shared_by}</p>
                  <p>Created: {formatDate(document.created_at)}</p>
                </div>
                
                <div className="flex justify-center">
                  <button
                    onClick={handleDownload}
                    className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    Download Document
                  </button>
                </div>
              </div>
            ) : (
              <div className="text-center text-gray-500">
                No document information available
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
