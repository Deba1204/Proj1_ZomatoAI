# Install and run the React frontend

Run these commands **in order** from a terminal (PowerShell or Command Prompt) where **Node.js** is installed.

## 1. Go to the frontend folder (from project root)

```bash
cd c:\Users\debad\Downloads\Proj1_ZomatoAI\frontend
```

## 2. Install dependencies (first time only)

```bash
npm install
```

## 3. Start the frontend dev server

```bash
npm run dev
```

## 4. Check the final output

- In the terminal you should see something like:
  - `Vite v5.x.x ready in xxx ms`
  - `Local: http://localhost:5173/`
- **Open in browser:** http://localhost:5173
- You should see:
  - **Zomato AI** heading and a form with **City / Locality** and **Price**
  - Select a city (e.g. btm), enter a price (e.g. `500` or `Medium`), click **Get recommendations**
  - Either a table of recommendations or an empty/error message

**Note:** The backend must be running at http://localhost:8000 (run `py -m web.app` from the project root first). The frontend proxies `/api` to the backend.

## One-liner from project root (after Node is installed)

```bash
cd c:\Users\debad\Downloads\Proj1_ZomatoAI\frontend && npm install && npm run dev
```

Then open **http://localhost:5173** in your browser.
