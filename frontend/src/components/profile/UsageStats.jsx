import { useState, useEffect } from 'react';
import { MessageSquare, FileText, User as UserIcon, Clock } from 'lucide-react';
import { getQueryStats } from '../../services/chatService';
import { formatRelativeTime } from '../../utils/formatters';
import Loader from '../common/Loader';

const UsageStats = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  
  useEffect(() => {
    fetchStats();
  }, []);
  
  const fetchStats = async () => {
    try {
      const data = await getQueryStats();
      setStats(data);
    } catch (err) {
      console.error('Failed to fetch stats:', err);
    } finally {
      setLoading(false);
    }
  };
  
  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">Usage Statistics</h2>
        <Loader />
      </div>
    );
  }
  
  const statCards = [
    {
      icon: MessageSquare,
      label: 'Total Questions Asked',
      value: stats?.total_queries || 0,
      color: 'text-blue-600',
      bgColor: 'bg-blue-100',
    },
    {
      icon: FileText,
      label: 'Documents Analyzed',
      value: stats?.unique_documents || 0,
      color: 'text-green-600',
      bgColor: 'bg-green-100',
    },
    {
      icon: UserIcon,
      label: 'Conversations',
      value: stats?.unique_sessions || 0,
      color: 'text-purple-600',
      bgColor: 'bg-purple-100',
    },
    {
      icon: Clock,
      label: 'Last Activity',
      value: stats?.last_query_time ? formatRelativeTime(stats.last_query_time) : 'Never',
      color: 'text-orange-600',
      bgColor: 'bg-orange-100',
    },
  ];
  
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h2 className="text-xl font-semibold text-gray-900 mb-6">Usage Statistics</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        {statCards.map((stat, index) => (
          <div
            key={index}
            className="p-4 border border-gray-200 rounded-lg hover:shadow-md transition-shadow"
          >
            <div className="flex items-center gap-3">
              <div className={`p-3 rounded-lg ${stat.bgColor}`}>
                <stat.icon className={stat.color} size={24} />
              </div>
              <div>
                <p className="text-sm text-gray-600">{stat.label}</p>
                <p className="text-2xl font-bold text-gray-900">{stat.value}</p>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default UsageStats;
