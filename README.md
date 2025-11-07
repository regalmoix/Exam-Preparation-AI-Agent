# Exam Preparation Agent Workshop

## What's Inside
- FastAPI service that is backed by OpenAI Agents.
- ChatKit Web Component wrapped in React with a document panel.
- Vector-store tooling for ingesting documents and exposing REST endpoints for previews, uploads.

## Quick Setup Verification

**Before starting, run the setup verification script to ensure your system is ready:**

### Windows
```cmd
cd setup
setup_check.bat
```

### macOS / Linux
```bash
cd setup
./setup_check.sh
```

The script will:
- ✅ Check all prerequisites are installed and correct versions
- ✅ Auto-create `.env` file from template if needed
- ✅ Offer to install missing tools (like `uv`) automatically
- ✅ Provide detailed instructions for anything that needs manual setup
- ✅ Test that dependencies can be installed

**📖 For detailed instructions and troubleshooting, see [setup/SETUP_GUIDE.md](setup/SETUP_GUIDE.md)**

## Prerequisites
- Python 3.11+
- [nvm](https://github.com/nvm-sh/nvm) (Node Version Manager)
- Node.js 22+ (installed via `nvm`)
- [uv](https://docs.astral.sh/uv/getting-started/installation/)
- [git](https://git-scm.com/)
- OpenAI API key as `OPENAI_API_KEY` in `.env`

## Steps to Run:
### Setup Notion
1. https://github.com/makenotion/notion-mcp-server/blob/main/README.md#1-setting-up-integration-in-notion
2. https://github.com/makenotion/notion-mcp-server/blob/main/README.md#2-connecting-content-to-integration
3. Copy `Internal Integration Secret` and put in your `.env`

### Setup Logfire
1. https://logfire-us.pydantic.dev/login
2. Signin using preferred method
3. Click "Lets go" to use default `starter-project`
4. Copy `Write token` and put in your `.env`

### Start the FastAPI backend
1. Setup environment
   - Copy the template environment file into your own `.env` file: `cp .env.template .env`
2. Create or reuse a vector store:
   - Visit [OpenAI Vector Stores](https://platform.openai.com/storage/vector_stores) and create a vector store, or, Use existing vector store
   - Copy the Vector Store ID (e.g. `vs_abc123`) and set in your `.env` file, alongside your OpenAI API Key
3. Use `nvm` OR ensure Node V22+: `nvm use`
4. Install dependencies and launch the API: `npm run backend`

### Start the React Frontend
1. Use `nvm` OR ensure Node V22+: `nvm use`
2. Launch frontend server: `npm run frontend`
