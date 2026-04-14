## Progress and Goals - JSDR Group

### Completed Work (Fall 2025)

**Backend Infrastructure:**
- RESTful API server for geographic data management
- MongoDB integration (local and cloud deployments)
- Deployed to Python Anywhere
- In-memory caching for query performance
- Comprehensive data validation

**Entities Implemented:**
- Countries: name, population, continent, capital, area
- States: name, population, capital, country association
- Cities: name, population, state/country association, coordinates
- Counties: name, population, state association

**REST API Endpoints:**
- Health check and echo endpoints
- Full CRUD operations for all entities:
  - `GET /countries` - List all countries (with search/filter)
  - `POST /countries` - Create new country
  - `GET /countries/{code}` - Get specific country
  - `PUT /countries/{code}` - Update country
  - `DELETE /countries/{code}` - Delete country
  - (Similar patterns for states, cities, counties)
- Stats endpoint for database metrics

**Development Tools:**
- Makefile for build automation
- Unit tests covering all controllers and data operations
- GitHub Actions CI/CD pipeline
- Swagger/OpenAPI documentation
- Test coverage: 85%+

**Requirements Met:**
RESTful API design  
Persistent data storage (MongoDB)  
Automated testing  
API documentation  
Cloud deployment  
Performance optimization (caching)

# Spring 2026 Project Goals

## Cost of Living Comparison Tool

**LiveWhere** is a web application that helps users compare cities based on cost of living, salary equivalence, and quality-of-life factors to make informed relocation and job decisions.

---

## Project Objectives

* Enable clear, side-by-side city comparisons
* Provide accurate salary-adjustment calculations across locations
* Surface “best value” cities based on user preferences
* Support personalization through saved comparisons and preferences
* Deliver a polished, data-driven frontend connected to a scalable backend

---

## Core Features

### 1. Interactive City Comparison Dashboard

* Map-based city visualization (React Leaflet)
* Color-coded affordability indicators
* Select 2–4 cities for quick comparison

### 2. City Comparison Interface

* Side-by-side breakdown across categories:

  * Housing
  * Food & Dining
  * Transportation
  * Healthcare
  * Entertainment & Lifestyle
* Visual charts (bar, pie)
* Overall affordability score (0–100)
* Adjustable spending-weight sliders

### 3. Salary Adjustment Calculator

* Compare purchasing power between cities
* Input: salary + origin city → equivalent salary in target city
* Accounts for cost of living and taxes
* Displays net-income and lifestyle-equivalent results

### 4. Smart City Finder

* Filter cities by:

  * Salary range
  * Amenities and infrastructure
  * Climate preferences
  * City size and region
* Ranked recommendations based on weighted criteria
* Highlights “best value” cities

### 5. User Profiles & Personalization

* Save favorite cities and comparisons
* Customize cost-category weights
* Track cities under consideration
* Public users: limited comparisons
* Authenticated users: full access

---

## Technical Stack

### Frontend

* React (Vite)
* Recharts or Chart.js
* React Leaflet
* Deployment: Vercel
* Backend connectivity via environment variables:

  * Local, staging, production endpoints

### Backend

* REST API with JWT authentication
* Secure password hashing
* Core endpoints:

  * City cost-of-living data
  * City comparisons
  * Salary calculator
  * Recommendations
  * Quality-of-life metrics
  * User accounts & saved comparisons

---

## Data Sources

* Numbeo (cost of living)
* Government labor and housing statistics
* World Bank data
* Manually curated dataset for initial 30–40 major cities

---

## Progress to Date (Spring 2026)

**Planning & Process:**
* Team roles defined (frontend, backend, data, testing)
* Weekly meetings established
* High-level wireframes completed
* Initial backend data models designed
* API and data-source research completed
* Kanban board and sprint planning in place

**Backend — Completed:**
* Google OAuth 2.0 authentication (`GET /auth/google`, `GET /auth/google/callback`)
  * User/session persistence in MongoDB (`Users` + `Sessions` collections)
  * 7-day session cookies (httpOnly, SameSite=Lax)
* CORS configured for frontend (`localhost:5173`)
* Cost-of-living index endpoint (`GET /cost-of-living`)
* Salary adjustment calculator (`GET /cost-of-living/salary-adjustment`)
  * Adjusts salary between cities based on COL index ratio
* Smart City Finder / Recommendations (`GET /recommendations`)
  * Affordability score (0–100) derived from COL index
  * Quality-of-life score (0–100) weighted by affordability + city size
  * Filters: state, city size (small/medium/large), top_n results
  * Returns equivalent salary per city when salary param provided
* Fallback city dataset (`data/bkup/cities.json`) when DB is unavailable
* Full CRUD for cities, countries, states, counties (carried over from Fall 2025)

**Frontend — Completed** (`jsdr-frontend` repo):
* React 19 + TypeScript + Vite app scaffolded
* Interactive city map with React Leaflet — color-coded affordability markers, click to select up to 4 cities
* City comparison panel — side-by-side breakdown, Recharts bar charts, adjustable spending-weight sliders
* Salary adjustment calculator UI — origin/target city inputs, COL-adjusted salary, state income tax estimates, take-home pay calculation
* Smart City Finder UI — filters by salary, state, city size; displays affordability + QOL scores from `/recommendations`
* Google OAuth integration (AuthBar) — sign-in link → `/auth/google`, session cookie handling, calls `/auth/me` to restore session state
* Sign-out button calling `POST /auth/logout`
* Vite proxy configured: `/api` → Flask backend at `localhost:8000`
* Basic Vitest + React Testing Library smoke tests
* Dark mode CSS variables
* Deployment scripts for local and cloud

**Backend — Missing (required by frontend):**
* `GET /auth/me` — return current user from session cookie (not yet implemented)
* `POST /auth/logout` — clear session cookie (not yet implemented)

---

## Planned Timeline

* **Weeks 3–4:** Auth, frontend–backend integration, initial city data
  * Acceptance: `/cities` POST/DELETE require tokens; React Leaflet map can display city markers from seeded data.
* **Weeks 5–7:** Comparison UI, charts, expand city dataset
  * Acceptance: Comparison dashboard supports 2–4 cities with Recharts data, filters apply to salary/amenity preferences, and budget sliders adjust scores.
* **Weeks 8–10:** Salary calculator, recommendations, QOL metrics
  * Acceptance: Salary adjustments and recommendations API return consistent payloads, UI displays QOL breakdowns
* **Weeks 11–12:** User profiles, saved comparisons, UI polish
  * Acceptance: Authenticated users can save comparisons, profile page lists saved sets, and UI matches polished wireframes.
* **Weeks 13–14:** Testing, deployment, final presentation
  * Acceptance: Automated tests cover frontend flows and backend controllers, CI/CD deploys to PythonAnywhere (or equivalent), and demo scripts ready for presentation.

---

