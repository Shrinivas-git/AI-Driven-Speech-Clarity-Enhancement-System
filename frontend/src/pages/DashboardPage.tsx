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
  ArrowDownIcon,
  PlayIcon,
  SparklesIcon,
  BoltIcon,
  TrophyIcon,
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
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  const stats = [
    {
      name: 'Total Processed',
      value: dashboardData?.statistics?.total_processed_files || 0,
      icon: DocumentTextIcon,
      change: '+12%',
      changeType: 'increase',
      bgColor: 'from-blue-500 to-blue-600',
    },
    {
      name: 'Usage Remaining',
      value: usageInfo?.is_premium ? '∞' : `${usageInfo?.remaining_uses || 0}`,
      icon: ChartBarIcon,
      change: usageInfo?.is_premium ? 'Premium' : 'Free',
      changeType: usageInfo?.is_premium ? 'neutral' : 'decrease',
      bgColor: 'from-indigo-500 to-indigo-600',
    },
    {
      name: 'Avg Improvement',
      value: `${dashboardData?.statistics?.average_improvement_score?.toFixed(1) || 0}%`,
      icon: TrophyIcon,
      change: '+2.1%',
      changeType: 'increase',
      bgColor: 'from-green-500 to-green-600',
    },
    {
      name: 'Processing Time',
      value: `${dashboardData?.statistics?.total_processing_time?.toFixed(1) || 0}s`,
      icon: BoltIcon,
      change: '-5%',
      changeType: 'decrease',
      bgColor: 'from-purple-500 to-purple-600',
    },
  ];

  return (
    <div className="space-y-6">
      {/* Welcome Section with Gradient */}
      <div className="relative overflow-hidden bg-gradient-to-br from-blue-600 to-indigo-600 rounded-2xl shadow-xl">
        <div className="absolute inset-0 bg-grid-white/10"></div>
        <div className="relative px-6 py-8 sm:px-8">
          <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between">
            <div className="mb-4 sm:mb-0">
              <div className="flex items-center space-x-2 mb-2">
                <SparklesIcon className="h-6 w-6 text-white" />
                <h1 className="text-3xl font-bold text-white">
                  Welcome back, {user?.name}!
                </h1>
              </div>
              <p className="text-blue-100 text-lg">
                Here's your speech enhancement overview
              </p>
            </div>
            <Link
              to="/app/process"
              className="inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-xl text-blue-600 bg-white hover:bg-blue-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-white shadow-lg transform hover:-translate-y-0.5 transition-all"
            >
              <SpeakerWaveIcon className="h-5 w-5 mr-2" />
              Process Audio
            </Link>
          </div>
        </div>
        <div className="absolute bottom-0 right-0 w-64 h-64 bg-white/5 rounded-full blur-3xl"></div>
      </div>

      {/* Usage Alert */}
      {usageInfo && !usageInfo.is_premium && usageInfo.remaining_uses <= 3 && (
        <div className="bg-gradient-to-r from-yellow-50 to-orange-50 border-l-4 border-yellow-400 rounded-lg p-4 shadow-sm">
          <div className="flex">
            <div className="flex-shrink-0">
              <ChartBarIcon className="h-6 w-6 text-yellow-600" />
            </div>
            <div className="ml-3">
              <h3 className="text-sm font-semibold text-yellow-800">
                Usage Limit Warning
              </h3>
              <div className="mt-2 text-sm text-yellow-700">
                <p>
                  You have <span className="font-bold">{usageInfo.remaining_uses}</span> free uses remaining.{' '}
                  <Link to="/app/subscription" className="font-semibold underline hover:text-yellow-900">
                    Upgrade to premium
                  </Link>{' '}
                  for unlimited usage.
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Stats Grid - Modern Cards */}
      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-4">
        {stats.map((item) => {
          const Icon = item.icon;
          return (
            <div key={item.name} className="relative group">
              <div className="absolute inset-0 bg-gradient-to-r opacity-0 group-hover:opacity-100 transition-opacity rounded-2xl blur-xl" 
                   style={{ background: `linear-gradient(to right, var(--tw-gradient-stops))` }}></div>
              <div className="relative bg-white overflow-hidden shadow-lg rounded-2xl hover:shadow-xl transition-all transform hover:-translate-y-1">
                <div className="p-6">
                  <div className="flex items-center justify-between mb-4">
                    <div className={`p-3 rounded-xl bg-gradient-to-br ${item.bgColor} shadow-lg`}>
                      <Icon className="h-6 w-6 text-white" />
                    </div>
                    <div
                      className={`flex items-center text-sm font-semibold ${
                        item.changeType === 'increase'
                          ? 'text-green-600'
                          : item.changeType === 'decrease'
                          ? 'text-red-600'
                          : 'text-gray-600'
                      }`}
                    >
                      {item.changeType === 'increase' && (
                        <ArrowUpIcon className="h-4 w-4 mr-1" />
                      )}
                      {item.changeType === 'decrease' && (
                        <ArrowDownIcon className="h-4 w-4 mr-1" />
                      )}
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
              </div>
            </div>
          );
        })}
      </div>

      {/* Recent Activity - Modern Design */}
      <div className="bg-white shadow-lg rounded-2xl overflow-hidden">
        <div className="px-6 py-5 border-b border-gray-100">
          <div className="flex items-center justify-between">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <ClockIcon className="h-5 w-5 text-blue-600" />
              </div>
              <h3 className="text-xl font-bold text-gray-900">
                Recent Activity
              </h3>
            </div>
            <Link
              to="/app/history"
              className="text-sm font-semibold text-blue-600 hover:text-blue-700 transition-colors"
            >
              View all →
            </Link>
          </div>
        </div>
        
        <div className="px-6 py-4">
          {dashboardData?.recent_activity?.length > 0 ? (
            <div className="space-y-4">
              {dashboardData.recent_activity.slice(0, 5).map((activity, activityIdx) => (
                <div key={activity.audio_id} className="flex items-center space-x-4 p-4 rounded-xl hover:bg-gray-50 transition-colors">
                  <div className={`flex-shrink-0 w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-500 flex items-center justify-center shadow-lg`}>
                    <SpeakerWaveIcon className="h-6 w-6 text-white" />
                  </div>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-semibold text-gray-900 truncate">
                      {activity.original_filename}
                    </p>
                    <div className="flex items-center space-x-4 mt-1">
                      {activity.fluency_scores && (
                        <span className="inline-flex items-center text-xs font-medium text-green-600">
                          <ArrowUpIcon className="h-3 w-3 mr-1" />
                          +{activity.fluency_scores.improvement?.toFixed(1)}% improvement
                        </span>
                      )}
                      <span className="text-xs text-gray-500">
                        {new Date(activity.created_at).toLocaleDateString()}
                      </span>
                    </div>
                  </div>
                  <div>
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      Completed
                    </span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-12">
              <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 mb-4">
                <SpeakerWaveIcon className="h-8 w-8 text-gray-400" />
              </div>
              <h3 className="text-lg font-semibold text-gray-900 mb-2">No activity yet</h3>
              <p className="text-sm text-gray-500 mb-6">
                Get started by processing your first audio file.
              </p>
              <Link
                to="/app/process"
                className="inline-flex items-center px-6 py-3 border border-transparent text-sm font-medium rounded-xl text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 shadow-lg transform hover:-translate-y-0.5 transition-all"
              >
                <PlayIcon className="h-4 w-4 mr-2" />
                Process Audio
              </Link>
            </div>
          )}
        </div>
      </div>

      {/* Quick Actions - Modern Cards */}
      <div className="bg-white shadow-lg rounded-2xl overflow-hidden">
        <div className="px-6 py-5 border-b border-gray-100">
          <div className="flex items-center space-x-3">
            <div className="p-2 bg-indigo-100 rounded-lg">
              <BoltIcon className="h-5 w-5 text-indigo-600" />
            </div>
            <h3 className="text-xl font-bold text-gray-900">
              Quick Actions
            </h3>
          </div>
        </div>
        <div className="p-6">
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <Link
              to="/app/process"
              className="group relative bg-gradient-to-br from-blue-50 to-indigo-50 p-6 rounded-2xl border-2 border-blue-100 hover:border-blue-300 hover:shadow-lg transition-all transform hover:-translate-y-1"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-gradient-to-br from-blue-500 to-indigo-500 rounded-xl shadow-lg">
                  <SpeakerWaveIcon className="h-6 w-6 text-white" />
                </div>
                <ArrowUpIcon className="h-5 w-5 text-blue-600 transform group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">
                Process Audio
              </h3>
              <p className="text-sm text-gray-600">
                Upload and enhance your speech recordings
              </p>
            </Link>

            <Link
              to="/app/history"
              className="group relative bg-gradient-to-br from-purple-50 to-pink-50 p-6 rounded-2xl border-2 border-purple-100 hover:border-purple-300 hover:shadow-lg transition-all transform hover:-translate-y-1"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-gradient-to-br from-purple-500 to-pink-500 rounded-xl shadow-lg">
                  <ClockIcon className="h-6 w-6 text-white" />
                </div>
                <ArrowUpIcon className="h-5 w-5 text-purple-600 transform group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">
                View History
              </h3>
              <p className="text-sm text-gray-600">
                Browse your processed audio files
              </p>
            </Link>

            <Link
              to="/app/subscription"
              className="group relative bg-gradient-to-br from-green-50 to-emerald-50 p-6 rounded-2xl border-2 border-green-100 hover:border-green-300 hover:shadow-lg transition-all transform hover:-translate-y-1"
            >
              <div className="flex items-center justify-between mb-4">
                <div className="p-3 bg-gradient-to-br from-green-500 to-emerald-500 rounded-xl shadow-lg">
                  <ChartBarIcon className="h-6 w-6 text-white" />
                </div>
                <ArrowUpIcon className="h-5 w-5 text-green-600 transform group-hover:translate-x-1 group-hover:-translate-y-1 transition-transform" />
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">
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