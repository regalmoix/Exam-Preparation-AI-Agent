# E2E Testing Setup

This project includes comprehensive end-to-end testing for both frontend and backend components.

## Test Structure

```
tests/
├── e2e/                    # Playwright frontend tests
│   ├── file-operations.spec.js
│   ├── chat-interactions.spec.js
│   └── navigation.spec.js
├── api/                    # Pytest API tests
│   ├── test_health_and_info.py
│   ├── test_file_operations.py
│   ├── test_agent_workflows.py
│   └── test_error_handling.py
└── fixtures/               # Test data
    ├── sample.txt
    └── invalid.exe
```

## Prerequisites

1. **Backend Dependencies**: Add these to `backend/pyproject.toml`:
   ```toml
   pytest = "^7.0.0"
   httpx = "^0.24.0"
   pytest-asyncio = "^0.21.0"
   ```

2. **Frontend Dependencies**: Already installed
   - `@playwright/test`
   - Playwright browsers

## Running Tests

### All Tests
```bash
npm run test
```

### API Tests Only
```bash
npm run test:api
```

### Frontend E2E Tests Only
```bash
npm run test:e2e
```

### Interactive Mode
```bash
npm run test:e2e-ui    # Playwright UI
npm run test:api-watch # Pytest watch mode
```

## Test Coverage

### API Tests (`tests/api/`)

**Health & Info Tests:**
- ✅ Health endpoint
- ✅ Vector store info
- ✅ Agent capabilities
- ✅ Documents list
- ✅ Vector store files list

**File Operations Tests:**
- ✅ File upload success
- ✅ File upload validation (invalid types)
- ✅ File info retrieval
- ✅ File deletion
- ✅ Error handling for nonexistent files

**Agent Workflow Tests:**
- ✅ Intent classification (SUMMARIZER, RESEARCH, RAG_QA, FLASHCARD)
- ✅ Q&A queries
- ✅ Research queries
- ✅ Full workflow execution
- ✅ Agent routing and guidance

**Error Handling Tests:**
- ✅ Invalid endpoints
- ✅ Malformed JSON
- ✅ Missing required fields
- ✅ Security (SQL injection, XSS attempts)
- ✅ Large payloads
- ✅ CORS headers
- ✅ Concurrent requests
- ✅ Unicode handling
- ✅ Timeout resilience

### Frontend E2E Tests (`tests/e2e/`)

**File Operations:**
- ✅ Upload file successfully
- ✅ Delete file successfully
- ✅ Handle invalid file types
- ✅ Display documents list

**Chat Interactions:**
- ✅ Type and send messages
- ✅ Receive AI responses
- ✅ Send with Enter key
- ✅ Handle long messages
- ✅ Test different intent queries

**Navigation & UI:**
- ✅ Page loads successfully
- ✅ All UI components visible
- ✅ No console errors
- ✅ Responsive design
- ✅ Accessibility checks

## Test Configuration

### Playwright (`playwright.config.js`)
- **Base URL**: `http://localhost:5172`
- **Browsers**: Chrome, Firefox, Safari
- **Auto-start**: Frontend and backend servers
- **Timeouts**: 30s for most operations
- **Retries**: 2 in CI, 0 locally

### Pytest (`pytest.ini`)
- **Test discovery**: `tests/api/test_*.py`
- **Async mode**: Auto-enabled
- **Verbose output**: Enabled
- **Markers**: `slow`, `integration`, `unit`

## Usage Examples

### Running Specific Test Files
```bash
# Single API test file
cd backend && uv run pytest ../tests/api/test_file_operations.py -v

# Single E2E test file
npx playwright test tests/e2e/chat-interactions.spec.js

# Specific test function
cd backend && uv run pytest ../tests/api/test_agent_workflows.py::test_intent_classification_summarizer -v
```

### Running with Filters
```bash
# Only fast tests
cd backend && uv run pytest ../tests/api/ -m "not slow" -v

# Only specific browser
npx playwright test --project=chromium

# Headed mode (visible browser)
npx playwright test --headed
```

### Debug Mode
```bash
# API tests with full traceback
cd backend && uv run pytest ../tests/api/ -v --tb=long

# E2E tests with debug mode
npx playwright test --debug
```

## CI/CD Integration

The tests are designed to run in CI environments:

```yaml
# Example GitHub Actions
- name: Run API Tests
  run: |
    cd backend
    uv sync
    uv run pytest ../tests/api/ -v

- name: Run E2E Tests
  run: |
    npm ci
    npx playwright install
    npm run test:e2e
```

## Test Data Management

### Fixtures
- `tests/fixtures/sample.txt`: Valid test file for uploads
- `tests/fixtures/invalid.exe`: Invalid file type for error testing

### Cleanup
Tests automatically clean up created resources:
- Uploaded files are deleted after tests
- No persistent test data remains

## Regression Prevention

These tests verify:
1. **API Endpoints**: All endpoints return correct responses
2. **File Operations**: Upload, retrieve, delete workflows
3. **Agent Integration**: Intent classification and routing
4. **Error Handling**: Graceful failure modes
5. **Frontend Functionality**: User interactions work correctly
6. **Performance**: Reasonable response times
7. **Security**: Input validation and sanitization

## Troubleshooting

**Tests failing locally?**
1. Ensure servers are running (`npm run start`)
2. Check backend is on port 8002
3. Check frontend is on port 5172
4. Verify environment variables are set

**Playwright browser issues?**
```bash
npx playwright install --force
```

**API test timeouts?**
- Check OpenAI API key is configured
- Some agent tests may take 30+ seconds
- Network-dependent tests may need longer timeouts