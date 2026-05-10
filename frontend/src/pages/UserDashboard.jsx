import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import Layout from '../components/Layout/Layout';
import CredentialsList from '../components/Wallet/CredentialsList';
import ProofGenerator from '../components/Proofs/ProofGenerator';
import ConsentHistory from '../components/Consent/ConsentHistory';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title } from 'chart.js';
import { Doughnut, Bar } from 'react-chartjs-2';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title);

export default function UserDashboard() {
  const { api } = useAuth();
  const [stats, setStats] = useState({ credentials: 0, proofs: 0, consents: 0 });
  const [recentActivity, setRecentActivity] = useState([]);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [creds, proofs, consents, logs] = await Promise.all([
        api.get('/wallet/credentials'),
        api.get('/wallet/proofs'),
        api.get('/consent/history'),
        api.get('/wallet/audit')
      ]);
      setStats({
        credentials: creds.data.length,
        proofs: proofs.data.length,
        consents: consents.data.length
      });
      setRecentActivity(logs.data.slice(0, 5));
    } catch (error) {
      console.error('Failed to fetch dashboard data:', error);
    }
  };

  const chartData = {
    labels: ['Active', 'Expired', 'Revoked'],
    datasets: [{
      data: [stats.credentials, 0, 0],
      backgroundColor: ['#10B981', '#F59E0B', '#EF4444']
    }]
  };

  return (
    <Layout>
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-8">User Dashboard</h1>
        
        {/* Stats */}
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-500">Credentials</h3>
            <p className="text-3xl font-bold text-gray-900">{stats.credentials}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-500">Proofs Generated</h3>
            <p className="text-3xl font-bold text-gray-900">{stats.proofs}</p>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-500">Consent Records</h3>
            <p className="text-3xl font-bold text-gray-900">{stats.consents}</p>
          </div>
        </div>
        
        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8 mb-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Credential Status</h3>
            <div className="w-64 mx-auto">
              <Doughnut data={chartData} />
            </div>
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-lg font-medium text-gray-900 mb-4">Recent Activity</h3>
            <div className="space-y-3">
              {recentActivity.map((activity, idx) => (
                <div key={idx} className="flex justify-between items-center border-b pb-2">
                  <span className="text-sm text-gray-600">{activity.event_type}</span>
                  <span className="text-xs text-gray-400">{new Date(activity.timestamp).toLocaleString()}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
        
        {/* Main sections */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">My Credentials</h3>
            <CredentialsList />
          </div>
          <div className="bg-white rounded-lg shadow p-6">
            <h3 className="text-xl font-bold text-gray-900 mb-4">Generate Zero-Knowledge Proof</h3>
            <ProofGenerator />
          </div>
        </div>
        
        <div className="mt-8 bg-white rounded-lg shadow p-6">
          <h3 className="text-xl font-bold text-gray-900 mb-4">Consent History</h3>
          <ConsentHistory />
        </div>
      </div>
    </Layout>
  );
}