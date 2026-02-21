# STEP 6 — Backend API

FastAPI server that exposes:

- **GET /api/cities** — list of valid city/locality values (for dropdown)
- **POST /api/recommend** — body `{ "city": "...", "price": "..." }`; returns recommendations or error

## Run

From the project root (`Proj1_ZomatoAI`):

```bash
# Install dependencies (if not already)
pip install -r requirements.txt

# Set GROQ_API_KEY for recommendations (e.g. in phase4/.env or environment)
# Then start the API:
python -m web.app
```

Server runs at **http://localhost:8000**. For the React frontend, start it with `npm run dev` in `frontend/`; it proxies `/api` to this backend.

## Tests

From the project root:

```bash
py -m pytest web/tests -v
```

Tests use a small in-memory DataFrame and mock the Groq recommendation engine, so no API key or network is required.
