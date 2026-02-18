# Environment Variables Setup

This document explains how to configure the API endpoint for different environments.

## Quick Start

1. Create a `.env.local` file in the `frontend/` directory (this file is git-ignored)
2. Add the following line:

```bash
VITE_API_BASE_URL=/api
```

This will use the Vite development proxy (recommended for local development).

## Environment Variables

### `VITE_API_BASE_URL`

The base URL for the API server. This variable is used by the API configuration in `src/config/api.ts`.

#### Development (with Vite proxy - recommended)
```bash
VITE_API_BASE_URL=/api
```
This uses the Vite proxy configured in `vite.config.ts`, which forwards requests to `http://127.0.0.1:8000`. This avoids CORS issues during development.

#### Development (direct connection)
```bash
VITE_API_BASE_URL=http://127.0.0.1:8000
```
Direct connection to the Flask server. Requires proper CORS configuration on the server.

#### Production
```bash
VITE_API_BASE_URL=https://api.yourdomain.com
```
Replace with your actual production API URL.

#### Staging
```bash
VITE_API_BASE_URL=https://staging-api.yourdomain.com
```
Replace with your actual staging API URL.

## Using the API Configuration

Import and use the API configuration in your components:

```typescript
import { API_BASE_URL, API_ENDPOINTS, API_URLS } from './config/api';

// Use predefined URLs
const citiesUrl = API_URLS.CITIES;  // e.g., "/api/cities" or "http://127.0.0.1:8000/cities"

// Or build custom URLs
const customUrl = `${API_BASE_URL}${API_ENDPOINTS.CITIES}`;

// For dynamic endpoints
const cityUrl = API_URLS.CITY_BY_ID('123');
```

## Notes

- All Vite environment variables must be prefixed with `VITE_`
- The `.env.local` file is git-ignored and won't be committed
- For production builds, set the environment variable in your deployment platform (Vercel, Netlify, etc.)
- The Vite proxy only works in development mode (`npm run dev`)

