# Roadmap

## Phase 1: Python OOP And LLD

Goal: build design intuition through small backend-flavored systems.

Projects:

1. Notification system
2. Payment provider system
3. API key management system
4. Rate limiter
5. Background job runner

Core topics:

- Classes, objects, methods, properties
- Composition over inheritance
- Abstract base classes and protocols
- SOLID in Python
- Strategy, Factory, Adapter, Repository, Unit of Work
- Domain models vs DTOs/schemas
- Testable design

## Phase 2: FastAPI Foundations

Goal: build APIs cleanly instead of putting all logic in route handlers.

Projects:

1. Task manager API
2. Auth and RBAC API
3. File upload API

Core topics:

- Routers
- Pydantic models
- Dependency injection
- Error handling
- Middleware
- SQLModel/SQLAlchemy
- Alembic migrations
- API tests with pytest and httpx

## Phase 3: Advanced Backend

Goal: learn production backend patterns.

Projects:

1. Async job queue
2. Redis-backed rate limiter
3. Event-driven notification service
4. Multi-tenant SaaS backend

Core topics:

- Async Python
- Background workers
- Redis caching
- Pagination, filtering, search
- Idempotency
- Retries and timeouts
- Observability
- API versioning

## Phase 4: AI Backend Systems

Goal: design and build AI-powered backend systems like a production engineer.

Projects:

1. AI document ingestion service
2. RAG Q&A backend
3. Streaming chat API
4. Usage tracking and cost controls

Core topics:

- Document parsing
- Chunking
- Embeddings
- Vector search
- Streaming responses
- Evaluation basics
- Latency and cost optimization
- Safety and access control

## Session Pattern

Each session should roughly follow:

1. Concept, 5-10 minutes
2. Coding, 40-60 minutes
3. Tests, 10-20 minutes
4. Review/refactor, 15-30 minutes
5. Progress update, 5 minutes

