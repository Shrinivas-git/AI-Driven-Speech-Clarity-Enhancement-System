import React, { useState, useEffect } from 'react';
import { useAuth } from '../contexts/AuthContext';
import { apiUtils } from '../utils/api';
import { CheckIcon, XMarkIcon } from '@heroicons/react/24/outline';
import toast from 'react-hot-toast';

interface PricingPlan {
  plan_type: string;
  name: string;
  price: number;
  currency: string;
  duration: string;
  features: string[];
  limitations: string[];
  is_popular: boolean;
}

interface SubscriptionInfo {
  subscription_id: number;
  plan_type: string;
  start_date: string;
  end_date?: string;
  is_active: boolean;
  amount: number;
  currency: string;
}

export const SubscriptionPage: React.FC = () => {
  const { usageInfo, refreshUsage } = useAuth();
  const [pricingPlans, setPricingPlans] = useState<PricingPlan[]>([]);
  const [currentSubscription, setCurrentSubscription] = useState<SubscriptionInfo | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isProcessing, setIsProcessing] = useState(false);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      // Load pricing plans
      const pricingResponse = await apiUtils.getPricing();
      setPricingPlans(pricingResponse.data.plans);

      // Load current subscription
      try {
        const subscriptionResponse = await apiUtils.getUserSubscription();
        setCurrentSubscription(subscriptionResponse.data);
      } catch (error: any) {
        // No active subscription is fine
        if (error.response?.status !== 404) {
          console.error('Failed to load subscription:', error);
        }
      }
    } catch (error) {
      console.error('Failed to load pricing data:', error);
      toast.error('Failed to load pricing information');
    } finally {
      setIsLoading(false);
    }
  };

  const handleSubscribe = async (planType: string) => {
    if (planType === 'free') {
      toast.error('You are already on the free plan');
      return;
    }

    setIsProcessing(true);
    try {
      const durationMonths = planType === 'yearly_premium' ? 12 : 1;
      await apiUtils.createSubscription(planType, durationMonths);
      
      toast.success('Subscription created successfully! (Simulated payment)');
      
      // Refresh data
      await loadData();
      await refreshUsage();
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Subscription failed';
      toast.error(message);
    } finally {
      setIsProcessing(false);
    }
  };

  const handleCancelSubscription = async () => {
    if (!currentSubscription) return;

    const confirmed = window.confirm(
      'Are you sure you want to cancel your subscription? You will lose premium benefits.'
    );
    
    if (!confirmed) return;

    setIsProcessing(true);
    try {
      await apiUtils.cancelSubscription();
      toast.success('Subscription cancelled successfully');
      
      // Refresh data
      await loadData();
      await refreshUsage();
    } catch (error: any) {
      const message = error.response?.data?.detail || 'Cancellation failed';
      toast.error(message);
    } finally {
      setIsProcessing(false);
    }
  };

  if (isLoading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-primary-600"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h1 className="text-2xl font-bold text-gray-900">Subscription Management</h1>
          <p className="mt-1 text-sm text-gray-600">
            Manage your subscription and upgrade for unlimited speech enhancement
          </p>
        </div>
      </div>

      {/* Current Status */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Current Status</h3>
          
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-3">
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-sm text-gray-600">Plan</div>
              <div className="text-lg font-semibold text-gray-900">
                {usageInfo?.is_premium ? 'Premium' : 'Free'}
              </div>
            </div>
            
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-sm text-gray-600">Usage</div>
              <div className="text-lg font-semibold text-gray-900">
                {usageInfo?.is_premium ? 'Unlimited' : `${usageInfo?.remaining_uses || 0} remaining`}
              </div>
            </div>
            
            <div className="bg-gray-50 rounded-lg p-4">
              <div className="text-sm text-gray-600">Status</div>
              <div className="text-lg font-semibold text-gray-900">
                {currentSubscription?.is_active ? 'Active' : 'Inactive'}
              </div>
            </div>
          </div>

          {currentSubscription && (
            <div className="mt-4 p-4 bg-blue-50 border border-blue-200 rounded-md">
              <div className="flex items-center justify-between">
                <div>
                  <h4 className="text-sm font-medium text-blue-800">
                    Current Subscription: {currentSubscription.plan_type.replace('_', ' ').toUpperCase()}
                  </h4>
                  <p className="text-sm text-blue-700">
                    Started: {new Date(currentSubscription.start_date).toLocaleDateString()}
                    {currentSubscription.end_date && (
                      <span> • Expires: {new Date(currentSubscription.end_date).toLocaleDateString()}</span>
                    )}
                  </p>
                </div>
                <button
                  onClick={handleCancelSubscription}
                  disabled={isProcessing}
                  className="text-sm text-red-600 hover:text-red-500 disabled:opacity-50"
                >
                  Cancel Subscription
                </button>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Pricing Plans */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <div className="text-center mb-8">
            <h3 className="text-2xl font-bold text-gray-900">Choose Your Plan</h3>
            <p className="mt-2 text-gray-600">
              Upgrade to premium for unlimited speech enhancement
            </p>
            <div className="mt-4 p-3 bg-yellow-50 border border-yellow-200 rounded-md">
              <p className="text-sm text-yellow-800">
                <strong>Note:</strong> This is a simulated payment system for academic demonstration purposes only.
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-6 lg:grid-cols-3">
            {pricingPlans.map((plan) => (
              <div
                key={plan.plan_type}
                className={`relative rounded-lg border ${
                  plan.is_popular
                    ? 'border-primary-500 shadow-lg'
                    : 'border-gray-200'
                } bg-white p-6`}
              >
                {plan.is_popular && (
                  <div className="absolute -top-3 left-1/2 transform -translate-x-1/2">
                    <span className="inline-flex items-center px-3 py-1 rounded-full text-xs font-medium bg-primary-500 text-white">
                      Most Popular
                    </span>
                  </div>
                )}

                <div className="text-center">
                  <h4 className="text-lg font-semibold text-gray-900">{plan.name}</h4>
                  <div className="mt-4">
                    <span className="text-4xl font-bold text-gray-900">
                      ${plan.price}
                    </span>
                    <span className="text-gray-600">/{plan.duration.toLowerCase()}</span>
                  </div>
                </div>

                <ul className="mt-6 space-y-3">
                  {plan.features.map((feature, index) => (
                    <li key={index} className="flex items-start">
                      <CheckIcon className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
                      <span className="ml-2 text-sm text-gray-700">{feature}</span>
                    </li>
                  ))}
                  {plan.limitations.map((limitation, index) => (
                    <li key={index} className="flex items-start">
                      <XMarkIcon className="h-5 w-5 text-red-500 flex-shrink-0 mt-0.5" />
                      <span className="ml-2 text-sm text-gray-500">{limitation}</span>
                    </li>
                  ))}
                </ul>

                <div className="mt-8">
                  {plan.plan_type === 'free' ? (
                    <div className="text-center">
                      <span className="text-sm text-gray-500">Current Plan</span>
                    </div>
                  ) : currentSubscription?.plan_type === plan.plan_type ? (
                    <div className="text-center">
                      <span className="text-sm text-green-600 font-medium">Active Plan</span>
                    </div>
                  ) : (
                    <button
                      onClick={() => handleSubscribe(plan.plan_type)}
                      disabled={isProcessing}
                      className={`w-full py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white ${
                        plan.is_popular
                          ? 'bg-primary-600 hover:bg-primary-700 focus:ring-primary-500'
                          : 'bg-gray-600 hover:bg-gray-700 focus:ring-gray-500'
                      } focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed`}
                    >
                      {isProcessing ? (
                        <div className="flex items-center justify-center">
                          <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                          Processing...
                        </div>
                      ) : (
                        `Subscribe to ${plan.name}`
                      )}
                    </button>
                  )}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* FAQ */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-4 py-5 sm:p-6">
          <h3 className="text-lg font-medium text-gray-900 mb-4">Frequently Asked Questions</h3>
          
          <div className="space-y-4">
            <div>
              <h4 className="text-sm font-medium text-gray-900">What happens when I upgrade to premium?</h4>
              <p className="mt-1 text-sm text-gray-600">
                You get unlimited speech enhancements, priority processing, and access to advanced features.
              </p>
            </div>
            
            <div>
              <h4 className="text-sm font-medium text-gray-900">Can I cancel my subscription anytime?</h4>
              <p className="mt-1 text-sm text-gray-600">
                Yes, you can cancel your subscription at any time. You'll continue to have premium access until the end of your billing period.
              </p>
            </div>
            
            <div>
              <h4 className="text-sm font-medium text-gray-900">Is this a real payment system?</h4>
              <p className="mt-1 text-sm text-gray-600">
                No, this is a simulated payment system for academic demonstration purposes only. No real payments are processed.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};