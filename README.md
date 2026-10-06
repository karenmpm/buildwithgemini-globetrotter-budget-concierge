# 🍍 Pineapple Trips Planner (GlobeTrotter Budget Concierge)

An autonomous AI travel concierge built with the **Google Agent Development Kit (ADK)**, **A2UI**, and **Google Cloud AI Platform**. **Pineapple Trips Planner** helps travelers discover budget-friendly destinations, calculate daily cost breakdowns, convert currencies in real-time, generate custom travel postcards with **Imagen 3**, and produce short video previews using **Gemini Omni**.

![Pineapple Trips Planner Demo](demo.gif)

---

## 🌟 Architecture & Features

The agent is powered by `gemini-2.5-flash` with Google ADK and includes the following fully implemented features and Google Cloud integrations:

### 📱 A2UI Rich Display UI
- **A2UI 0.8 Schema Integration**: Uses `a2ui_utils.py` and `BasicCatalog` to emit structured UI components (cards, headers, cost breakdowns, and image galleries) natively rendered in the web UI.

### 🧠 Vertex AI Memory Bank
- **Long-Term Context & Preferences**: Configured with `PreloadMemoryTool` and memory callbacks to persist user preferences (preferred travel style, daily budget caps, favorite regions) across sessions.

### 🗄️ Firestore Database Storage
- **Persistent Destination Directory**: Real-time queries and updates to the `budget_destinations` Firestore collection to fetch travel spots, top attractions, and hostel pricing.

### ☁️ Cloud Storage (GCS) Public Bucket
- **Media Asset Storage**: Uploads generated images and videos directly to a public Cloud Storage bucket (`globetrotter-budget-assets-...`) returning public `https://storage.googleapis.com/...` URLs.

### 📸 Imagen 3 Postcard Generation
- **Visual Postcards**: Generates high-resolution destination postcards using `imagen-3.0-generate-002`, saving artifacts both to the ADK Playground and GCS.

### 🎥 Gemini Omni Short Video Previews
- **Video Previews**: Uses `gemini-omni-flash-preview` in the `global` region to produce short video teasers for travel destinations.

### 💱 Real-Time Currency & Budget Tools
- **Live Exchange Rates**: Fetches live rates via `open.er-api.com` to perform currency conversions (e.g., EUR to JPY, USD to THB) and calculate daily expense breakdowns.

### 💻 Code Sandbox Execution
- **Python Code Executor**: Safe Python sandbox execution for calculating complex multi-currency budgets and expense splits.

---

## 🏗️ Codebase Overview

```
├── app/
│   ├── agent.py               # Root ADK agent definition & tool registry
│   ├── a2ui_utils.py          # A2UI 0.8 schema manager & callbacks
│   ├── budget_tools.py        # Budget calculation tools
│   ├── currency_tools.py      # Currency conversion logic
│   ├── live_currency_tools.py # Real-time exchange rate API client
│   ├── firestore_tools.py     # Firestore database operations
│   ├── image_tools.py         # Imagen 3 destination image generator
│   ├── postcard_tools.py      # Postcard generator with GCS upload
│   └── video_tools.py         # Gemini Omni video preview generator
├── frontend/
│   ├── main.py                # FastAPI proxy speaking A2A protocol
│   └── static/
│       └── index.html         # Pineapple Trips Planner UI with Dark Mode & Lightbox
├── agents-cli-manifest.yaml   # Agent deployment manifest
└── demo.gif                   # App demonstration
```

---

## 🚀 Running the Project Locally

### 1. Prerequisites
- Python 3.11+
- [`uv`](https://github.com/astral-sh/uv) package manager installed
- [`agents-cli`](https://cloud.google.com/vertex-ai) installed

### 2. Set Up Environment Variables
Ensure the following Google Cloud environment variables are exported in your terminal:

```bash
export GOOGLE_GENAI_USE_VERTEXAI=true
export GOOGLE_CLOUD_PROJECT="<YOUR_GCP_PROJECT_ID>"
export GOOGLE_CLOUD_LOCATION="us-central1"
```

### 3. Run Agent Locally
Launch the ADK web development server:

```bash
uv run agents-cli dev
```

### 4. Run Frontend Locally
To start the custom FastAPI proxy and web frontend locally:

```bash
cd frontend
uv run uvicorn main:app --host 0.0.0.0 --port 8080
```

---

## 🛠️ Deploying to Agent Platform & Cloud Run

### Deploy the Agent to Agent Engine
```bash
agents-cli deploy \
  --region us-central1 \
  --update-env-vars GOOGLE_GENAI_USE_VERTEXAI=true,GOOGLE_CLOUD_LOCATION=us-central1
```

### Deploy the Frontend to Cloud Run
```bash
cd frontend
gcloud run deploy globetrotter-budget-frontend \
  --source . \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars AGENT_ENGINE_RESOURCE_NAME="<YOUR_AGENT_RUNTIME_RESOURCE_NAME>",AGENT_DIRECTORY="app"
```
