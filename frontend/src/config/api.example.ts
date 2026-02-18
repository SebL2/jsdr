/**
 * Example usage of the API configuration
 * 
 * This file demonstrates how to use the API configuration in your components.
 * You can delete this file once you understand how to use the API config.
 */

import { API_BASE_URL, API_ENDPOINTS, API_URLS } from './api';

// Example 1: Using predefined full URLs
export async function fetchCities() {
  const response = await fetch(API_URLS.CITIES);
  return response.json();
}

// Example 2: Using endpoint paths with base URL
export async function fetchCityById(id: string) {
  const url = `${API_BASE_URL}${API_ENDPOINTS.CITY_BY_ID(id)}`;
  const response = await fetch(url);
  return response.json();
}

// Example 3: Using the helper function for dynamic endpoints
export async function fetchCityByIdHelper(id: string) {
  const response = await fetch(API_URLS.CITY_BY_ID(id));
  return response.json();
}

// Example 4: Health check
export async function checkServerHealth() {
  const response = await fetch(API_URLS.HELLO);
  return response.json();
}

// Example 5: POST request with JSON body
export async function createCity(cityData: {
  name: string;
  state_code: string;
  population: number;
}) {
  const response = await fetch(API_URLS.CITIES, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(cityData),
  });
  return response.json();
}

// Example 6: Using with React hooks

// import { useState, useEffect } from 'react';
// import { API_URLS } from './config/api';

// function CitiesList() {
//   const [cities, setCities] = useState([]);
//   const [loading, setLoading] = useState(true);

//   useEffect(() => {
//     async function loadCities() {
//       try {
//         const response = await fetch(API_URLS.CITIES);
//         const data = await response.json();
//         setCities(data.Cities || []);
//       } catch (error) {
//         console.error('Failed to fetch cities:', error);
//       } finally {
//         setLoading(false);
//       }
//     }
//     loadCities();
//   }, []);

//   if (loading) return <div>Loading...</div>;
//   return <div>{/* Render cities */}</div>;
// }


