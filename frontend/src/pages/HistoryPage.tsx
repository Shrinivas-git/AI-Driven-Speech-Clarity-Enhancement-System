import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { apiUtils } from '../utils/api';
import {
  MagnifyingGlassIcon,
  FunnelIcon,
  TrashIcon,
  ArrowDownTrayIcon,
  DocumentTextIcon,
  SpeakerWaveIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  UserIcon,
} from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

interface AudioHistoryItem {
  audio_id: number;
  original_filename: string;
  transcript_raw?: string;
  transcript_cleaned?: string;
  output_mode: string;
  processing_duration?: number;
  file_size_mb?: number;
  created_at: string;
  fluency_scores?: {
    before_score: number;
    after_score: number;
    improvement: number;
  };
  user_info?: {
    user_id: number;
    name: string;
    email: string;
  };
}

interface HistoryResponse {
  items: AudioHistoryItem[];
  total: number;
  page: number;
  per_page: number;
  has_next: boolean;
  has_prev: boolean;
}

export const HistoryPage: React.FC = () => {
  const { user } = useAuth();
  const [history, setHistory] = useState<HistoryResponse | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [selectedItems, setSelectedItems] = useState<number[]>([]);
  const [filters, setFilters] = useState({
    search: '',
    output_mode: '',
    days: '',
  });
  const [currentPage, setCurrentPage] = useState(1);
  const [showFilters, setShowFilters] = useState(false);
  
  const isAdmin = user?.role === 'admin';

  useEffect(() => {
    loadHistory();
  }, [currentPage, filters]);

  const loadHistory = async () => {
    setIsLoading(true);
    try {
      const params: any = {
        page: currentPage,
        per_page: 20,
      };

      if (filters.search) params.search = filters.search;
      if (filters.output_mode) params.output_mode = filters.output_mode;
      if (filters.days) params.days = parseInt(filters.days);

      const response = await apiUtils.getProcessingHistory(params);
      setHistory(response.data);
    } catch (error) {
      console.error('Failed to load history:', error);
      toast.error('Failed to load processing history');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault();
    setCurrentPage(1);
    loadHistory();
  };

  const handleFilterChange = (key: string, value: string) => {
    setFilters(prev => ({ ...prev, [key]: value }));
    setCurrentPage(1);
  };

  const handleSelectItem = (audioId: number) => {
    setSelectedItems(prev => 
      prev.includes(audioId) 
        ? prev.filter(id => id !== audioId)
        : [...prev, audioId]
    );
  };

  const handleSelectAll = () => {
    if (!history) return;
    
    if (selectedItems.length === history.items.length) {
      setSelectedItems([]);
    } else {
      setSelectedItems(history.items.map(item => item.audio_id));
    }
  };

  const handleDeleteSelected = async () => {
    if (selectedItems.length === 0) return;

    const confirmed = window.confirm(
      `Are you sure you want to delete ${selectedItems.length} selected item(s)?`
    );
    
    if (!confirmed) return;

    try {
      await apiUtils.bulkDeleteRecords(selectedItems);
      toast.success(`${selectedItems.length} item(s) deleted successfully`);
      setSelectedItems([]);
      loadHistory();
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Delete failed';
      toast.error(message);
    }
  };

  const handleDeleteItem = async (audioId: number) => {
    const confirmed = window.confirm('Are you sure you want to delete this item?');
    if (!confirmed) return;

    try {
      await apiUtils.deleteAudioRecord(audioId);
      toast.success('Item deleted successfully');
      loadHistory();
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Delete failed';
      toast.error(message);
    }
  };

  const downloadAudio = async (filename: string) => {
    try {
      const response = await apiUtils.downloadAudio(filename);
      const blob = response.data;
      
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = filename;
      document.body.appendChild(a);
      a.click();
      window.URL.revokeObjectURL(url);
      document.body.removeChild(a);
      
      toast.success('Audio downloaded successfully');
    } catch (error) {
      console.error('Download failed:', error);
      toast.error('Failed to download audio');
    }
  };

  if (isLoading && !history) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-2xl font-bold text-gray-900 dark:text-white">
                Processing History
                {isAdmin && (
                  <span className="ml-3 inline-flex items-center px-3 py-1 rounded-full text-sm font-medium bg-purple-100 text-purple-800 dark:bg-purple-900 dark:text-purple-200">
                    Admin View - All Users
                  </span>
                )}
              </h1>
              <p className="mt-1 text-sm text-gray-600 dark:text-gray-400">
                {isAdmin ? 'View and manage all processed audio files' : 'View and manage your processed audio files'}
              </p>
            </div>
            
            <div className="flex items-center space-x-3">
              <button
                onClick={() => setShowFilters(!showFilters)}
                className="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500"
              >
                <FunnelIcon className="h-4 w-4 mr-2" />
                Filters
              </button>
              
              {selectedItems.length > 0 && (
                <button
                  onClick={handleDeleteSelected}
                  className="inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
                >
                  <TrashIcon className="h-4 w-4 mr-2" />
                  Delete ({selectedItems.length})
                </button>
              )}
            </div>
          </div>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          {/* Search */}
          <form onSubmit={handleSearch} className="mb-4">
            <div className="relative">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <MagnifyingGlassIcon className="h-5 w-5 text-gray-400" />
              </div>
              <input
                type="text"
                placeholder="Search by filename or transcript..."
                value={filters.search}
                onChange={(e) => setFilters(prev => ({ ...prev, search: e.target.value }))}
                className="block w-full pl-10 pr-3 py-2 border border-gray-300 dark:border-gray-600 rounded-md leading-5 bg-white dark:bg-gray-700 placeholder-gray-500 dark:placeholder-gray-400 text-gray-900 dark:text-white focus:outline-none focus:placeholder-gray-400 focus:ring-1 focus:ring-primary-500 focus:border-primary-500 sm:text-sm"
              />
            </div>
          </form>

          {/* Filters */}
          {showFilters && (
            <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Output Mode
                </label>
                <select
                  value={filters.output_mode}
                  onChange={(e) => handleFilterChange('output_mode', e.target.value)}
                  className="form-input dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                >
                  <option value="">All modes</option>
                  <option value="audio">Audio only</option>
                  <option value="text">Text only</option>
                  <option value="both">Audio + Text</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-1">
                  Time Period
                </label>
                <select
                  value={filters.days}
                  onChange={(e) => handleFilterChange('days', e.target.value)}
                  className="form-input dark:bg-gray-700 dark:border-gray-600 dark:text-white"
                >
                  <option value="">All time</option>
                  <option value="1">Last 24 hours</option>
                  <option value="7">Last 7 days</option>
                  <option value="30">Last 30 days</option>
                  <option value="90">Last 90 days</option>
                </select>
              </div>

              <div className="flex items-end">
                <button
                  onClick={() => {
                    setFilters({ search: '', output_mode: '', days: '' });
                    setCurrentPage(1);
                  }}
                  className="btn-secondary"
                >
                  Clear Filters
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* History List */}
      <div className="bg-white dark:bg-gray-800 shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          {history && history.items.length > 0 ? (
            <>
              {/* Bulk Actions */}
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center">
                  <input
                    type="checkbox"
                    checked={selectedItems.length === history.items.length && history.items.length > 0}
                    onChange={handleSelectAll}
                    className="rounded border-gray-300 dark:border-gray-600 text-primary-600 focus:ring-primary-500"
                  />
                  <span className="ml-2 text-sm text-gray-700 dark:text-gray-300">
                    Select all ({history.items.length} items)
                  </span>
                </div>
                
                <div className="text-sm text-gray-500 dark:text-gray-400">
                  Showing {((currentPage - 1) * 20) + 1} to {Math.min(currentPage * 20, history.total)} of {history.total} results
                </div>
              </div>

              {/* Items */}
              <div className="space-y-4">
                {history.items.map((item) => (
                  <div
                    key={item.audio_id}
                    className={`border rounded-lg p-4 ${
                      selectedItems.includes(item.audio_id) ? 'border-primary-500 bg-primary-50 dark:bg-primary-900/20' : 'border-gray-200 dark:border-gray-700'
                    }`}
                  >
                    <div className="flex items-start justify-between">
                      <div className="flex items-start space-x-3">
                        <input
                          type="checkbox"
                          checked={selectedItems.includes(item.audio_id)}
                          onChange={() => handleSelectItem(item.audio_id)}
                          className="mt-1 rounded border-gray-300 dark:border-gray-600 text-primary-600 focus:ring-primary-500"
                        />
                        
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center space-x-2">
                            <h4 className="text-sm font-medium text-gray-900 dark:text-white truncate">
                              {item.original_filename}
                            </h4>
                            <span className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                              item.output_mode === 'both' ? 'bg-blue-100 text-blue-800' :
                              item.output_mode === 'audio' ? 'bg-green-100 text-green-800' :
                              'bg-purple-100 text-purple-800'
                            }`}>
                              {item.output_mode}
                            </span>
                          </div>
                          
                          <div className="mt-1 flex items-center space-x-4 text-xs text-gray-500 dark:text-gray-400">
                            <span>{new Date(item.created_at).toLocaleString()}</span>
                            {item.file_size_mb && (
                              <span>{item.file_size_mb.toFixed(2)} MB</span>
                            )}
                            {item.processing_duration && (
                              <span>{item.processing_duration.toFixed(1)}s processing</span>
                            )}
                          </div>

                          {/* User info for admin */}
                          {isAdmin && item.user_info && (
                            <div className="mt-2 flex items-center space-x-2 text-xs">
                              <UserIcon className="h-4 w-4 text-gray-400" />
                              <span className="text-gray-600 dark:text-gray-400">
                                <span className="font-medium">{item.user_info.name}</span>
                                <span className="text-gray-500 dark:text-gray-500"> ({item.user_info.email})</span>
                              </span>
                            </div>
                          )}

                          {item.fluency_scores && (
                            <div className="mt-2 flex items-center space-x-4 text-xs">
                              <span className="text-gray-600 dark:text-gray-400">
                                Fluency: {item.fluency_scores.before_score.toFixed(1)}% → {item.fluency_scores.after_score.toFixed(1)}%
                              </span>
                              <span className={`font-medium ${
                                item.fluency_scores.improvement > 0 ? 'text-green-600 dark:text-green-400' : 'text-gray-600 dark:text-gray-400'
                              }`}>
                                {item.fluency_scores.improvement > 0 ? '+' : ''}{item.fluency_scores.improvement.toFixed(1)}%
                              </span>
                            </div>
                          )}

                          {item.transcript_cleaned && (
                            <div className="mt-2">
                              <p className="text-xs text-gray-600 dark:text-gray-400 line-clamp-2">
                                {item.transcript_cleaned}
                              </p>
                            </div>
                          )}
                        </div>
                      </div>

                      <div className="flex items-center space-x-2 ml-4">
                        {item.output_mode !== 'text' && (
                          <button
                            onClick={() => {
                              // Extract filename from enhanced audio path or use original filename
                              const filename = `enhanced_${item.audio_id}_${item.original_filename.split('.')[0]}.wav`;
                              downloadAudio(filename);
                            }}
                            className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                            title="Download audio"
                          >
                            <ArrowDownTrayIcon className="h-4 w-4" />
                          </button>
                        )}
                        
                        <button
                          onClick={() => handleDeleteItem(item.audio_id)}
                          className="p-1 text-gray-400 hover:text-red-600 dark:hover:text-red-400"
                          title="Delete item"
                        >
                          <TrashIcon className="h-4 w-4" />
                        </button>
                      </div>
                    </div>
                  </div>
                ))}
              </div>

              {/* Pagination */}
              {history.total > 20 && (
                <div className="mt-6 flex items-center justify-between">
                  <button
                    onClick={() => setCurrentPage(prev => Math.max(1, prev - 1))}
                    disabled={!history.has_prev}
                    className="inline-flex items-center px-3 py-2 border border-gray-300 dark:border-gray-600 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    <ChevronLeftIcon className="h-4 w-4 mr-1" />
                    Previous
                  </button>
                  
                  <span className="text-sm text-gray-700 dark:text-gray-300">
                    Page {currentPage} of {Math.ceil(history.total / 20)}
                  </span>
                  
                  <button
                    onClick={() => setCurrentPage(prev => prev + 1)}
                    disabled={!history.has_next}
                    className="inline-flex items-center px-3 py-2 border border-gray-300 dark:border-gray-600 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 dark:text-gray-300 bg-white dark:bg-gray-700 hover:bg-gray-50 dark:hover:bg-gray-600 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-primary-500 disabled:opacity-50 disabled:cursor-not-allowed"
                  >
                    Next
                    <ChevronRightIcon className="h-4 w-4 ml-1" />
                  </button>
                </div>
              )}
            </>
          ) : (
            <div className="text-center py-12">
              <DocumentTextIcon className="mx-auto h-12 w-12 text-gray-400" />
              <h3 className="mt-2 text-sm font-medium text-gray-900 dark:text-white">No processing history</h3>
              <p className="mt-1 text-sm text-gray-500 dark:text-gray-400">
                {filters.search || filters.output_mode || filters.days
                  ? 'No results found for your current filters.'
                  : 'Get started by processing your first audio file.'
                }
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};