# 📚 PDF Chat Application

A production-ready FastAPI backend for intelligent document conversations. Upload PDFs, ask questions in natural language, and get accurate answers powered by RAG (Retrieval-Augmented Generation).

[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-00a393.svg?style=flat&logo=FastAPI)](https://fastapi.tiangolo.com)
[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg?style=flat&logo=python)](https://www.python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

## ✨ Features

- **🔐 Secure Authentication** - JWT-based user authentication with role-based access control
- **📄 PDF Processing** - Upload, validate, and extract text from PDF documents
- **🤖 AI-Powered Chat** - Ask questions about your documents using natural language
- **💾 Conversation History** - Maintain context across multiple queries with session management
- **🎯 Source Attribution** - Every answer includes page references and source chunks
- **👥 Multi-User Support** - Complete data isolation between users
- **📊 Analytics Dashboard** - Track usage statistics and query metrics
- **⚡ Async Operations** - Fast, non-blocking API with background processing

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                  FastAPI Backend                     │
├─────────────────────────────────────────────────────┤
│  Authentication  │  Document API  │  Chat API       │
│─────────────────────────────────────────────────────│
│         Service Layer (Business Logic)              │
│  PDF Processing │ Vector Store │ Chat Service       │
│─────────────────────────────────────────────────────│
│  PostgreSQL     │   ChromaDB    │    OpenAI         │
│  (Metadata)     │  (Embeddings) │    (LLM)          │
└─────────────────────────────────────────────────────┘
```

**Stack:**
- **Backend**: FastAPI, SQLModel, LangChain
- **Database**: PostgreSQL (metadata), ChromaDB (vectors)
- **AI**: OpenAI GPT-4 & Embeddings
- **Auth**: JWT with bcrypt password hashing

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- PostgreSQL 14+
- OpenAI API key

### Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/pdf-chat-backend.git
cd pdf-chat-backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env with your credentials
```

### Configuration

Create a `.env` file with the following variables:

```bash
# Database
DATABASE_URL=postgresql+asyncpg://user:password@localhost:5432/pdf_chat

# OpenAI
OPENAI_API_KEY=sk-your-api-key-here
LLM_MODEL=gpt-4o-mini
EMBEDDING_MODEL=text-embedding-3-small

# JWT Authentication
SECRET_KEY=your-secret-key-here
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Optional Settings
MAX_FILE_SIZE_MB=10
CHUNK_SIZE=1000
RETRIEVAL_TOP_K=4
```

### Run the Application

```bash
# Start the server
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Access the API documentation
# Swagger UI: http://localhost:8000/docs
# ReDoc: http://localhost:8000/redoc
```

## 📡 API Overview

### Authentication

```bash
# Register a new user
POST /auth/register
{
  "username": "user@example.com",
  "email": "user@example.com",
  "password": "securepassword123"
}

# Login
POST /auth/login
{
  "username": "user@example.com",
  "password": "securepassword123"
}
```

### Document Management

```bash
# Upload PDF
POST /documents/upload
Headers: Authorization: Bearer <token>
Body: multipart/form-data (file)

# List documents
GET /documents/

# Delete document
DELETE /documents/{document_id}
```

### Chat & Queries

```bash
# Ask a question
POST /chat/query
{
  "question": "What is the main topic of this document?",
  "document_id": "abc123",
  "session_id": "session-uuid"
}

# Get conversation history
GET /chat/history/{session_id}

# Clear session
DELETE /chat/session/{session_id}
```

## 🗂️ Project Structure

```
Backend/
├── app/
│   ├── main.py              # FastAPI app initialization
│   ├── config.py            # Configuration management
│   ├── auth.py              # JWT utilities
│   ├── routes/              # API endpoints
│   │   ├── auth.py
│   │   ├── users.py
│   │   ├── document.py
│   │   └── chat.py
│   ├── services/            # Business logic
│   │   ├── pdf_processor.py
│   │   ├── vector_store.py
│   │   ├── chat_service.py
│   │   └── query_stats.py
│   ├── models/              # Data models
│   │   ├── db_models.py
│   │   └── schemas.py
│   └── db/                  # Database configuration
│       └── session.py
├── data/
│   └── chroma/              # Vector store persistence
├── .env                     # Environment variables
├── requirements.txt         # Dependencies
└── README.md
```

## 🔐 Security Features

- **Password Hashing**: bcrypt with salt rounds
- **JWT Tokens**: Secure token-based authentication
- **Data Isolation**: User-specific data access controls
- **Input Validation**: Pydantic schemas for all requests
- **File Validation**: Type and size checks for uploads
- **SQL Injection Protection**: Async ORM with parameterized queries

## 📊 Key Features Explained

### RAG (Retrieval-Augmented Generation)

1. User uploads a PDF → Document is chunked and embedded
2. User asks a question → Query is embedded
3. Similar chunks are retrieved from vector database
4. LLM generates answer using retrieved context
5. Answer includes source citations with page numbers

### Document Processing Pipeline

```
Upload → Validate → Hash → Extract Text → Chunk → 
Embed → Store in ChromaDB → Update Status → Ready
```

### Session Management

- Each conversation has a unique `session_id`
- Chat history maintained per session
- Context-aware responses using previous Q&A
- Sessions can be cleared individually or in bulk

## 🔧 Development

### Database Migrations

```bash
# Initialize database
python -c "from app.db.session import init_db; import asyncio; asyncio.run(init_db())"
```

## 📈 Performance

- **Async Operations**: All I/O operations are non-blocking
- **Background Processing**: PDF processing doesn't block API responses
- **Connection Pooling**: Efficient database connection management
- **Embeddings Cache**: Duplicate documents reuse existing embeddings

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [FastAPI](https://fastapi.tiangolo.com/) - Modern web framework
- [LangChain](https://www.langchain.com/) - LLM application framework
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [OpenAI](https://openai.com/) - LLM and embeddings

## 📧 Support

For questions and support:
- Open an issue on [GitHub Issues](https://github.com/yourusername/pdf-chat-backend/issues)
- Email: support@example.com

---

Built with ❤️ using FastAPI and LangChain
