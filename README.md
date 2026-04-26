# AI Data Analyst

A Streamlit app that turns any CSV into an **AI-powered data analyst**: it generates an automated dashboard (5 charts) and lets you chat with your data to get answers or request custom Plotly visualizations.

## Features

- **Upload a CSV** from the sidebar.
- **Auto dashboard**: the app asks an LLM to build **5 diverse Plotly Express charts** and renders them in a 2-column grid.
- **Chat with your data**:
  - Ask questions (aggregations, summaries, comparisons) and get **natural language answers**.
  - Ask explicitly for a **chart/plot/graph** and the agent will generate Plotly code and the app will render it.
- **Schema context**: after upload, the app shows an expander with dataset shape + inferred dtypes.

## How it works (high level)

- `app.py` is the Streamlit UI:
  - Handles CSV upload and stores the DataFrame in `st.session_state`.
  - Calls `generate_dashboard(df)` to build an initial dashboard.
  - Uses `process_query(df, prompt)` to answer chat questions or produce charts.
- `utils/data_handler.py` loads the CSV and produces a quick schema summary (row/column count + dtypes).
- `agent/core_agent.py` builds two LangChain dataframe agents:
  - `process_query(df, query)` routes between **text output** vs **Plotly figure output**.
  - `generate_dashboard(df)` requests code for **exactly 5** Plotly figures and returns them as a list.

### LLM provider

The agent uses **LangChain + `ChatOpenAI` pointed at OpenRouter**:

- Base URL: `https://openrouter.ai/api/v1`
- API key env var: `OPENROUTER_API_KEY`
- Default model in code: `openai/gpt-4o-mini`

> Note: The code enables `allow_dangerous_code=True` and executes LLM-generated Python with `exec()` to render charts. Only run this with trusted data and in an environment you control.

## Project structure

```text
.
├── app.py
├── requirements.txt
├── agent/
│   └── core_agent.py
└── utils/
    └── data_handler.py
```

## Setup

### 1) Create a virtual environment

```bash
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

### 2) Install dependencies

```bash
pip install -r requirements.txt
```

### 3) Configure environment variables

Create a `.env` file in the project root:

```bash
OPENROUTER_API_KEY=your_openrouter_key_here
```

### 4) Run the Streamlit app

```bash
streamlit run app.py
```

Then open the local URL Streamlit prints (usually http://localhost:8501).

## Usage

1. Upload a `.csv` from the sidebar.
2. Wait for the automated dashboard to render.
3. Use the chat input to ask questions like:
   - "What are the top 10 categories by sales?"
   - "What is the average order value by region?"
   - "Create a bar chart of revenue by month" (explicitly asks for a chart)

## Troubleshooting

- **"Please upload a CSV"**: you must upload a CSV before chatting.
- **LLM errors**: confirm `OPENROUTER_API_KEY` is set and valid.
- **Chart not rendering**: the agent must assign the Plotly chart to a variable named `fig` (for chat charts) or return a list named `figs` (for dashboard).

## Security notes

Because this project executes LLM-generated Python:

- Prefer running locally, not on a shared server.
- Avoid uploading sensitive datasets.
- Consider sandboxing if deploying (separate process/container, resource limits, disable dangerous operations).

## License

No license file is currently included in this repository. If you plan to share or reuse this code, consider adding a LICENSE file (e.g., MIT, Apache-2.0).