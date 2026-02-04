import axios from 'axios';

// Create Axios instance pointing to Flask backend
const apiClient = axios.create({
  baseURL: 'http://localhost:5000',
  withCredentials: true, // Required to send/receive HttpOnly session cookies
  headers: {
    'Content-Type': 'application/json'
  }
});

// Response interceptor to handle session expiry (401)
apiClient.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response && error.response.status === 401) {
      // Clear local storage routing flags
      localStorage.removeItem('user_role');
      localStorage.removeItem('user_id');
      localStorage.removeItem('profile_id');
      localStorage.removeItem('user_email');

      // Force redirect to login if not already there
      if (window.location.pathname !== '/login' && window.location.pathname !== '/register') {
        window.location.href = '/login';
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;