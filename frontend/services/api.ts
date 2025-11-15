/**
 * Base API client configuration using Axios
 * Handles requests to FastAPI backend
 */

import axios, { type AxiosInstance, type AxiosError } from "axios";
import type { APIError } from "@/types/api.types";

// Create axios instance with base configuration
const api: AxiosInstance = axios.create({
  baseURL: process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000/api",
  headers: {
    "Content-Type": "application/json",
  },
  timeout: 10000, // 10 second timeout
});

// Request interceptor (for future auth token injection)
api.interceptors.request.use(
  (config) => {
    // Add auth token if available (future feature)
    if (typeof window !== "undefined") {
      const token = localStorage.getItem("auth_token");
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor (error handling)
api.interceptors.response.use(
  (response) => response,
  (error: AxiosError<APIError>) => {
    // Log error for debugging
    console.error("API Error:", {
      url: error.config?.url,
      method: error.config?.method,
      status: error.response?.status,
      message: error.response?.data?.message || error.message,
    });

    // Return structured error
    return Promise.reject({
      message: error.response?.data?.message || error.message || "An error occurred",
      code: error.response?.data?.code || error.code,
      details: error.response?.data?.details,
      status: error.response?.status,
    } as APIError & { status?: number });
  }
);

export default api;
