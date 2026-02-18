/**
 * API Configuration
 * 
 * Centralized configuration for API endpoints.
 * Uses environment variables for different environments (development, staging, production).
 */

/**
 * Get the base API URL from environment variables.
 * Falls back to development default if not set.
 */
const getApiBaseUrl = (): string => {
  // In Vite, environment variables must be prefixed with VITE_
  const apiUrl = import.meta.env.VITE_API_BASE_URL;
  
  if (apiUrl) {
    return apiUrl;
  }
  
  // Default to development server
  // In development, Vite proxy will handle this (see vite.config.ts)
  // In production, this should be set via environment variable
  return import.meta.env.DEV 
    ? '/api'  // Use proxy in development
    : 'http://localhost:8000';  // Fallback (should be overridden in production)
};

/**
 * Base URL for all API requests
 */
export const API_BASE_URL = getApiBaseUrl();

/**
 * API endpoint paths
 */
export const API_ENDPOINTS = {
  // Cities endpoints
  CITIES: '/cities',
  CITY_BY_ID: (id: string) => `/cities/${id}`,
  
  // Health check
  HELLO: '/hello',
  
  // Endpoints discovery
  ENDPOINTS: '/endpoints',
} as const;

/**
 * Full API URLs (base + endpoint)
 */
export const API_URLS = {
  CITIES: `${API_BASE_URL}${API_ENDPOINTS.CITIES}`,
  HELLO: `${API_BASE_URL}${API_ENDPOINTS.HELLO}`,
  ENDPOINTS: `${API_BASE_URL}${API_ENDPOINTS.ENDPOINTS}`,
  CITY_BY_ID: (id: string) => `${API_BASE_URL}${API_ENDPOINTS.CITY_BY_ID(id)}`,
} as const;

