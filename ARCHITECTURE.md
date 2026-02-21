# Zomato AI Restaurant Recommendation Service — Architecture

## Overview

This document describes the architecture of a Zomato AI Restaurant Recommendation Service. The system takes **city** and **price** from the user and recommends restaurants from the Zomato dataset hosted on Hugging Face: [ManikaSaini/zomato-restaurant](https://huggingface.co/datasets/ManikaSaini/zomato-restaurant). Recommendations are powered by a **Groq LLM** model.

**Interface Strategy:**
- **Development:** CLI (command-line interface) — Steps 1–5
- **STEP 6:** Web frontend — user enters city and price in a browser; recommendations are displayed on the same page

---

## Dataset Context

**Source:** Hugging Face — `ManikaSaini/zomato-restaurant` (recommendation variant)

**Expected fields (typical Zomato schema):**

| Column | Description |
|--------|-------------|
| `name` | Restaurant name |
| `listed_in(city)` / `location` | City or area |
| `approx_cost(for two people)` | Estimated cost for 2 |
| `rate` | Rating |
| `votes` | Number of votes |
| `cuisines` | Cuisine types |
| `rest_type` | Restaurant type (e.g. Quick Bites, Casual Dining) |
| `dish_liked` | Popular dishes |
| `online_order` | Online order availability |
| `book_table` | Table booking availability |
| `address` | Address |
| `url` | Restaurant URL |

---

## System Architecture

```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                    ZOMATO AI RECOMMENDATION SERVICE                                 │
├─────────────────────────────────────────────────────────────────────────────────────┤
│  STEP 1          STEP 2          STEP 3          STEP 4          STEP 5    STEP 6   │
│  ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐    ┌─────────┐  ┌───────┐ │
│  │  Load   │───▶│  User   │───▶│Integrate│───▶│Recommend│───▶│ Display │─▶│ Web   │ │
│  │  Data   │    │  Input  │    │         │    │         │    │         │  │Front  │ │
│  └─────────┘    └─────────┘    └─────────┘    └─────────┘    └─────────┘  └───────┘ │
└─────────────────────────────────────────────────────────────────────────────────────┘
                                                                  ▲              │
                                                                  │   STEP 6:    │
                                                                  │   Frontend   │
                                                                  │   (form +    │
                                                                  │   results)   │
```

---

## Phase 1 — Input the Zomato Data (STEP 1)

**Objective:** Load and prepare the Zomato dataset for use.

### Responsibilities

- **Data source:** Hugging Face `datasets` library — load `ManikaSaini/zomato-restaurant`
- **Format:** Convert to in-memory DataFrame (e.g. pandas) for processing
- **Validation:** Check dataset schema, presence of `city`- and `price`-related columns
- **Cleaning:** Handle missing values, normalize numeric fields (e.g. `approx_cost`), fix rating formats

### Expected Outputs

- Data loader module/script
- Cleaned DataFrame (or equivalent structure)
- Schema and basic statistics

### Considerations

- `approx_cost(for two people)` may be string (e.g. "₹300") — parse and normalize
- `rate` may include text (e.g. "4.5/5") — extract numeric rating
- Decide how to treat city: `listed_in(city)` vs `location`

---

## Phase 2 — User Input (STEP 2)

**Objective:** Capture and validate user preferences.

### Responsibilities

- **Inputs:**
  - **City** — string (e.g. "Bangalore", "Mumbai")
  - **Price** — budget indicator (e.g. "500", "1000–2000", "Low/Medium/High")
- **Validation:** Check city exists in dataset; normalize price ranges
- **Interface:** Design contract for how user input is passed; **CLI first** (e.g. `argparse`) for development; WebUI later
- **Defaults:** Optional default values for missing or partial input

### Expected Outputs

- Input handler/parser
- Validated, structured input object
- Mapping of price range to numeric bands (e.g. Low = 0–500, Medium = 500–1500, High = 1500+)

### Considerations

- City name matching (case, spelling)
- Price format (single value vs range)
- Handling invalid or out-of-range inputs

---

## Phase 3 — Integrate (STEP 3)

**Objective:** Connect data loading and user input into a single pipeline.

### Responsibilities

- **Integration flow:**
  1. Load data (STEP 1)
  2. Accept user input (STEP 2)
  3. Use both in the recommendation engine
- **Wiring:** Single entry point that runs:
  - Data load → validation → user input → recommendation
- **State:** In-memory dataset; no persistence required
- **Error handling:** Graceful failures for bad input, missing data, or empty results

### Expected Outputs

- Main pipeline/orchestration script
- Dependency injection or module wiring
- Error-handling and logging strategy

### Considerations

- Caching or lazy loading of dataset if reloading is expensive
- Separation of concerns between data, input, and recommendation logic

---

## Phase 4 — Recommendation (STEP 4)

**Objective:** Generate restaurant recommendations using a **Groq LLM** to reason over filtered data and produce ranked suggestions.

### Responsibilities

- **Pre-filtering:** Narrow dataset before LLM call to reduce context size and cost:
  - City: match `listed_in(city)` or `location` to user’s city
  - Price: filter by `approx_cost(for two people)` within user’s budget
- **LLM Integration:** Use **Groq API** with a suitable model (e.g. `llama-3`, `mixtral`):
  - Construct a prompt with: user's city, price preference, and filtered restaurant subset (or summary)
  - Instruct LLM to rank/select top N recommendations with brief rationale
  - Parse LLM response into structured list of recommended restaurants
- **Context management:** Keep prompt within token limits; truncate or sample if dataset is large
- **Edge cases:** No matches after pre-filter → return informative message; suggest nearby cities or broader price range

### Expected Outputs

- Recommendation engine module with Groq client integration
- Prompt template(s) for recommendation task
- Structured output parser (from LLM response to restaurant list)
- Configurable parameters (model name, top N, temperature)

### Considerations

- Groq API key storage (e.g. env variable); never hardcode
- Token limits — pass summary or top-K candidates rather than full dataset
- Response format — use structured output / JSON mode if Groq supports it for reliable parsing
- Fallback behavior if API is unavailable or rate-limited
- Cost and latency — pre-filter aggressively to minimise prompt size

---

## Phase 5 — Display to the User (STEP 5)

**Objective:** Present recommendations clearly to the end user.

### Responsibilities

- **Output format:** Text, table, or structured JSON depending on interface
- **Fields to show:**
  - Name, rating, votes
  - Approx cost for two
  - Cuisine and restaurant type
  - Address or area
  - Online order / table booking
- **Layout:** Numbered list or table with fixed columns
- **Feedback:** Clear message when no results match (with hints if applicable)
- **Interface:** **CLI during development** (e.g. `argparse`, `rich`, `tabulate`); **WebUI in future phase** (HTML + API)

### Expected Outputs

- Display/formatter module
- Template for each restaurant card/row
- Handling for empty result set

### Considerations

- Truncation of long fields (e.g. cuisines, dish_liked)
- Consistent formatting for numeric fields (rating, cost)
- Optional: color/formatting for CLI (e.g. better ratings in green)

---

## Phase 6 — Web Frontend (STEP 6)

**Objective:** Provide a web frontend where the user can enter the required input (city and price) and see recommendations displayed on the same page.

### Responsibilities

- **Frontend page:**
  - Form or controls for **city** (e.g. text input or dropdown of valid cities) and **price** (e.g. number, range, or Low/Medium/High).
  - Submit action that sends input to the backend.
  - Results area that displays the recommendation list (or an empty-state message).
- **Display on page:**
  - Show the same fields as CLI: rank, name, rating, votes, cost_for_two, cuisines, locality, address (as a table or card layout).
  - Handle empty result set with a friendly message (e.g. suggest increasing budget or trying a different city).
- **Integration:**
  - Backend API (e.g. FastAPI/Flask) that accepts city and price, runs the existing pipeline (Steps 1–5), and returns recommendations as JSON or HTML.
  - Frontend calls this API and renders the response.

### Backend–Frontend integration

**Communication:** REST over HTTP. Frontend and backend can be served from the same app (e.g. Flask/FastAPI serves both HTML and API) or from different origins (backend API + separate static/SPA frontend; CORS must be enabled on the backend).

**Flow:**
1. User opens the frontend page → (optional) frontend fetches list of valid cities from the backend.
2. User enters city and price and submits the form.
3. Frontend sends a request to the backend API with the input (e.g. `POST /api/recommend` with JSON body, or `GET /api/recommend?city=btm&price=500-1000`).
4. Backend runs the pipeline (load/use dataset → validate input → recommend → build response) and returns a single JSON response.
5. Frontend renders the recommendations (table or cards) or shows the empty-state / error message from the response.

**API contract (recommendations):**

| Aspect | Detail |
|--------|--------|
| **Endpoint** | `POST /api/recommend` (or `GET /api/recommend?city=...&price=...`) |
| **Request** | Body (JSON): `{ "city": "btm", "price": "500-1000" }` — or query params for GET. `price` can be a number, range string (e.g. `"500-1000"`), or label (`"Low"` / `"Medium"` / `"High"`). |
| **Success response (200)** | `{ "ok": true, "user_input": { "city": "...", "min_price": 500, "max_price": 1000 }, "recommendations": [ { "name": "...", "rating": 4.2, "votes": 100, "cost_for_two": 500, "cuisines": "...", "locality": "...", "address": "..." }, ... ], "empty": false }` |
| **Empty result (200)** | Same shape with `"recommendations": []` and `"empty": true`; optional `"message": "No recommendations found. Try increasing budget or a different city."` for the frontend to show. |
| **Client error (4xx)** | `{ "ok": false, "error": "Validation error message" }` (e.g. invalid city, invalid price). Use 400 for validation errors. |
| **Server error (5xx)** | `{ "ok": false, "error": "Pipeline or server error message" }` (e.g. missing GROQ_API_KEY, dataset load failure). |

**Optional endpoint (cities list):**

| Aspect | Detail |
|--------|--------|
| **Endpoint** | `GET /api/cities` |
| **Response (200)** | `{ "cities": ["btm", "church street", "koramangala", ...] }` — list of valid city/locality values from the dataset (e.g. for a dropdown). Backend can derive this from the loaded dataset or a cached list. |

**Frontend behaviour:**
- On submit: disable form or show loading state; call the recommend API; on success, render `recommendations` or the `message` when `empty` is true; on 4xx/5xx, show `error` to the user.
- All recommendation and validation logic stays on the backend; the frontend only sends input and displays the returned data.

### Expected Outputs

- Web UI (HTML/CSS/JS or a simple framework) with:
  - Input form for city and price.
  - Area for recommendations (table or cards).
  - Empty-state and error messaging.
- Backend endpoint(s) that reuse pipeline and display logic (or return structured data for the frontend to render).

### Considerations

- Reuse validation (city, price) and pipeline from Steps 2–4; keep display logic interface-agnostic so CLI and Web share the same data shape.
- Security: do not expose GROQ_API_KEY or raw dataset to the client; all recommendation logic stays server-side.
- Optional: cache dataset or precomputed city list to keep first load fast.

**Implementation:** Backend API in `web/` (FastAPI: `GET /api/cities`, `POST /api/recommend`). React frontend in `frontend/` (Vite); see `web/README.md` and `frontend/README.md` for run instructions. **Streamlit deployment:** single-app UI + pipeline in `streamlit_app.py`; run locally with `streamlit run streamlit_app.py` or deploy on Streamlit Community Cloud — see `STREAMLIT_DEPLOY.md`.

---

## Data Flow Summary

```
HuggingFace Dataset
        │
        ▼
┌───────────────────┐
│  STEP 1: Load     │  → Cleaned DataFrame
│  & Prepare        │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  STEP 2: User     │  → { city, price }
│  Input            │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  STEP 3:          │  → Integrated Pipeline
│  Integrate        │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  STEP 4:          │  → LLM-ranked Restaurant List
│  Recommendation   │     (Groq LLM)
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  STEP 5:          │  → User-friendly Output (CLI or API response)
│  Display          │
└─────────┬─────────┘
          │
          ▼
┌───────────────────┐
│  STEP 6:          │  → Frontend: form (city, price) + recommendations table/cards
│  Web Frontend     │     Backend API runs pipeline; frontend displays result
└───────────────────┘
```

---

## Suggested Project Structure

```
Proj1_ZomatoAI/
├── ARCHITECTURE.md          # This document
├── data/
│   ├── loader.py            # STEP 1: Data loading & cleaning
│   └── schema.py            # Schema definitions & validation
├── input/
│   └── handler.py           # STEP 2: User input parsing
├── pipeline/
│   └── integrate.py         # STEP 3: Integration/orchestration
├── recommendation/
│   ├── engine.py            # STEP 4: Recommendation logic
│   └── groq_client.py       # Groq LLM client & prompt templates
├── display/
│   └── formatter.py         # STEP 5: Output formatting
├── config/
│   └── settings.py         # Config & constants
├── main.py                  # CLI entry point
├── requirements.txt
├── web/                     # STEP 6: Web frontend (optional)
│   ├── app.py               # FastAPI/Flask app; API endpoint for recommend
│   ├── static/              # CSS, JS if any
│   └── templates/           # HTML page(s) with form + results area
└── frontend/                # Alternative: separate SPA or static frontend
```

---

## Technology Recommendations

| Component | Option |
|-----------|--------|
| Data loading | `datasets` (Hugging Face), `pandas` |
| **Recommendation (LLM)** | **Groq API** (e.g. `llama-3`, `mixtral`); `groq` Python SDK |
| Language | Python 3.9+ |
| Input handling | `argparse` (CLI); FastAPI/Flask (API for STEP 6) |
| Display | `rich` or `tabulate` (CLI); HTML + table/cards (STEP 6 frontend) |
| **STEP 6 Frontend** | FastAPI or Flask (backend); HTML form + results table; optional JS framework |

---

## Success Criteria by Phase

| Phase | Success Criteria |
|-------|------------------|
| STEP 1 | Dataset loads; schema validated; basic statistics available |
| STEP 2 | Valid city and price inputs accepted; invalid inputs rejected |
| STEP 3 | End-to-end flow runs from load → input → recommendation |
| STEP 4 | Groq LLM returns recommendations matching city and budget; output is parseable |
| STEP 5 | Recommendations shown clearly; empty state handled |
| STEP 6 | User can submit city and price on a web page; recommendations display on the same page; empty state and errors handled |

---

## Notes

- Deployment is **not** included in this plan.
- Phases 1–5 cover CLI; Phase 6 adds the web frontend that reuses the same pipeline.
- Dataset schema may differ slightly; adjust column names during implementation.
- Groq API key must be stored securely (e.g. `.env`, environment variable).
- Display modules should be interface-agnostic where possible to ease CLI → WebUI migration.
- STEP 6 frontend consumes the same pipeline via an API; no duplicate business logic.
