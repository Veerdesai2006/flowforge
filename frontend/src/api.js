import axios from 'axios';

// NEW CONCEPT: Axios Instance
// What it is: A pre-configured version of the axios HTTP client.
// Why it exists: Instead of typing the full URL (http://localhost:8000/api) every time 
// we make a request, we create a single instance that already knows where our backend is.
const api = axios.create({
  baseURL: '/api',
});

// NEW CONCEPT: Request Interceptor
// What it is: A function that runs *before* every single request is sent to the backend.
// Why we need it: Our FastAPI backend requires a JWT token (Authorization: Bearer <token>) for protected routes.
// Instead of manually adding the token to every single request across our entire app, 
// this interceptor grabs the token from localStorage and attaches it automatically!
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
}, (error) => {
  return Promise.reject(error);
});

export default api;
