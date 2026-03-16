import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { apiUtils } from '../utils/api';
import {
  ChartBarIcon,
  ClockIcon,
  DocumentTextIcon,
  SpeakerWaveIcon,
  ArrowUpIcon,
  PlayIcon,
  BoltIcon,
  TrophyIcon,
  ExclamationTriangleIcon,
  ArrowTrendingUpIcon,
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

interface DashboardData {
  user_info: any;
  usage_info: any;
  subscription_info: any;
  recent_activity: any[];
  statistics: any;
}

export const DashboardPage: React.FC = () => {
  const { user, usageInfo } = useAuth();
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      const response = await apiUtils.getDashboardOverview();
      setDashboardData(response.data);
    } catch (error) {
      console.error('Failed to load dashboard data:', error);
      toast.error('Failed to load dashboard data');
    } finally {
      setIsLoading(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="spinner"></div>
        <span className="ml-3 text-gray-600">Loading dashboard...</span>
      </div>
    );
  }

  const stats = [
    {
      name: 'Total Processed',
      value: dashboardData?.statistics?.total_processed_files || 0,
      icon: DocumentTextIcon,
      change: '+12%',
      bgColor: 'bg-blue-50',
      iconColor: 'text-blue-600',
      borderColor: 'border-blue-100',
    },
    {
      name: 'Usage Remaining',
      value: usageInfo?.is_premium ? '∞' : `${usageInfo?.remaining_uses || 0}`,
      icon: ChartBarIcon,
      change: usageInfo?.is_premium ? 'Premium' : 'Free',
      bgColor: 'bg-purple-50',
      iconColor: 'text-purple-600',
      borderColor: 'border-purple-100',
    },
    {
      name: 'Avg Improvement',
      value: `${dashboardData?.statistics?.average_improvement_score?.toFixed(1) || 0}%`,
      icon: TrophyIcon,
      change: '+2.1%',
      bgColor: 'bg-green-50',
      iconColor: 'text-green-600',
      borderColor: 'border-green-100',
    },
    {
      name: 'Processing Time',
      value: `${dashboardData?.statistics?.total_processing_time?.toFixed(1) || 0}s`,
      icon: BoltIcon,
      change: '-5%',
      bgColor: 'bg-orange-50',
      iconColor: 'text-orange-600',
      borderColor: 'border-orange-100',
    },
  ];

  return (
    <div className="space-y-8 fade-in">
      {/* Welcome Section */}
      <div className="grid lg:grid-cols-2 gap-8 items-center py-8">
        <div className="text-center lg:text-left">
          <h1 className="text-5xl font-bold text-gray-900 mb-4">
            Welcome back, {user?.name}
          </h1>
          <p className="text-xl text-gray-600 mb-8">
            Extract crystal-clear speech from any audio
          </p>
          <Link
            to="/app/process"
            className="btn-primary inline-flex items-center gap-2"
          >
            <SpeakerWaveIcon className="w-5 h-5" />
            Process Audio
          </Link>
        </div>
        
        {/* Dashboard Image */}
        <div className="relative">
          <div className="bg-white rounded-2xl p-6 shadow-xl border border-gray-100">
            <img 
              src="/pic1.png" 
              alt="Speech Enhancement Dashboard" 
              className="w-full h-auto rounded-xl object-contain"
              style={{ maxHeight: '400px' }}
            />
          </div>
          <div className="absolute -bottom-4 -right-4 w-32 h-32 bg-gradient-to-br from-blue-400 to-indigo-400 rounded-full opacity-20 blur-2xl"></div>
          <div className="absolute -top-4 -left-4 w-32 h-32 bg-gradient-to-br from-indigo-400 to-purple-400 rounded-full opacity-20 blur-2xl"></div>
        </div>
      </div>

      {/* Usage Alert */}
      {usageInfo && !usageInfo.is_premium && usageInfo.remaining_uses <= 3 && (
        <div className="card p-5 border-l-4 border-yellow-400 slide-up">
          <div className="flex items-start gap-3">
            <ExclamationTriangleIcon className="w-6 h-6 text-yellow-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <h3 className="text-sm font-semibold text-gray-900 mb-1">
                Usage Limit Warning
              </h3>
              <p className="text-sm text-gray-600">
                You have <span className="font-semibold text-gray-900">{usageInfo.remaining_uses}</span> free uses remaining.{' '}
                <Link to="/app/subscription" className="text-blue-600 hover:text-blue-700 underline font-medium">
                  Upgrade to premium
                </Link>{' '}
                for unlimited usage.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Stats Grid */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((item, index) => {
          const Icon = item.icon;
          return (
            <div 
              key={item.name} 
              className={`stat-card border ${item.borderColor} scale-in`}
              style={{ animationDelay: `${index * 0.1}s` }}
            >
              <div className="flex items-center justify-between mb-4">
                <div className={`w-12 h-12 rounded-xl ${item.bgColor} flex items-center justify-center`}>
                  <Icon className={`w-6 h-6 ${item.iconColor}`} />
                </div>
                <div className="flex items-center gap-1 text-sm font-medium text-green-600">
                  <ArrowTrendingUpIcon className="w-4 h-4" />
                  {item.change}
                </div>
              </div>
              <div>
                <p className="text-sm font-medium text-gray-600 mb-1">
                  {item.name}
                </p>
                <p className="text-3xl font-bold text-gray-900">
                  {item.value}
                </p>
              </div>
            </div>
          );
        })}
      </div>

      {/* Recent Activity */}
      <div className="card overflow-hidden">
        <div className="px-6 py-5 border-b border-gray-100">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <ClockIcon className="w-6 h-6 text-gray-600" />
              <h3 className="text-xl font-semibold text-gray-900">
                Recent Activity
              </h3>
            </div>
            <Link
              to="/app/history"
              className="text-sm font-medium text-gray-600 hover:text-gray-900 transition-colors"
            >
              View all →
            </Link>
          </div>
        </div>
        
        <div className="p-6">
          {dashboardData?.recent_activity?.length > 0 ? (
            <div className="space-y-3">
              {dashboardData.recent_activity.slice(0, 5).map((activity) => (
                <div 
                  key={activity.audio_id} 
                  className="flex items-center gap-4 p-4 rounded-xl bg-gray-50 hover:bg-gray-100 border border-gray-100 transition-colors"
                >
                  <div className="flex-shrink-0 w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-purple-500 flex items-center justify-center shadow-sm">
                    <SpeakerWaveIcon className="w-6 h-6 text-white" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-gray-900 truncate">
                      {activity.original_filename}
                    </p>
                    <div className="flex items-center gap-4 mt-1">
                      {activity.fluency_scores && (
                        <span className="inline-flex items-center text-xs font-medium text-green-600">
                          <ArrowUpIcon className="w-3 h-3 mr-1" />
                          +{activity.fluency_scores.improvement?.toFixed(1)}% improvement
                        </span>
                      )}
                      <span className="text-xs text-gray-500">
                        {new Date(activity.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                  <div>
                    <span className="badge-success">
                      Completed
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-16">
              <div className="inline-flex items-center justify-center w-20 h-20 rounded-full bg-gray-100 mb-4">
                <SpeakerWaveIcon className="w-10 h-10 text-gray-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No activity yet</h3>
              <p className="text-sm text-gray-600 mb-6">
                Get started by processing your first audio file.
              </p>
              <Link
                to="/app/process"
                className="btn-primary inline-flex items-center gap-2"
              >
                <PlayIcon className="w-5 h-5" />
                Process Audio
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions */}
      <div className="card overflow-hidden">
        <div className="px-6 py-5 border-b border-gray-100">
          <div className="flex items-center gap-3">
            <BoltIcon className="w-6 h-6 text-gray-600" />
            <h3 className="text-xl font-semibold text-gray-900">
              Quick Actions
            </h3>
          </div>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <Link
              to="/app/process"
              className="card p-6 hover:shadow-md transition-all group"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-xl bg-blue-50 flex items-center justify-center border border-blue-100">
                  <SpeakerWaveIcon className="w-6 h-6 text-blue-600" />
                </div>
                <ArrowUpIcon className="w-5 h-5 text-gray-400 group-hover:text-blue-600 transition-colors rotate-45" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Process Audio
              </h3>
              <p className="text-sm text-gray-600">
                Upload and enhance your speech recordings
              </p>
            </Link>

            <Link
              to="/app/history"
              className="card p-6 hover:shadow-md transition-all group"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-xl bg-purple-50 flex items-center justify-center border border-purple-100">
                  <ClockIcon className="w-6 h-6 text-purple-600" />
                </div>
                <ArrowUpIcon className="w-5 h-5 text-gray-400 group-hover:text-purple-600 transition-colors rotate-45" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                View History
              </h3>
              <p className="text-sm text-gray-600">
                Browse your processed audio files
              </p>
            </Link>

            <Link
              to="/app/subscription"
              className="card p-6 hover:shadow-md transition-all group"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="w-12 h-12 rounded-xl bg-green-50 flex items-center justify-center border border-green-100">
                  <ChartBarIcon className="w-6 h-6 text-green-600" />
                </div>
                <ArrowUpIcon className="w-5 h-5 text-gray-400 group-hover:text-green-600 transition-colors rotate-45" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">
                Manage Subscription
              </h3>
              <p className="text-sm text-gray-600">
                Upgrade to premium for unlimited usage
              </p>
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
};
