import axios from 'axios';

// Create an Axios instance with base URL and credentials enabled
const api = axios.create({
    baseURL: import.meta.env.VITE_REACT_APP_API_URL,
    withCredentials: true, // Important for sending cookies with requests
});

// Add an interceptor to include the token in every request
api.interceptors.request.use((config) => {
    const token = localStorage.getItem("token"); // Replace with your token storage mechanism
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
});
  
export default api;