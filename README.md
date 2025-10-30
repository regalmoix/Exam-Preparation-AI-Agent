# Knowledge Assistant Demo

Ground every answer with citations using a ChatKit-powered knowledge workflow. This example combines a FastAPI backend that queries an OpenAI File Search vector store with a React UI that highlights the documents referenced in each response.

## What's Inside
- FastAPI service that streams grounded answers from an OpenAI Agent plus document citations.
- ChatKit Web Component wrapped in React with a document panel and inline citation highlighting.
- Vector-store tooling for ingesting policy documents and exposing REST endpoints for previews.

## Prerequisites
- Python 3.11+
- Node.js 20+
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (recommended) or `pip`
- OpenAI API key exported as `OPENAI_API_KEY`
- ChatKit domain key exported as `VITE_KNOWLEDGE_CHATKIT_API_DOMAIN_KEY` (use any non-empty placeholder locally; replace with the real key in production)
- Vector store ID exported as `KNOWLEDGE_VECTOR_STORE_ID` (see below)

## Quickstart Overview
1. Prepare the knowledge vector store and start the backend API.
2. Configure the domain key and launch the React frontend.
3. Explore grounded answers in the demo workflow.

Each step is detailed below.

### 1. Start the FastAPI backend

The backend lives in `examples/knowledge-assistant/backend` and includes its own `pyproject.toml`.

1. Create or reuse a vector store:
   - Visit [OpenAI Vector Stores](https://platform.openai.com/storage/vector_stores).
   - Upload the reference documents and copy the store ID (e.g. `vs_abc123`).
   - Export the ID so the agent can perform grounded search:
     ```bash
     export KNOWLEDGE_VECTOR_STORE_ID=vs_...
     ```

2. Install dependencies and launch the API:
   ```bash
   cd examples/knowledge-assistant/backend
   uv sync
   export OPENAI_API_KEY="sk-proj-..."
   uv run uvicorn app.main:app --reload --port 8002
   ```

   The API exposes ChatKit at `http://127.0.0.1:8002/knowledge/chatkit` and document helpers under `/knowledge/*` (documents, files, citations, health). If your shell cannot locate the local `app` package, set `PYTHONPATH=$(pwd)` before running Uvicorn.

### 2. Run the React frontend

```bash
cd examples/knowledge-assistant/frontend
npm install
npm run dev
```

The dev server runs at `http://127.0.0.1:5172` and proxies `/knowledge` calls to the API, which is sufficient for local iteration.

From the `examples/knowledge-assistant` directory you can also run `npm start` to launch the backend (`uv sync` + Uvicorn) and frontend together. Ensure `uv` is installed and required environment variables (such as `OPENAI_API_KEY`, `KNOWLEDGE_VECTOR_STORE_ID`, and the domain key) are exported before using this shortcut.

Regarding the domain public key, you can use any string during local development. However, for production deployments:

1. Host the frontend on infrastructure you control behind a managed domain.
2. Register that domain on the [domain allowlist page](https://platform.openai.com/settings/organization/security/domain-allowlist) and add it to `examples/knowledge-assistant/frontend/vite.config.ts` under `server.allowedHosts`.
3. Set `VITE_KNOWLEDGE_CHATKIT_API_DOMAIN_KEY` to the key returned by the allowlist page and confirm `examples/knowledge-assistant/frontend/src/lib/config.ts` reflects any env overrides you expect (API URLs, prompt text, etc.).

To rehearse remote-access flows before launch, expose the app temporarily with a tunnel—e.g. `ngrok http 5172` or `cloudflared tunnel --url http://localhost:5172`—and allowlist that hostname before testing.

### 3. Try the workflow

Open the printed URL and ask grounded questions such as:

- `Summarise the September 17, 2025 policy decision with citations.`
- `What does the August 2025 CPI release highlight?`
- `Compare the growth and inflation projections from the latest SEP.`

Each response streams with inline citations; the document grid highlights referenced files, and you can click a tile to preview the source.

### Customize the demo

- **Vector store**: Point `KNOWLEDGE_VECTOR_STORE_ID` to a different store to change the knowledge base.
- **Document manifest**: Edit `examples/knowledge-assistant/backend/app/documents.py` to rename or hide files in the grid.
- **Frontend config**: Override default endpoints with `VITE_KNOWLEDGE_*` variables or adjust behavior in `frontend/src/lib/config.ts`.
- **Port and proxy**: Update `frontend/vite.config.ts` if you need different ports or additional allowed hosts.
