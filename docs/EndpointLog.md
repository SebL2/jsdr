# Endpoint Response Log

Documentation of every API endpoint defined in `server/endpoints.py` and the structure of the response each one returns.

Live host: https://sebl2.pythonanywhere.com

---

## `GET /hello`

Health check.

```json
{ "hello": "world" }
```

---

## `GET /endpoints`

Returns a sorted list of every URL rule registered with Flask.

```json
{
  "Available endpoints": [
    "/cities",
    "/cities/<string:city_id>",
    "/endpoints",
    "/hello",
    "..."
  ]
}
```

---

## `GET /cities`

Returns the full cities collection plus a count.

```json
{
  "Cities": [
    {
      "name": "New York",
      "state_code": "NY",
      "population": 8000000
    }
  ],
  "Number of cities": 1
}
```

## `POST /cities`

Body: `{ "name": str, "state_code": str, "population": int }`

- `201`: `{ "Success": true }`
- `400`: `{ "Error": "<reason>" }`

## `PUT /cities`

Body: `{ "city": str, "state": str, "population": int }`

- `200`: `{ "Success": true }`
- `400`: `{ "Error": "<reason>" }`

## `DELETE /cities`

Body: `{ "city": str, "state": str }`

- `200`: `{ "Success": true }`
- `400`: `{ "Error": "<reason>" }`

---

## `GET /cities/<city_id>`

- `200`:

```json
{
  "Cities": {
    "name": "New York",
    "state_code": "NY",
    "population": 8000000
  }
}
```

- `404`: `{ "Error": "City <city_id> not found" }`
- `500`: `{ "Error": "There is a connection error" }`

## `GET /cities/<city_id>/exists`

- `200`: `{ "exists": true }` or `{ "exists": false }`
- `500`: `{ "Error": "There is a connection error" }`

---

## `GET /cost-of-living`

```json
{
  "cost_of_living": {
    "New York": 100.0,
    "Austin": 75.4
  },
  "count": 2
}
```

## `GET /cost-of-living/salary-adjustment`

Query: `salary` (float), `from_city` (str), `to_city` (str)

- `200`: object returned by `col.adjust_salary()` with original and adjusted salary details.
- `400`: `{ "Error": "Salary cannot be negative" }`
- `404`: `{ "Error": "<city not found>" }`

---

## `GET /recommendations`

Query (all optional): `salary` (float), `state` (str), `size` (small|medium|large|any), `top_n` (int, max 50).

```json
{
  "recommendations": [
    {
      "name": "Austin",
      "state_code": "TX",
      "population": 978908,
      "lat": 30.2672,
      "lng": -97.7431,
      "col_index": 75.4,
      "affordability_score": 42,
      "qol_score": 58,
      "adjusted_salary": 75400.0
    }
  ],
  "total": 1
}
```

`adjusted_salary` is `null` if no `salary` query param was provided.

---

## `GET /auth/google`

`302` redirect to Google's OAuth consent screen. On config error: `503 { "Error": "<reason>" }`.

## `GET /auth/google/callback`

On success: `302` redirect to the post-login URL with a `session` cookie set.

Errors:
- `400`: `{ "Error": "Missing auth code" | "<google error desc>" | "No return email" }`
- `502`: `{ "Error": "<userinfo fetch error>" }`
- `500`: `{ "Error": "Database error: <detail>" }`

## `GET /auth/me`

- `200` (signed in):

```json
{
  "authenticated": true,
  "user": {
    "id": "<mongo id>",
    "email": "user@example.com",
    "name": "User",
    "avatar_url": "https://..."
  }
}
```

- `401` (not signed in):

```json
{
  "authenticated": false,
  "Error": "Session missing or expired. Sign in to continue.",
  "login_url": "/auth/google"
}
```

## `POST /auth/logout`

- `200`: `{ "authenticated": false }` (also clears the `session` cookie).

---

## `GET /auth/me/profile`

- `200`:

```json
{
  "user_id": "<id>",
  "favorites": [],
  "saved_comparisons": [],
  "weights": {
    "Housing": 3,
    "Food": 2,
    "Transportation": 2,
    "Healthcare": 2,
    "Entertainment": 1
  },
  "updated_at": "2026-05-04T..."
}
```

- `401`: `{ "Error": "Authentication required" }`

## `POST /auth/me/favorites`

Body: `{ "name": str, "state_code": str }`

- `200`:

```json
{
  "favorites": [
    {
      "name": "Austin",
      "state_code": "TX",
      "added_at": "2026-05-04T..."
    }
  ]
}
```

- `400`: `{ "Error": "name and state_code required" }`
- `401`/`403`: auth/policy error.

## `DELETE /auth/me/favorites/<city_key>`

`city_key` is URL-encoded `"<name>|<state_code>"`.

- `200`: `{ "favorites": [...] }` (updated list)
- `401`: `{ "Error": "Authentication required" }`

## `POST /auth/me/comparisons`

Body: `{ "name": str, "cities": [{ "name": str, "state_code": str }, ...] }`

- `200`:

```json
{
  "saved_comparisons": [
    {
      "id": "<hex>",
      "name": "My comparison",
      "cities": [{ "name": "Austin", "state_code": "TX" }],
      "created_at": "2026-05-04T..."
    }
  ]
}
```

- `400`: `{ "Error": "name required" | "cities must be a non-empty list" | "cities entries require name and state_code" }`
- `401`: `{ "Error": "Authentication required" }`

## `DELETE /auth/me/comparisons/<comparison_id>`

- `200`: `{ "saved_comparisons": [...] }` (updated list)
- `401`: `{ "Error": "Authentication required" }`

## `PUT /auth/me/weights`

Body: `{ "weights": { "<category>": int (0-5), ... } }`

- `200`: `{ "weights": { "Housing": 3, ... } }` (clamped to 0-5; non-numeric entries dropped)
- `400`: `{ "Error": "weights must be an object" }`
- `401`: `{ "Error": "Authentication required" }`

---

## `POST /dev/locations/bulk`

Header: `X-Dev-Key: <DEV_API_KEY>`. Body: JSON array of location objects.

- `207 Multi-Status`:

```json
{
  "summary": { "total": 2, "inserted": 1, "failed": 1 },
  "results": [
    {
      "index": 0,
      "status": "inserted",
      "name": "Austin",
      "state_code": "TX",
      "inserted_id": "<mongo id>"
    },
    {
      "index": 1,
      "status": "error",
      "name": "Bad",
      "error": "population must be a non-negative integer"
    }
  ]
}
```

- `400`: `{ "Error": "Request body must be a JSON array" }`
- `401`: `{ "Error": "Invalid or missing X-Dev-Key" }`
- `503`: `{ "Error": "DEV_API_KEY not configured on server" }`
