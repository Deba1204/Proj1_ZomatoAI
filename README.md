# 🍽️ ZomatoAI — Context-Aware Restaurant Discovery Engine

> **TL;DR:** An AI-assisted dining recommender that combines **deterministic filtering** (city, budget) with **LLM semantic ranking** (Groq) to solve decision fatigue when choosing where to eat.

![Status](https://shields.io)
![Stack](https://shields.io)


## 1. Problem Statement
Traditional food discovery apps overwhelm diners with hundreds of keyword-matched listings and noisy ratings. Users rarely want a raw list of 200 restaurants—they want **3 to 5 high-conviction recommendations** tailored to their budget, city, and dining vibe.

* **Target User:** Urban diners looking for fast, budget-aligned restaurant picks without manually cross-checking menus, reviews, and price-for-two estimates.
* **Core Hypothesis:** Combining hard structured filters (eliminating out-of-budget or out-of-city hallucinations) with LLM contextual ranking produces faster, higher-trust dining decisions.


## 2. Solution & Key Features
* **Hybrid Retrieval Pipeline:** Uses structured dataset filtering first to guarantee factual accuracy (location and price constraints), followed by LLM reasoning to rank and explain top matches.
* **Modular Architecture:** Decoupled data ingestion, validation, recommendation orchestration, and web presentation layers for easy model or dataset swapping.
* **Resilient Input Handling:** Sanitizes user queries and handles edge cases (e.g., ultra-low budgets or niche cuisine requests) gracefully.


## 3. System Architecture

```text
[Raw Restaurant Dataset] ──► [Data Cleaning & Normalization Pipeline]
                                            │
                                            ▼
[User Query: City + Budget] ──► [Deterministic Pre-Filter (SQL/Pandas)]
                                            │
                                            ▼
                           [Candidate Subset (Top-N Matches)]
                                            │
                                            ▼
                       [Groq LLM Orchestrator & Ranker]
                                            │
                                            ▼
                  [Web UI: Ranked Picks + Concise Rationale]



## 4. Product & Engineering Trade-Offs
* **Why Pre-Filtering Before LLM Ranking?** Passing raw restaurant catalogs directly to an LLM increases token costs, latency, and hallucination risk. Filtering by city and budget first reduces context size and ensures every recommended venue is actionable.
* **Why Groq for Inference?** Selected for sub-second token generation so restaurant discovery feels interactive rather than sluggish.


## 5. Run Locally


# 1. Clone the repository
git clone https://github.com
cd Proj1_ZomatoAI

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set your Groq API key
export GROQ_API_KEY="your_groq_api_key_here"

# 4. Launch the streamlit web app
streamlit run streamlit_app.py


## 6. Metrics & Future Enhancements
* **Target Metrics:** Query-to-recommendation latency (< 3s), constraint adherence rate (100% within user budget/city), and click-through/selection rate.
* **Next Steps:** Add dietary preference tags, group-dining consensus mode, and live review sentiment summarization.
