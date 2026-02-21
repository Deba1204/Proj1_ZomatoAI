# Zomato AI — React frontend (STEP 6)

React (Vite) UI for restaurant recommendations: city + price form, recommendations table, empty and error states.

## Prerequisites

- **Node.js 18+** — [Download LTS](https://nodejs.org/) if not installed.
- **If "npm is not recognized"** after installing Node: use **`run-frontend.bat`** in this folder (it adds Node to PATH for the session), or see **`NPM-NOT-RECOGNIZED.md`** for fixing PATH.
- **Backend API** running at **http://localhost:8000** (from project root: `py -m web.app`).

## Install and run (from project path)

From the **project root** `Proj1_ZomatoAI`:

```bash
cd frontend
npm install
npm run dev
```

Or in one line:

```bash
cd frontend && npm install && npm run dev
```

## Check the final output

1. After `npm run dev`, the terminal shows: **Local: http://localhost:5173/**
2. Open in browser: **http://localhost:5173**
3. You should see the Zomato AI form (city dropdown, price input, “Get recommendations” button).
4. Select a city (e.g. **btm**), enter price (e.g. **500** or **Medium**), submit.
5. Result: either a **recommendations table** (name, rating, votes, cost, cuisines, locality, address) or an **empty/error message**.

The frontend proxies `/api` to the backend, so the backend must be running on port 8000.

## Build for production

```bash
cd frontend
npm run build
npm run preview
```

Then open the URL shown by `npm run preview` (e.g. http://localhost:4173). For production, configure your server to proxy `/api` to the backend.
