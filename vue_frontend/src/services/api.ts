import axios from 'axios';
import type { AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import Cookies from 'js-cookie';
import { retry } from '@/lib/retry';
import { useAuthStore } from '@/stores/auth';
import router from '@/router';

const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL;
console.debug('api.ts initialization - API_BASE_URL:', { API_BASE_URL });

const api: AxiosInstance = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add a request interceptor to dynamically set the CSRF token
api.interceptors.request.use(
  (config: InternalAxiosRequestConfig): InternalAxiosRequestConfig => {
    const csrfToken = Cookies.get('csrftoken');
    if (csrfToken) {
      if (config.headers) {
        config.headers['X-CSRFToken'] = csrfToken;
      }
    }
    return config;
  },
  (error: any) => Promise.reject(error)
);

api.interceptors.response.use(
  response => response,
  async error => {
    const config = error.config;

    if (error.response && error.response.status === 403) {
      const { detail } = error.response.data;
      // If the error is due to missing credentials, log the user out
      // The server will return a 403 status code with a detail message
      //  like "Authentication credentials were not provided."
      if (detail && detail.includes('credentials')) {
        const authStore = useAuthStore();
        await authStore.logout();
        router.push({ name: 'login' });
      }
    }

    // Only retry if:
    // 1. It's a retryable error (network or 5xx)
    // 2. The request hasn't been retried yet
    if (config && !config.__isRetry) {
      config.__isRetry = true;
      try {
        return await retry(() => api(config), {
          retries: 3,
          onRetry: (error, attempt) => {
            console.log(`Retry attempt ${attempt} for ${config.url}:`, error);
          }
        });
      } catch (retryError) {
        throw retryError;
      }
    }

    throw error;
  }
);

export default api;
