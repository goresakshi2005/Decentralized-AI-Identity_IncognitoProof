import React, { useState, useEffect } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import { EyeIcon, ShieldCheckIcon, XCircleIcon } from '@heroicons/react/24/outline';

export default function CredentialsList() {
  const { api } = useAuth();
  const [credentials, setCredentials] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchCredentials();
  }, []);

  const fetchCredentials = async () => {
    try {
      const response = await api.get('/wallet/credentials');
      setCredentials(response.data);
    } catch (error) {
      console.error('Failed to fetch credentials:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status) => {
    const styles = {
      active: 'bg-green-100 text-green-800',
      revoked: 'bg-red-100 text-red-800',
      expired: 'bg-yellow-100 text-yellow-800'
    };
    return styles[status] || 'bg-gray-100 text-gray-800';
  };

  if (loading) return <div className="text-center py-4">Loading credentials...</div>;

  return (
    <div className="space-y-4">
      {credentials.length === 0 ? (
        <p className="text-gray-500 text-center py-4">No credentials yet</p>
      ) : (
        credentials.map((cred) => (
          <div key={cred.credential_id} className="border rounded-lg p-4 hover:shadow-md transition">
            <div className="flex justify-between items-start">
              <div>
                <h4 className="font-semibold text-gray-900 capitalize">{cred.claim_type.replace('_', ' ')}</h4>
                <p className="text-sm text-gray-500">Issued: {new Date(cred.issued_date).toLocaleDateString()}</p>
                <p className="text-sm text-gray-500">Expires: {new Date(cred.expiry_date).toLocaleDateString()}</p>
                {cred.blockchain_hash && (
                  <p className="text-xs text-gray-400 truncate">Tx: {cred.blockchain_hash.slice(0, 20)}...</p>
                )}
              </div>
              <div className="flex items-center space-x-2">
                <span className={`px-2 py-1 rounded-full text-xs font-medium ${getStatusBadge(cred.status)}`}>
                  {cred.status}
                </span>
                {cred.status === 'active' && <ShieldCheckIcon className="h-5 w-5 text-green-500" />}
                {cred.status === 'revoked' && <XCircleIcon className="h-5 w-5 text-red-500" />}
              </div>
            </div>
          </div>
        ))
      )}
    </div>
  );
}