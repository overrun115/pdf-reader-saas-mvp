import api from './api';

const API_BASE_URL = '';

export interface SubscriptionPlan {
  tier: string;
  name: string;
  price: number;
  price_id: string;
  features: string[];
  files_per_month: number;
}

export interface SubscriptionStatus {
  tier: string;
  subscription_active: boolean;
  subscription_id: string | null;
  subscription_end_date: string | null;
  stripe_customer_id: string | null;
}

export interface UsageInfo {
  current_tier: string;
  files_processed_this_month: number;
  tier_limit: number;
  remaining_files: number;
  subscription_active: boolean;
  subscription_end_date: string | null;
}

export interface CreateCheckoutRequest {
  price_id: string;
  success_url: string;
  cancel_url: string;
}

export interface CheckoutResponse {
  checkout_url: string;
  session_id: string;
}

export interface BillingPortalResponse {
  portal_url: string;
}

class SubscriptionAPI {
  async getSubscriptionPlans(): Promise<SubscriptionPlan[]> {
    try {
      const response = await api.get(`${API_BASE_URL}/subscription/plans`);
      return response.data;
    } catch (error) {
      console.error('Error fetching subscription plans:', error);
      throw error;
    }
  }

  async getSubscriptionStatus(): Promise<SubscriptionStatus> {
    try {
      const response = await api.get(`${API_BASE_URL}/subscription/status`);
      return response.data;
    } catch (error) {
      console.error('Error fetching subscription status:', error);
      throw error;
    }
  }

  async getUsageInfo(): Promise<UsageInfo> {
    try {
      const response = await api.get(`${API_BASE_URL}/subscription/usage`);
      return response.data;
    } catch (error) {
      console.error('Error fetching usage info:', error);
      throw error;
    }
  }

  async createCheckoutSession(request: CreateCheckoutRequest): Promise<CheckoutResponse> {
    try {
      const response = await api.post(`${API_BASE_URL}/subscription/create-checkout`, request);
      return response.data;
    } catch (error) {
      console.error('Error creating checkout session:', error);
      throw error;
    }
  }

  async createBillingPortalSession(returnUrl: string): Promise<BillingPortalResponse> {
    try {
      const response = await api.post(`${API_BASE_URL}/subscription/create-billing-portal`, {
        return_url: returnUrl
      });
      return response.data;
    } catch (error) {
      console.error('Error creating billing portal session:', error);
      throw error;
    }
  }

  async cancelSubscription(): Promise<void> {
    try {
      await api.post(`${API_BASE_URL}/subscription/cancel`, {});
    } catch (error) {
      console.error('Error cancelling subscription:', error);
      throw error;
    }
  }
}

export const subscriptionAPI = new SubscriptionAPI();