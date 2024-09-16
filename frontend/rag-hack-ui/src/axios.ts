import axios from 'axios';

const axiosInstance = axios.create({
  baseURL: 'https://curio-4dpf.onrender.com/api/',
  headers: {
    'Content-Type': 'application/json',
  },
});

export default axiosInstance;