## AI-CHATBOT-APP

This project is a small AI Chatbot demo that wires a frontend (Streamlit) to a FastAPI backend which invokes AI agents (via Langchain adapters for Groq/OpenAI) and an optional web search tool (Tavily).

This README documents the repository files, dependencies, environment variables, how to run the app locally, and example requests.

---

## Repository layout (files you should care about)

- `ai_agent.py`
  - Implements the wrapper that configures LLMs and tools and invokes the agent.
  - Uses `langchain-groq` and `langchain-openai` adapters (`ChatGroq`, `ChatOpenAI`) and `TavilySearch` for optional web search.
  - Exposes `response_from_ai_agents(llm_id, query, allow_search, system_prompt, provider)` which returns the latest AI message (string) from the agent invocation.
  - Important: API keys are read from environment variables: `GROQ_API_KEY`, `TAVILY_API_KEY`, and `OPENAI_API_KEY`.

- `backend.py`
  - A small FastAPI app exposing a POST `/chat` endpoint.
  - Accepts a JSON body matching the `RequestState` Pydantic model:
    - `model_name: str` — e.g. `llama-3.3-70b-versatile` or `gpt-4o-mini`
    - `model_provider: str` — `Groq` or `OpenAI`
    - `system_prompt: str` — system role / instruction
    - `messages: List[str]` — list of messages (current code sends the user query as a single-item list)
    - `allow_search: bool` — whether the Tavily search tool should be used
  - Validates the model name against `allowed_model_names`. Calls `response_from_ai_agents` and returns the AI response. If that fails, it attempts a Groq fallback and returns an error dict if both fail.
  - If you run `python backend.py` directly it starts `uvicorn` on `127.0.0.1:9999`.

- `frontend.py`
  - Streamlit-based UI used to gather `system_prompt`, choose a provider/model, set whether web search is allowed, and send a user query.
  - Sends POST requests to the backend at `http://127.0.0.1:9999/chat` with a JSON payload.
  - If the primary provider fails it attempts the other provider as a fallback.

- `Pipfile` and `Pipfile.lock`
  - Project dependency manifest (Pipenv). `Pipfile` lists the required packages and the required Python version (`3.13`).
  - Use `pipenv install` to create the environment and install deps. `Pipfile.lock` (if present) contains the locked versions for reproducibility.

---

## Dependencies (high level)

Primary packages referenced by the code:

- fastapi
- uvicorn
- streamlit
- requests
- pydantic
- langchain-groq (adapter)
- langchain-openai (adapter)
- langgraph
- langchain-community
- langchain (indirect via adapters)
- tavily / langchain_tavily (search tool used in `ai_agent.py`)

The full `Pipfile` in this project lists additional packages (pytest, playwright, etc.). See `Pipfile` if you need exact pinned versions.

Environment: The `Pipfile` specifies Python 3.13. Use the same or a compatible 3.13.x interpreter.

NOTE: Some of the langchain adapters used in this repository are third-party packages. Ensure they exist on PyPI for your environment, or install them from the provider's instructions (GitHub, private index) if necessary.

---

## Required environment variables

Before running the backend you must set provider API keys in the shell environment so the LLM adapters and search tool can authenticate:

- `GROQ_API_KEY` — Groq API key (if you plan to use Groq)
- `OPENAI_API_KEY` — OpenAI API key (if you plan to use OpenAI)
- `TAVILY_API_KEY` — Tavily search API key (if you plan to use the Tavily search tool)

Example (macOS / zsh):

```bash
export OPENAI_API_KEY="sk-..."
export GROQ_API_KEY="groq-..."
export TAVILY_API_KEY="tavily-..."
```

---

## How to run (local dev)

This project uses Pipenv (Pipfile). If you prefer pip + venv you can translate the dependencies from `Pipfile` to a `requirements.txt`.

Recommended steps (with pipenv):

1. Install pipenv (if you don't have it):

```bash
python3 -m pip install --user pipenv
```

2. From the project root, create the virtual environment and install dependencies:

```bash
# create and install from Pipfile
pipenv install

# (optional) to install dev deps from lockfile exactly:
# pipenv sync
```

3. Start the backend (option A - using pipenv):

```bash
# run backend using pipenv-managed python (this will start uvicorn on 127.0.0.1:9999)
pipenv run python backend.py
```

or (option B - use uvicorn directly):

```bash
# inside the pipenv shell
pipenv shell
uvicorn backend:app --reload --host 127.0.0.1 --port 9999
```

4. Start the frontend Streamlit app in a new terminal:

```bash
pipenv run streamlit run frontend.py
```

5. Open the Streamlit UI in your browser (Streamlit prints the local URL, usually `http://localhost:8501`).

---

## API contract (backend)

Endpoint: POST /chat

Request JSON shape (example):

```json
{
  "model_name": "gpt-4o-mini",
  "model_provider": "OpenAI",
  "system_prompt": "You are a helpful assistant.",
  "messages": ["Tell me about the latest in AI."],
  "allow_search": false
}
```

Successful response:
- Typically the backend returns the AI-generated text as the response body (string).

Error responses:
- If model validation fails: {"error": "Invalid model, Select valid AI model"}
- If both providers fail: {"error": "Both OpenAI and Groq failed", "details": "..."}

Notes: The frontend assumes the backend is at `http://127.0.0.1:9999/chat`.

---

## Quick development notes & edge cases

- The `ai_agent.py` function `response_from_ai_agents` expects `messages` to be a list; the frontend currently sends the user query as a single string inside a list. The agent code then creates a `state` dict with `{"messages": query}`. If you change the frontend to send multiple messages, confirm `ai_agent` still handles the shape correctly.
- If the LLM adapters or Tavily packages are not available via PyPI for your platform, you may need to install them from their source repositories.
- The project currently returns plain strings from the backend in success cases; returning structured JSON (e.g., {"text": "..."}) may simplify client-side handling.

---

## Troubleshooting

- If you see connection errors in the frontend, make sure the backend is running and reachable at `127.0.0.1:9999`.
- If you see authentication errors from the providers, verify the environment variables are set and valid.
- If you see import errors for `langchain-groq`, `langchain-openai` or similar, verify the packages exist on your Python index or check the adapter package installation instructions.

---

If you'd like, I can:

- Add a small test that mocks the LLM adapters so the backend can be unit-tested without API keys.
- Convert the backend to always return JSON objects (safer for clients).
- Create a `requirements.txt` for easier pip usage.

Choose one and I'll implement it next.
