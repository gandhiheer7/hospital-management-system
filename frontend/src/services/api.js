import axios from 'axios';

const api = axios.create({
  baseURL: 'http://localhost:5000', // Flask Backend
  withCredentials: true, // Important for Session Cookies
  headers: {
    'Content-Type': 'application/json'
  }
});

// Handle 401 (Unauthorized) globally
api.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      localStorage.clear();
      window.location.href = '/login';
    }
    return Promise.reject(error);
  }
);

export default api;