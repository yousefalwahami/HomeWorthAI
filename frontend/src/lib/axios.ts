import axios from 'axios';

// Create an Axios instance with base URL and credentials enabled
const api = axios.create({
    baseURL: import.meta.env.VITE_REACT_APP_API_URL,
    withCredentials: true, // Important for sending cookies with requests
});

export default api;