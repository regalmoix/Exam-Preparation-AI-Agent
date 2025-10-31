# 🧪 AI Study Agent Workshop - Testing Guide

This comprehensive testing guide helps workshop participants validate all functionality as they build their AI study assistant system.

## 🚀 Pre-Workshop Setup Verification

### 1. Environment Setup
```bash
# Verify environment variables are set
cat backend/.env

# Expected variables:
# OPENAI_API_KEY=sk-proj-...
# EXAM_PREP_VECTOR_STORE_ID=vs_...
# VITE_EXAM_PREP_CHATKIT_API_DOMAIN_KEY=...
```

### 2. Backend Health Check
```bash
# Start backend
npm run backend

# Test health endpoint
curl http://localhost:8002/exam-assistant/health
# Expected: {"status": "ok"}
```

### 3. API Documentation Access
```bash
# Visit interactive API docs
open http://localhost:8002/docs
```

## 📝 Phase-by-Phase Testing

### **Phase 1: Document Upload & Summarization**

#### Test Document Upload
```bash
# Upload a test document
curl -X POST -F "file=@data/sample_document.pdf" \
  http://localhost:8002/exam-assistant/vector-store/files

# Expected response: File uploaded successfully with file ID
```

#### Test Document Summarization
```bash
# Generate document summary
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "document_id": "doc_123",
    "document_type": "lecture_notes",
    "focus_areas": ["key concepts", "definitions"]
  }' \
  http://localhost:8002/exam-assistant/summarize

# Expected: Structured summary with key concepts, study notes, and citations
```

#### Validation Checklist
- [ ] Document uploads successfully to vector store
- [ ] Summary contains main_topic, key_concepts, study_notes
- [ ] Citations are properly formatted with page references
- [ ] Processing metadata is included (word_count, processing_time)

---

### **Phase 2: RAG Q&A System**

#### Test ChatKit Integration
```bash
# Ask a question about uploaded documents
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "What are the main concepts in quantum mechanics?"
      }
    ]
  }' \
  http://localhost:8002/exam-assistant/chatkit

# Expected: Streaming response with contextual answer
```

#### Test Citation Retrieval
```bash
# Get sources for a thread (replace with actual thread ID)
curl http://localhost:8002/exam-assistant/threads/thr_abc123/citations

# Expected: List of source documents with relevance scores
```

#### Validation Checklist
- [ ] Questions are answered using uploaded document context
- [ ] Citations link back to specific document sections
- [ ] Responses are factually grounded in source material
- [ ] Thread management works for conversation continuity

---

### **Phase 3: Research Agent**

#### Test Web Research
```bash
# Conduct research on a topic
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "query": "quantum computing developments 2024",
    "save_to_vectorstore": true,
    "user_id": "student123"
  }' \
  http://localhost:8002/exam-assistant/research/query

# Expected: Research synthesis with validated sources
```

#### Test Research Results Retrieval
```bash
# Get research results by task ID (use ID from previous response)
curl http://localhost:8002/exam-assistant/research/results/task_abc123

# Expected: Cached research results with source validation
```

#### Validation Checklist
- [ ] Research returns multiple high-credibility sources
- [ ] Source validation includes credibility and relevance scores
- [ ] Synthesis provides coherent summary of findings
- [ ] Results can be optionally saved to vector store
- [ ] Academic, educational, and research sources are identified

---

### **Phase 4: Flashcard Generation & MCP Integration**

#### Test Flashcard Generation
```bash
# Generate flashcards from a document
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "document_id": "doc_123",
    "card_count": 8,
    "difficulty": "medium",
    "deck_name": "Quantum Physics Study Cards",
    "user_id": "student123"
  }' \
  http://localhost:8002/exam-assistant/flashcards/generate

# Expected: Generated flashcards with different types (basic, cloze, multiple choice)
```

#### Test MCP Anki Export
```bash
# Export flashcards to Anki via MCP
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "deck_id": "deck_abc123",
    "card_count": 8
  }' \
  http://localhost:8002/exam-assistant/flashcards/export-anki

# Expected: Anki export confirmation with MCP integration details
```

#### Test Deck Information
```bash
# View flashcard deck details
curl http://localhost:8002/exam-assistant/flashcards/deck/deck_abc123

# Expected: Deck metadata including card count and difficulty
```

#### Validation Checklist
- [ ] Flashcards are generated in multiple formats (basic, cloze, multiple choice)
- [ ] Difficulty levels affect question complexity appropriately
- [ ] MCP integration shows "connected" status
- [ ] Anki export provides clear next steps for users
- [ ] Card types are properly analyzed and reported
- [ ] Spaced repetition is enabled in exported decks

---

### **Phase 5: Intent Classification & Smart Routing**

#### Test Intent Classification
```bash
# Test various query types for classification
# Summarization intent
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "query": "Can you summarize chapter 3 for me?",
    "user_id": "student123"
  }' \
  http://localhost:8002/exam-assistant/classify-intent

# Research intent
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "query": "I need to research more about machine learning algorithms"
  }' \
  http://localhost:8002/exam-assistant/classify-intent

# Flashcard intent
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "query": "Create quiz questions to test my knowledge"
  }' \
  http://localhost:8002/exam-assistant/classify-intent
```

#### Test Smart Chat Routing
```bash
# Test intelligent routing that combines classification + agent selection
curl -X POST -H "Content-Type: application/json" \
  -d '{
    "message": "I want flashcards for quantum physics concepts",
    "user_id": "student123",
    "session_id": "session456"
  }' \
  http://localhost:8002/exam-assistant/chat/smart-route

# Expected: Intent classification + appropriate agent response preparation
```

#### View Agent Capabilities
```bash
# Get comprehensive system information
curl http://localhost:8002/exam-assistant/agents/capabilities | jq .

# Expected: All 5 agents listed with capabilities and workshop phases
```

#### Validation Checklist
- [ ] Intent classification correctly identifies SUMMARIZER, RESEARCH, FLASHCARD, RAG_QA
- [ ] Confidence scores are reasonable (>70% for clear intents)
- [ ] Entity extraction captures relevant parameters
- [ ] Smart routing provides appropriate next steps for each agent type
- [ ] Agent capabilities endpoint lists all 5 agents with correct phases

## 🔍 Integration Testing Scenarios

### End-to-End Workflow Tests

#### Scenario 1: Complete Study Session
```bash
# 1. Upload study material
curl -X POST -F "file=@data/physics_lecture.pdf" \
  http://localhost:8002/exam-assistant/vector-store/files

# 2. Get document summary
curl -X POST -H "Content-Type: application/json" \
  -d '{"document_id": "doc_physics_001"}' \
  http://localhost:8002/exam-assistant/summarize

# 3. Ask questions about the material
curl -X POST -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "What is quantum entanglement?"}]}' \
  http://localhost:8002/exam-assistant/chatkit

# 4. Research additional information
curl -X POST -H "Content-Type: application/json" \
  -d '{"query": "quantum entanglement applications"}' \
  http://localhost:8002/exam-assistant/research/query

# 5. Generate study flashcards
curl -X POST -H "Content-Type: application/json" \
  -d '{"document_id": "doc_physics_001", "card_count": 10}' \
  http://localhost:8002/exam-assistant/flashcards/generate
```

#### Scenario 2: Intent-Driven Interactions
```bash
# Student asks for help - system determines best approach
curl -X POST -H "Content-Type: application/json" \
  -d '{"message": "I dont understand this chapter, help me study"}' \
  http://localhost:8002/exam-assistant/chat/smart-route

# Follow up based on classification result
# If SUMMARIZER: Generate summary
# If RAG_QA: Answer specific questions
# If FLASHCARD: Create study materials
```

## ⚠️ Common Issues & Troubleshooting

### Backend Issues
```bash
# If getting import errors
cd backend && uv sync

# If port 8002 is busy
lsof -ti :8002 | xargs kill -9

# Check environment variables are loaded
python -c "from app.config import config; print(config.validate())"
```

### API Response Issues
- **Empty responses**: Check OpenAI API key validity
- **404 errors**: Ensure backend server is running on port 8002
- **500 errors**: Check logs for specific error messages

### Vector Store Issues
```bash
# Verify vector store connection
curl http://localhost:8002/exam-assistant/vector-store

# List uploaded documents
curl http://localhost:8002/exam-assistant/documents
```

## 📊 Performance Benchmarks

### Expected Response Times
- **Document Upload**: < 5 seconds for files under 10MB
- **Summarization**: < 3 seconds for typical documents
- **Research Queries**: < 4 seconds with source validation
- **Flashcard Generation**: < 2 seconds for 10 cards
- **Intent Classification**: < 500ms for typical queries

### Quality Metrics
- **Intent Classification Accuracy**: >85% for clear queries
- **Research Source Credibility**: >80% average credibility score
- **Flashcard Variety**: Minimum 3 different card types generated
- **Citation Accuracy**: Sources should link to actual document sections

## ✅ Workshop Completion Checklist

By the end of the workshop, verify all these functionalities work:

### Core Infrastructure
- [ ] Backend server starts without errors
- [ ] All environment variables are configured
- [ ] API documentation is accessible at `/docs`

### Phase 1: Upload & Summarize
- [ ] Documents upload to vector store successfully
- [ ] Summaries generate with structured format
- [ ] Key concepts and study notes are extracted

### Phase 2: RAG Q&A
- [ ] ChatKit provides contextual answers
- [ ] Citations link to source documents
- [ ] Conversation threads maintain context

### Phase 3: Research Integration
- [ ] Web research returns validated sources
- [ ] Source credibility scoring works
- [ ] Research synthesis is coherent

### Phase 4: MCP Flashcard Integration
- [ ] Multiple flashcard types are generated
- [ ] MCP Anki integration is demonstrated
- [ ] Difficulty levels affect complexity

### Phase 5: Smart Routing
- [ ] Intent classification works for all agent types
- [ ] Smart routing provides appropriate responses
- [ ] Multi-agent coordination functions

### Integration & Polish
- [ ] All endpoints return proper error handling
- [ ] Response formats are consistent across agents
- [ ] Workshop documentation is complete and accurate

## 🎓 Next Steps After Workshop

1. **Production Deployment**: Configure for production environment
2. **Real MCP Integration**: Connect to actual Anki MCP server
3. **Enhanced RAG**: Implement hybrid search and re-ranking
4. **User Authentication**: Add user management and session handling
5. **Advanced Analytics**: Track learning progress and effectiveness

---

**Happy Testing!** 🧪✨

*This testing guide ensures every aspect of your AI Study Assistant workshop functions correctly and provides an excellent learning experience for all participants.*
