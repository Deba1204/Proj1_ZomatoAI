# Phase 4 — Recommendation (STEP 4)

## GROQ_API_KEY

The recommendation engine uses the **Groq** LLM to rank top 10 restaurants. You must set the environment variable **`GROQ_API_KEY`** (never hardcode it).

### Set the API key

**Windows (PowerShell):**
```powershell
$env:GROQ_API_KEY = "your-api-key-here"
```

**Windows (CMD):**
```cmd
set GROQ_API_KEY=your-api-key-here
```

**Linux/macOS:**
```bash
export GROQ_API_KEY=your-api-key-here
```

Get an API key at [console.groq.com](https://console.groq.com).

### Run Phase 4 tests (with API key)

From the **project root** (`Proj1_ZomatoAI`), with `phase4/.env` containing `GROQ_API_KEY=your_key`:

```bash
py -m pytest phase4/tests -v
```

If you see **"GROQ_API_KEY is not set"**, set it in the shell first, then run pytest:

**Windows PowerShell:**
```powershell
$env:GROQ_API_KEY = (Get-Content phase4\.env | Where-Object { $_ -match '^GROQ_API_KEY=' } | ForEach-Object { ($_ -split '=',2)[1].Trim() })
py -m pytest phase4/tests -v
```

**Windows CMD:**
```cmd
for /f "usebackq tokens=2 delims==" %i in (`type phase4\.env ^| findstr GROQ_API_KEY`) do set GROQ_API_KEY=%i
py -m pytest phase4/tests -v
```

**Linux/macOS:**
```bash
export GROQ_API_KEY=$(grep '^GROQ_API_KEY=' phase4/.env | cut -d= -f2- | tr -d '"' | tr -d "'")
py -m pytest phase4/tests -v
```

### Run full pipeline (main.py)

```bash
py main.py --city btm --price 500-1000
```

If there are more than 10 candidates after pre-filtering and scoring, the pipeline calls Groq to rank them. If `GROQ_API_KEY` is not set, you will see a validation error.
