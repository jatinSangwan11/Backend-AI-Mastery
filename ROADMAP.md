# Roadmap

## Phase 1: OOP And LLD Foundations

Status: done.

Goal: build initial object-design intuition through small backend-flavored systems.

Completed projects:

1. Notification system
2. Payment provider system
3. API key management system

Core topics covered:

- Classes, objects, methods, `self`, and `__init__`
- Dataclasses as contracts
- Stable config vs event data
- Behavior objects
- Composition
- Protocols and structural typing
- Dependency injection
- Test doubles
- Result contracts
- Internal models vs display/API-safe models
- Module responsibility splits

## Phase 2: Advanced OOP, LLD, DB Design, And FastAPI

Status: next.

Goal: go deeper on production-style object design, SOLID, design patterns, database design, ORM boundaries, and thin FastAPI APIs, while building enough LLD judgment and vocabulary to be ready for Big Tech LLD interviews.

Learning rule:

```text
Pure Python design first -> DB design second -> ORM/repository third -> FastAPI last
```

Phase 2 projects:

1. Inventory and Order Management
2. Movie Ticket Booking
3. E-commerce Checkout Capstone

The first two projects are required. The third is the Phase 2 capstone if time allows, or it becomes the bridge into Phase 3.

Core OOP and LLD topics:

- Encapsulation and invariants
- Entities vs value objects
- Domain services vs application services
- Abstract base classes vs protocols
- Inheritance vs composition tradeoffs
- Polymorphism in real workflows
- Object lifecycle and state transitions
- Error boundaries and domain exceptions
- SOLID principles under production pressure
- Design patterns through backend requirements

Design patterns to learn through pressure:

- Strategy
- Factory
- Adapter
- Repository
- Unit of Work
- State
- Command
- Observer / Publisher-Subscriber
- Decorator
- Template Method
- Chain of Responsibility
- Specification
- Builder
- Singleton mostly as a cautionary pattern

DB and API topics:

- Table design from domain requirements
- Primary keys, foreign keys, and uniqueness
- Indexes and lookup paths
- Transaction boundaries
- Database-enforced invariants
- SQLAlchemy/SQLModel repositories
- Alembic migrations
- Pydantic request/response schemas
- FastAPI routers and dependencies
- API tests with pytest and httpx

Big Tech LLD readiness topics:

- Requirement clarification
- Use-case and actor identification
- Core entity discovery
- Class responsibility assignment
- Method/API contract design
- Relationship modeling
- State transition modeling
- Extensibility under changing requirements
- Tradeoff discussion
- Schema design and constraints
- Clear verbal explanation of the design
- Timed LLD mock rounds after project depth is built

Phase 2 guardrails:

```text
No FastAPI route until we can explain what the route orchestrates.
No ORM model until we can explain what the domain object owns.
No database table until we can explain what invariant the database must protect.
```

Teaching rule:

```text
Pressure first -> Jatin reasons -> code/refactor -> reveal the concept name clearly.
```

## Phase 3: Advanced Backend

Goal: learn production backend patterns while keeping LLD, responsibility boundaries, SOLID, and design tradeoffs in the loop.

Projects:

1. Async job queue
2. Redis-backed rate limiter
3. Event-driven notification service
4. Multi-tenant SaaS backend

Core topics:

- LLD under scale and failure pressure
- Async Python
- Background workers
- Redis caching
- Pagination, filtering, search
- Idempotency
- Retries and timeouts
- Observability
- API versioning
- Multi-tenancy

## Phase 4: AI Backend Systems

Goal: design and build AI-powered backend systems like a production engineer while continuing to apply LLD, responsibility boundaries, SOLID, and design tradeoffs.

Projects:

1. AI document ingestion service
2. RAG Q&A backend
3. Streaming chat API
4. Usage tracking and cost controls

Core topics:

- LLD for AI backend workflows
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

1. Concept/discussion, 5-15 minutes
2. Coding, 40-60 minutes
3. Tests, 10-20 minutes
4. Review/refactor, 15-30 minutes
5. Progress and notes update, 5 minutes
