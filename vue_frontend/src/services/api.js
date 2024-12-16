import axios from 'axios'
import Cookies from 'js-cookie'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL

console.log({API_BASE_URL});

const api = axios.create({
  baseURL: API_BASE_URL,
  withCredentials: true,
  timeout: 5000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// Add a request interceptor to dynamically set the CSRF token
api.interceptors.request.use(config => {
  const csrfToken = Cookies.get('csrftoken')
  if (csrfToken) {
    config.headers['X-CSRFToken'] = csrfToken
  }
  return config
}, error => {
  return Promise.reject(error)
})

export default api
