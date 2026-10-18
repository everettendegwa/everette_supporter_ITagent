# Windows Support Agent API

First backend slice for the project: local SQLite guide search and an AI-backed chat endpoint. It does not inspect, control, or store data from a user's computer. Conversation history is supplied by the client per request and is not persisted by this API.

Every chat request sends the user's message, supplied history, and retrieved guide excerpts to OpenAI for response generation. The frontend must clearly disclose that before chat is used. Enabling `include_web_search` also allows the provider's web-search tool to search Microsoft Support and Microsoft Learn using the user's question.

## Endpoints

- `GET /health` — liveness check.
- `GET /api/v1/guides/search?q=wifi%20internet` — full-text search over the included curated guide database.
- `GET /api/v1/guides/{guide_id}` — return one guide with steps, cautions, tags, and references.
- `POST /api/v1/chat` — provide an answer using matching guides and OpenAI Responses API.
- `GET /docs` — interactive API documentation while the server is running.

Example chat request:

```json
{
  "message": "My Windows laptop says connected but there is no internet",
  "history": [],
  "include_web_search": false
}
```

Set `include_web_search` to `true` only when the UI has clearly told the user that their question will be sent to the AI provider's web-search feature. Search is constrained to Microsoft Support and Microsoft Learn domains. When web search is disabled, the agent uses its matching guide context and general model reasoning; it must say when the curated collection does not cover an issue.

## Run locally on Windows

From the repository root in PowerShell:

```powershell
cd backend
Copy-Item .env.example .env
# Put your OpenAI API key in .env. Keep .env private and out of version control.
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

Then open `http://127.0.0.1:8000/docs` or use the guide-search endpoint. Chat requires `OPENAI_API_KEY` and a model enabled for the API project. The API uses the Responses API; web search is opt-in and uses the provider's built-in `web_search` tool.

## Configuration

Copy `.env.example` to `.env` and configure `OPENAI_API_KEY`. `GUIDE_DATABASE_PATH` defaults to the copy at `backend/data/windows_troubleshooting.db`. Set `OPENAI_MODEL` to a model available to your API project. Set `ALLOW_ORIGINS` to the exact local frontend origin(s); do not use `*` for a deployed app.

## Scope and next work

- Guides are currently drafts, not human-approved production support material.
- Draft guides are hidden from search and chat by default. Set `SERVE_DRAFT_GUIDES=true` in local development only if you want to inspect prototype retrieval before review; never enable this for public deployment.
- The API is a local development prototype: it has no user authentication, rate limiting, persistent conversations, hosted database, or local-computer tool execution.
- Before public deployment, add authentication, abuse/rate controls, request-size limits, provider/data-retention disclosures, and a reviewed privacy policy. Move user accounts and conversation history to a shared hosted database such as Supabase/Postgres if needed.
- Never expose the OpenAI API key in a browser. Do not add arbitrary shell/PowerShell execution to the agent.
