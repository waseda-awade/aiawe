import axios from 'axios';
import type { AxiosInstance, AxiosRequestConfig } from 'axios';
import Cookies from 'js-cookie';

const API_BASE_URL: string = import.meta.env.VITE_API_BASE_URL;

console.log({ API_BASE_URL });

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
  (config: AxiosRequestConfig): AxiosRequestConfig => {
    const csrfToken = Cookies.get('csrftoken');
    if (csrfToken) {
      if (config.headers) {
        config.headers['X-CSRFToken'] = csrfToken;
      }
    }
    return config;
  },
  (error: any): Promise<any> => {
    return Promise.reject(error);
  }
);

export default api;
