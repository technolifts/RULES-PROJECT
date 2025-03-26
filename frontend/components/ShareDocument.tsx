'use client';

import { useState } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import axios from 'axios';
import { format } from 'date-fns';

export default function ShareDocument({ document, onClose, onShareSuccess }) {
  const [expiryDays, setExpiryDays] = useState(7);
  const [sharing, setSharing] = useState(false);
  const [shareLink, setShareLink] = useState(null);
  const [error, setError] = useState(null);
  const { token } = useAuth();

  const handleShare = async () => {
    try {
      setSharing(true);
      setError(null);
      
      // Calculate expiry date
      const expiryDate = new Date();
      expiryDate.setDate(expiryDate.getDate() + parseInt(expiryDays));
      
      const response = await axios.post(
        'http://localhost:8000/shares/',
        {
          document_id: document.id,
          expires_at: expiryDate.toISOString()
        },
        {
          headers: {
            Authorization: `Bearer ${token}`
          }
        }
      );
      
      // Create the full share URL
      const shareUrl = `${window.location.origin}/shared/${response.data.token}`;
      setShareLink(shareUrl);
      
      if (onShareSuccess) {
        onShareSuccess();
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to create share link');
      console.error(err);
    } finally {
      setSharing(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(shareLink);
  };

  return (
    <div className="fixed inset-0 bg-gray-600 bg-opacity-50 overflow-y-auto h-full w-full flex items-center justify-center z-50">
      <div className="relative bg-white rounded-lg shadow-xl max-w-md w-full mx-4">
        <div className="p-6">
          <div className="flex justify-between items-center mb-4">
            <h3 className="text-lg font-medium text-gray-900">Share Document</h3>
            <button
              type="button"
              className="text-gray-400 hover:text-gray-500"
              onClick={onClose}
            >
              <span className="sr-only">Close</span>
              <svg className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
          
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded relative mb-4" role="alert">
              <span className="block sm:inline">{error}</span>
            </div>
          )}
          
          <div className="mb-4">
            <p className="text-sm text-gray-600 mb-2">
              You are sharing: <span className="font-semibold">{document.original_filename}</span>
            </p>
          </div>
          
          {!shareLink ? (
            <>
              <div className="mb-4">
                <label htmlFor="expiryDays" className="block text-sm font-medium text-gray-700 mb-2">
                  Link expires after (days)
                </label>
                <select
                  id="expiryDays"
                  className="mt-1 block w-full pl-3 pr-10 py-2 text-base border-gray-300 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm rounded-md"
                  value={expiryDays}
                  onChange={(e) => setExpiryDays(parseInt(e.target.value))}
                >
                  <option value="1">1 day</option>
                  <option value="7">7 days</option>
                  <option value="30">30 days</option>
                  <option value="90">90 days</option>
                </select>
              </div>
              
              <div className="flex justify-end space-x-3">
                <button
                  type="button"
                  className="inline-flex justify-center py-2 px-4 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  onClick={onClose}
                >
                  Cancel
                </button>
                <button
                  type="button"
                  disabled={sharing}
                  className="inline-flex justify-center py-2 px-4 border border-transparent shadow-sm text-sm font-medium rounded-md text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:opacity-50"
                  onClick={handleShare}
                >
                  {sharing ? 'Creating link...' : 'Create Share Link'}
                </button>
              </div>
            </>
          ) : (
            <>
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  Share Link
                </label>
                <div className="flex">
                  <input
                    type="text"
                    readOnly
                    value={shareLink}
                    className="flex-grow shadow-sm focus:ring-blue-500 focus:border-blue-500 block w-full sm:text-sm border-gray-300 rounded-md"
                  />
                  <button
                    type="button"
                    onClick={copyToClipboard}
                    className="ml-2 inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md shadow-sm text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  >
                    Copy
                  </button>
                </div>
                <p className="mt-2 text-sm text-gray-500">
                  This link will expire on {format(new Date(new Date().setDate(new Date().getDate() + parseInt(expiryDays))), 'PPP')}
                </p>
              </div>
              
              <div className="flex justify-end">
                <button
                  type="button"
                  className="inline-flex justify-center py-2 px-4 border border-gray-300 shadow-sm text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
                  onClick={onClose}
                >
                  Close
                </button>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
