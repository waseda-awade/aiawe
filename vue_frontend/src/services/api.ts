import axios from 'axios';
import type { AxiosInstance, InternalAxiosRequestConfig } from 'axios';
import Cookies from 'js-cookie';
import { retry } from '@/lib/retry';

const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL;
console.log('api.ts initialization - API_BASE_URL:', { API_BASE_URL });

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
