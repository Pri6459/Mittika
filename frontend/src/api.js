import axios from "axios";
import { BACKEND_BASE_URL } from "./utils/backendUrl";

const API = axios.create({
  baseURL: BACKEND_BASE_URL,
});

// ✅ Attach token automatically
API.interceptors.request.use((req) => {
  const token = localStorage.getItem("token");

  if (token) {
    req.headers.Authorization = `Bearer ${token}`;
  }

  return req;
});

API.interceptors.response.use(
  (response) => response,
  (error) => {
    if (error.response?.status === 401) {
      localStorage.removeItem("token");
      localStorage.removeItem("user");
      window.dispatchEvent(new Event("mittika:unauthorized"));
    }
    return Promise.reject(error);
  }
);

export default API;