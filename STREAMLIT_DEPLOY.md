# Deploy backend on Streamlit

The **Streamlit app** runs the same recommendation pipeline as the FastAPI backend (load dataset → validate city/price → Groq LLM → display results). You can run it locally or deploy on [Streamlit Community Cloud](https://streamlit.io/cloud).

---

## Run locally

From the **project root** (`Proj1_ZomatoAI`):

```bash
pip install -r requirements.txt
streamlit run streamlit_app.py
```

- App URL: **http://localhost:8501**
- Set **GROQ_API_KEY** in `phase4/.env` (or environment) for recommendations.

---

## Deploy on Streamlit Community Cloud

1. **Push your app to GitHub**  
   Your repo should contain at least:
   - `streamlit_app.py` (at repo root)
   - `requirements.txt` (at repo root)

2. **Sign in** at [share.streamlit.io](https://share.streamlit.io) with GitHub.

3. **New app**
   - **Repository**: `your-username/your-repo`
   - **Branch**: `main` (or your default)
   - **Main file path**: `streamlit_app.py`
   - **App URL**: e.g. `https://your-app-name.streamlit.app`

4. **Secrets (required for Groq)**  
   In the app’s **Settings → Secrets**, add:

   ```toml
   GROQ_API_KEY = "your-groq-api-key-here"
   ```

   Or in the Cloud UI: **Secrets** → paste the above. Do **not** commit this key.

5. **Deploy**  
   Streamlit will install from `requirements.txt` and run `streamlit run streamlit_app.py`. The first run may be slow while the HuggingFace dataset is downloaded.

---

## Requirements

- **Python 3.9+**
- **GROQ_API_KEY** (from [console.groq.com](https://console.groq.com)) for the recommendation engine.
- All dependencies are in `requirements.txt` (including `streamlit`, `datasets`, `pandas`, `groq`, etc.).

---

## Notes

- Dataset is loaded once and cached for 1 hour (`@st.cache_data(ttl=3600)`).
- On Streamlit Cloud, the app runs in the cloud; no need to run FastAPI or React. This is a **single-app deployment** (UI + backend logic in one process).
