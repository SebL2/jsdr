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

