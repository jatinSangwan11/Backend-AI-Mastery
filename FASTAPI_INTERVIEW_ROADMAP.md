# Python FastAPI Backend Interview Sprint

Status: active.

Target profile:

```text
Backend / AI Software Engineer
~2 years of professional experience
Python + FastAPI focus
Production-oriented backend interviews
```

Default duration: 6 weeks.

Default pace:

```text
Weekdays: 2-3 focused hours
Weekend: 3-4 hours for integration, review, and mock interviews
Six working days per week
```

If available time is lower, extend the calendar. Do not remove the exit criteria.

## Objective

Become capable of doing all of the following under interview time pressure:

- Write correct, idiomatic, typed Python without depending on an IDE or AI completion.
- Build and explain a production-shaped FastAPI endpoint.
- Choose correctly between synchronous code, asynchronous I/O, threads, processes, and background workers.
- Model relational data and write non-trivial SQL.
- Use SQLAlchemy sessions and transactions without leaking or sharing state incorrectly.
- Diagnose correctness, concurrency, performance, and security failures.
- Test behavior at unit, repository, integration, and API boundaries.
- Explain deployment, scaling, observability, and failure handling.
- Design a small-to-medium backend system and defend its tradeoffs.
- Discuss AI-backend concerns including streaming, rate limits, cost, evaluation, and tenant isolation.

## Non-Negotiable Interview Standard

Memorized definitions are insufficient.

For every subject, Jatin must be able to:

1. Explain the problem in plain language.
2. Implement a minimal correct solution.
3. Identify failure modes and edge cases.
4. Test the important behavior.
5. Explain the production version and its tradeoffs.
6. State what changes under concurrency and scale.

## Pair-Coding Protocol

Each coding session follows this structure.

### 1. Requirement clarification — 5 minutes

Jatin asks about:

- Inputs and outputs
- Expected scale
- Failure behavior
- Consistency requirements
- Security boundaries
- Required and deferred functionality

### 2. Design aloud — 5-10 minutes

Before coding, state:

- Data model
- API or function contract
- Responsibility boundaries
- Time and space complexity
- Likely failure cases

### 3. First implementation — 25-40 minutes

Jatin drives the code. Codex acts as interviewer and pair engineer.

Codex should not immediately supply the full solution. It may provide:

- Requirement clarification
- A failing test or counterexample
- A targeted hint after Jatin has reasoned
- Production review after the first working implementation

### 4. Verification — 15-20 minutes

Required checks:

- Happy path
- Invalid inputs
- Boundary conditions
- Duplicate/retry behavior where relevant
- Failure and rollback behavior
- Concurrency behavior where relevant

### 5. Production pass — 15-25 minutes

Review:

- Security
- Scalability and database access
- Maintainability and ownership
- Error handling
- Tests
- Logging, metrics, and tracing
- Deployment implications

### 6. Interview recap — 5 minutes

Jatin explains:

```text
What I built
Why I chose this design
What can fail
What I would change at larger scale
```

## Capstone Used Throughout The Sprint

Build one production-shaped service instead of many disconnected demos:

```text
AI Processing Jobs API
```

Core use case:

- Authenticated clients submit a document or AI-processing job.
- Submission supports idempotency.
- Jobs are persisted in PostgreSQL.
- Work runs asynchronously outside the request process.
- Clients query status or consume streamed progress/results.
- Usage, latency, errors, and cost are observable.
- Tenant boundaries prevent cross-customer data access.

Incremental capabilities:

1. FastAPI service skeleton and health endpoints
2. Job creation and retrieval
3. PostgreSQL and SQLAlchemy persistence
4. Idempotent submission
5. Background worker boundary
6. Redis-backed queue/cache/rate limiting
7. Authentication and tenant authorization
8. Timeouts, retries, and dead-letter behavior
9. Structured logging, metrics, and tracing
10. Streaming result endpoint
11. Dockerized deployment
12. Load and failure testing

This project is an interview vehicle, not a feature-maximization exercise. Every addition must demonstrate a specific competency.

## Week 0 / Day 1: Diagnostic Baseline

No preparation before the diagnostic.

### Python diagnostic — 35 minutes

Implement an in-memory job scheduler supporting:

- Submit job
- Retrieve by ID
- Mark running/succeeded/failed
- Reject invalid state transitions
- List jobs with pagination

Evaluation:

- Modeling
- Type hints
- Data structures
- Exceptions
- Tests
- Complexity explanation

### FastAPI diagnostic — 35 minutes

Expose:

```text
POST /jobs
GET /jobs/{job_id}
GET /jobs
```

Evaluation:

- Request/response models
- HTTP status codes
- Validation
- Dependency usage
- Error mapping
- Testability

### SQL diagnostic — 25 minutes

Write schema and queries for:

- Jobs by user
- Latest jobs
- Count by status
- Idempotent request lookup
- Failed jobs older than a threshold

### Production review — 20 minutes

Explain:

- How this breaks with multiple workers
- Where transactions begin and end
- How authentication is added
- What is logged and measured
- What runs outside the request process

Diagnostic results produce a gap list. Weak fundamentals are repaired immediately; strong topics are compressed.

## Week 1: Python, HTTP, And FastAPI Core

Goal: remove syntax uncertainty and build correct API boundaries quickly.

### Python topics

- Mutability, identity, equality, copying, and hashability
- Lists, tuples, dictionaries, sets, and complexity
- Functions, closures, decorators, iterators, generators
- Context managers and resource cleanup
- Exceptions: domain, infrastructure, and boundary errors
- Dataclasses, protocols, abstract base classes, composition
- Type hints, generics, `Protocol`, `TypedDict`, `Annotated`
- Object lifecycle and dependency ownership
- Memory references and common mutable-default bugs

### HTTP and API topics

- Methods, safety, and idempotency
- Status-code semantics
- Headers, cookies, content types, and caching headers
- Validation errors versus domain conflicts versus server failures
- Pagination, filtering, sorting, and stable cursors
- API versioning and backwards compatibility
- Request IDs and correlation IDs

### FastAPI topics

- ASGI, Starlette, FastAPI, and Uvicorn responsibilities
- Routers and application structure
- Pydantic request, response, and internal models
- Dependency injection and dependency overrides
- Exception handlers
- Middleware and request lifecycle
- Lifespan startup/shutdown
- OpenAPI generation and response contracts
- Correct use of `def` versus `async def`

### Pair-coding drills

1. Typed TTL cache
2. Cursor-pagination encoder/decoder
3. FastAPI CRUD boundary with domain errors
4. Dependency-based authorization guard
5. Request-ID middleware with structured context

### Exit criteria

- Build and test a clean FastAPI CRUD slice in 60 minutes.
- Explain ASGI and the FastAPI request lifecycle.
- Correctly choose sync versus async endpoint code.
- Use response models without leaking database objects.

## Week 2: Async Python, Concurrency, And External I/O

Goal: understand concurrency instead of decorating everything with `async`.

### Topics

- Event loop, coroutines, tasks, futures, and cooperative scheduling
- I/O-bound versus CPU-bound work
- Blocking calls inside async functions
- Thread pools and process pools
- Structured concurrency and task groups
- Cancellation propagation and cleanup
- Timeouts and deadlines
- Semaphores and bounded concurrency
- Race conditions and shared mutable state
- GIL implications without folklore
- Async HTTP clients and connection reuse
- Sync SQLAlchemy versus Async SQLAlchemy tradeoffs
- One `AsyncSession` per task; never share a session concurrently

### Pair-coding drills

1. Concurrent upstream aggregator with timeout budget
2. Bounded-concurrency batch processor
3. Cancellation-safe resource context manager
4. Retry helper with exponential backoff and jitter
5. Async endpoint containing a blocking bug, followed by diagnosis and repair

### Exit criteria

- Explain why async improves concurrency but not CPU execution.
- Diagnose event-loop blocking from code.
- Implement timeout, cancellation, and bounded concurrency safely.
- Explain when a background worker is required instead of an in-process task.

## Week 3: PostgreSQL, SQL, SQLAlchemy, And Transactions

Goal: become reliable at the persistence layer, where most backend candidates are weak.

### PostgreSQL and SQL

- Primary, foreign, candidate, and composite keys
- Normalization and intentional denormalization
- Constraints as correctness boundaries
- B-tree indexes, composite ordering, selectivity, covering indexes
- Joins, grouping, aggregates, subqueries, and CTEs
- Offset versus cursor pagination
- `EXPLAIN` and `EXPLAIN ANALYZE`
- Transactions and isolation levels
- Lost updates, write skew, row locks, deadlocks
- Optimistic and pessimistic concurrency control
- Idempotency and unique constraints

### SQLAlchemy 2.x

- Engine, connection pool, Session, transaction, and ORM responsibilities
- Declarative mappings and relationships
- Unit of Work and Identity Map behavior
- `flush` versus `commit`
- Lazy loading, eager loading, and N+1 queries
- Transaction context managers
- Session-per-request/task lifecycle
- Sync and async sessions
- Integrity-error mapping
- Repository tradeoffs
- Alembic migration workflow

### Pair-coding drills

1. Design the jobs schema with constraints and indexes
2. Write latest-job and status-aggregation SQL
3. Fix an N+1 query
4. Implement idempotent job creation transactionally
5. Implement safe job claiming using locking or conditional update
6. Diagnose and repair a transaction boundary bug

### Exit criteria

- Derive a schema from requirements and defend every constraint/index.
- Write joins and aggregate queries without ORM guesswork.
- Explain Session lifecycle, `flush`, `commit`, rollback, and identity map.
- Prevent duplicate processing under concurrent workers.

## Week 4: Testing, Security, Reliability, And Observability

Goal: turn working code into production code.

### Testing

- Test pyramid and boundary selection
- Unit, repository, integration, and API tests
- Pytest fixtures, parametrization, monkeypatching, and factories
- FastAPI `TestClient` and HTTPX async tests
- Dependency overrides
- Transactional test isolation
- Fakes versus mocks
- Contract tests for external services
- Concurrency and failure-injection tests

### Security

- Authentication versus authorization
- Password hashing and token handling
- OAuth2/JWT concepts and failure modes
- Object-level authorization and tenant isolation
- SQL injection, SSRF, unsafe deserialization, path traversal
- CORS and CSRF distinctions
- Secret handling and rotation
- Rate limiting and abuse protection
- Input and upload limits
- Avoiding sensitive-data leakage in logs and errors

### Reliability

- Timeouts before retries
- Retry safety, exponential backoff, jitter
- Circuit breakers and bulkheads
- Idempotency
- Queue acknowledgement and poison messages
- Dead-letter queues
- Graceful shutdown
- Health, readiness, and liveness

### Observability

- Structured logs
- Correlation and trace IDs
- Metrics: request rate, errors, latency, saturation
- Tracing across API, DB, worker, and AI provider
- SLOs and actionable alerts
- Cardinality control

### Pair-coding drills

1. Secure tenant-scoped job endpoint
2. Tests exposing an authorization bypass
3. Retry wrapper that refuses unsafe retries
4. Structured request logging middleware
5. Health/readiness endpoints with dependency status
6. Failure-injection test for DB rollback and external timeout

### Exit criteria

- Threat-model one endpoint and close object-level authorization gaps.
- Write tests for success, invalid input, conflict, timeout, and rollback.
- Define useful logs, metrics, traces, and alerts without leaking secrets.
- Explain why retries without idempotency can corrupt state.

## Week 5: Workers, Redis, Deployment, And AI Backend Production

Goal: cover the production surface expected from a backend/AI engineer.

### Background processing

- Request/background-task/worker boundaries
- Queue semantics and delivery guarantees
- At-least-once processing
- Idempotent consumers
- Job leases, heartbeats, retries, and dead letters
- Transactional outbox fundamentals

### Redis

- Cache-aside
- TTLs and invalidation
- Distributed rate limiting
- Atomic operations
- Lock limitations
- Cache stampede and hot keys

### Deployment

- Uvicorn workers and process memory
- Containers and multi-stage Docker builds
- Configuration and secrets
- Connection-pool sizing across workers
- Reverse proxy and HTTPS boundary
- Migrations as a one-time deployment step
- Graceful shutdown and rolling deploys
- Kubernetes concepts: deployment, service, probes, resources
- Horizontal scaling and stateless APIs

### AI backend production

- Provider timeouts, rate limits, and retries
- Streaming responses and disconnect handling
- Token and cost accounting
- Prompt/version tracking
- RAG ingestion and retrieval boundaries
- Evaluation and regression datasets
- Tenant isolation for documents and vectors
- Prompt injection and untrusted retrieved content
- Model fallback and degraded behavior
- PII handling and auditability

### Pair-coding drills

1. Idempotent worker job claim and completion
2. Redis sliding-window/token-bucket rate limiter
3. Streaming FastAPI endpoint with disconnect cleanup
4. AI-provider client with deadlines and bounded retries
5. Usage/cost ledger with transactional persistence
6. Docker and deployment review of the capstone

### Exit criteria

- Explain why in-process background tasks are not a durable job queue.
- Design an at-least-once worker that is safe under redelivery.
- Explain worker count, DB pool size, and memory interaction.
- Design safe AI-provider failure, streaming, and cost-control boundaries.

## Week 6: System Design, LLD, And Mock Interview Loop

Goal: convert knowledge into interview performance.

### LLD exercises

- Rate limiter
- Job scheduler
- Notification service
- Payment abstraction
- Feature-flag service
- Parking lot or elevator only as object-modeling drills

### Backend system-design exercises

- Async job-processing platform
- Notification delivery service
- File/document ingestion pipeline
- API rate limiter
- Multi-tenant RAG service
- Usage and billing system

### Required discussion dimensions

- Functional and non-functional requirements
- API contracts
- Data model
- Consistency and transaction boundaries
- Caching and invalidation
- Queue and worker semantics
- Failure handling
- Security and tenancy
- Observability
- Capacity estimates and bottlenecks
- Evolution path, not premature complexity

### Mock schedule

```text
Mock 1: Python pair coding, 45 minutes
Mock 2: FastAPI feature and tests, 60 minutes
Mock 3: SQL/database debugging, 45 minutes
Mock 4: Backend LLD, 45 minutes
Mock 5: System design, 60 minutes
Mock 6: Production incident/code review, 45 minutes
```

Every mock receives a score, concrete failure examples, and a retry after remediation.

## Continuous DSA And SQL Track

Backend interviews still reject candidates on basic coding and SQL. Do not substitute framework knowledge for fundamentals.

Daily minimum:

```text
30-45 minutes data structures/algorithms
20-30 minutes SQL or database reasoning
```

### DSA priority

1. Hash maps and sets
2. Two pointers and sliding windows
3. Stacks and queues
4. Binary search
5. Intervals
6. Heaps and top-K
7. Trees and traversal
8. Graph BFS/DFS
9. Basic dynamic programming
10. Tries where relevant

Target is reliable medium-level reasoning, not competitive-programming specialization.

### SQL priority

- Joins
- Grouping and conditional aggregation
- Window functions
- CTEs and subqueries
- Deduplication
- Top-N per group
- Time-range queries
- Index reasoning
- Transaction/concurrency scenarios

## Production Scenario And Incident Track

This track runs throughout all six weeks. Interview readiness requires diagnosing ambiguous production symptoms, not merely implementing endpoints.

### Required response framework

For every scenario, answer in this order:

```text
1. Clarify the symptom and blast radius.
2. Check recent changes and establish a time window.
3. Inspect metrics, traces, logs, and resource saturation.
4. Separate application, database, dependency, and infrastructure causes.
5. Mitigate customer impact before attempting a perfect fix.
6. Validate recovery with objective signals.
7. Identify root cause.
8. Add prevention, detection, and a regression test/runbook.
```

Do not jump directly to “add caching,” “add workers,” or “scale horizontally.” Those answers are guesses until evidence identifies the bottleneck.

### Scenario 1: API latency increased

Required investigation:

- Compare p50, p95, and p99 latency.
- Identify affected routes, tenants, payload sizes, and deployment versions.
- Split request time using traces: middleware, application, database, cache, external APIs, serialization.
- Check CPU, memory, event-loop lag, worker saturation, DB-pool wait time, query latency, and downstream latency.
- Inspect query count for N+1 behavior and query plans for regressions.
- Check timeouts, retries, and retry amplification.

Possible mitigations only after evidence:

- Roll back a bad release.
- Disable an expensive feature.
- Apply a timeout or circuit breaker to a degraded dependency.
- Repair an index/query or remove N+1 access.
- Bound concurrency.
- Add capacity when actual resource saturation justifies it.
- Cache only when staleness and invalidation are understood.

### Scenario 2: API is fast locally but slow in production

- Production data volume and skew
- Missing production index
- Network and TLS latency
- Connection-pool waits
- Multiple workers and memory duplication
- Cold starts
- External dependency geography
- Debug logging or serialization overhead

### Scenario 3: Async FastAPI endpoint blocks other requests

- Blocking database/client library inside `async def`
- File or CPU work on the event loop
- Synchronous DNS or SDK behavior
- Event-loop lag measurement
- Move blocking I/O to appropriate sync route/thread boundary
- Move CPU-heavy work to worker/process boundary

### Scenario 4: Database connection pool exhaustion

- Leaked sessions/connections
- Transactions held open during network calls
- Slow queries increasing checkout duration
- Worker count multiplied by per-worker pool size
- Unbounded request concurrency
- Pool timeout and saturation metrics
- Correct session-per-request/task cleanup

### Scenario 5: Database CPU rises and endpoints time out

- Slow-query log and `pg_stat_statements`
- `EXPLAIN (ANALYZE, BUFFERS)`
- Sequential scans, bad estimates, stale statistics
- N+1 queries
- Lock waits and long transactions
- Excessive indexes slowing writes
- Pagination and unbounded result sets

### Scenario 6: Error rate rises after deployment

- Compare version dimensions and recent migrations/config changes
- Rollback versus forward-fix decision
- Schema/application compatibility during rolling deploys
- Feature flags
- Error classification instead of raw 500 counts
- Migration run-once safety

### Scenario 7: Downstream provider is slow or failing

- Explicit connect/read/total deadlines
- Bounded retries with backoff and jitter
- Retry only safe/idempotent operations
- Circuit breaker
- Bulkhead or semaphore isolation
- Degraded response/fallback
- Avoid synchronized retry storms

### Scenario 8: Redis or cache failure

- Cache is an optimization unless explicitly authoritative
- Fall back without overwhelming PostgreSQL
- Stampede protection
- TTL jitter
- Hot-key detection
- Stale-data policy
- Invalidation correctness

### Scenario 9: Worker queue backlog grows

- Arrival rate versus processing rate
- Oldest-message age, not queue length alone
- Poison messages and retry loops
- Worker saturation and downstream bottlenecks
- Scaling consumers only when dependencies can absorb load
- Backpressure and admission control
- Dead-letter handling

### Scenario 10: Duplicate jobs or payments

- At-least-once delivery
- Lost client response followed by retry
- Idempotency-key persistence and uniqueness
- Consumer deduplication
- Transactional outbox
- Never rely on an in-memory “already processed” set across replicas

### Scenario 11: Memory usage continuously grows

- Request-correlated memory profiling
- Unbounded caches and collections
- Large response/materialization behavior
- Task/session/reference leaks
- Worker recycling as mitigation, not root-cause fix
- Streaming and bounded buffers

### Scenario 12: One tenant causes platform degradation

- Per-tenant metrics and cardinality discipline
- Quotas and rate limits
- Fair scheduling
- Bulkheads
- Payload and concurrency limits
- Noisy-neighbor isolation

### Scenario 13: AI provider latency and cost spike

- Token/input/output distributions
- Model and prompt-version dimensions
- Streaming time-to-first-token versus total latency
- Provider rate-limit headers
- Request cancellation propagation
- Budget enforcement
- Fallback model policy
- Cache safety and prompt/data privacy

### Scenario 14: Security incident or suspected data leak

- Contain access and rotate affected secrets
- Preserve evidence and audit logs
- Determine tenant/object-level authorization scope
- Revoke tokens/sessions as required
- Avoid leaking more sensitive data through debugging
- Patch, test, deploy, and perform post-incident prevention work

### Scenario drill format

Each week includes at least two 20-30 minute drills:

```text
Codex provides symptoms and incomplete telemetry.
Jatin asks for specific evidence.
Codex reveals only requested evidence.
Jatin produces a ranked hypothesis list.
Jatin chooses immediate mitigation.
Jatin proposes root-cause validation and permanent correction.
```

Scoring:

- Avoids premature conclusions
- Prioritizes customer-impact mitigation
- Uses observability signals correctly
- Understands concurrency and resource saturation
- Chooses safe rollback/retry behavior
- Produces concrete prevention and verification

## External API, Webhook, And OpenAI Integration Track

This track also runs throughout the sprint. Integrations are treated as unreliable distributed boundaries, not as simple SDK calls.

### Outbound HTTP API client

Required competencies:

- Typed request and response contracts
- One reusable client with connection pooling
- Explicit connect, read, write, pool, and total timeout budgets
- Authentication headers without logging secrets
- Response-status classification
- Safe handling of malformed or oversized responses
- Retry only transient and idempotent operations
- Exponential backoff and jitter
- Rate-limit headers and `Retry-After`
- Circuit breaking and bounded concurrency
- Cancellation propagation
- Correlation IDs and trace propagation
- Metrics by provider, operation, status class, and latency
- Provider adapter interface so domain/services do not depend on SDK response shapes

Pair-coding integrations:

1. Weather/payment-style REST client using HTTPX
2. Concurrent fan-out to two providers with one deadline
3. Provider fallback without duplicating side effects
4. Contract test using a controlled fake HTTP server

### Inbound webhook receiver

A production webhook endpoint must handle:

- Raw request-body preservation for signature verification
- Signature and timestamp verification before trusting/parsing the event
- Replay-window protection
- Stable provider event ID
- Unique database constraint for deduplication
- At-least-once and out-of-order delivery
- Fast `2xx` acknowledgement
- Durable enqueue/persistence before acknowledgement when required
- Non-trivial work in a background worker, not inside the webhook request
- Safe handling of unknown event types
- Event-version evolution
- Secret rotation
- Auditable processing status and retry/dead-letter behavior

Required webhook exercise:

```text
POST /webhooks/provider
-> verify raw-body signature
-> persist provider event id uniquely
-> acknowledge duplicate events safely
-> enqueue processing
-> return promptly
```

Failure tests:

- Invalid signature
- Stale timestamp/replay
- Duplicate delivery
- Event received out of order
- Database unavailable before acknowledgement
- Worker fails after acknowledgement
- Unknown event type

### OpenAI provider integration

The capstone will include an OpenAI adapter using the current official Python SDK and Responses API concepts.

API-key rules:

```text
OPENAI_API_KEY is a server-side secret.
It is loaded from environment/secret management.
It is never committed to Git.
It is never returned to clients.
It is never embedded in browser/mobile code.
It is redacted from logs and traces.
```

Production client concerns:

- Provider adapter boundary instead of SDK calls in route handlers
- Model/config selection outside business code
- Explicit deadlines
- Bounded retries for safe failures
- Provider request IDs in logs
- Rate-limit handling
- Streaming event lifecycle
- Client disconnect and cancellation behavior
- Input/output token and cost accounting
- Maximum input/output limits
- PII and tenant-data handling
- Prompt and model-version tracking
- Response validation and structured outputs where appropriate
- Test doubles that never consume real API quota
- Graceful provider degradation/fallback policy

OpenAI exercises:

1. Non-streaming provider adapter invoked from an application service
2. FastAPI SSE endpoint that relays streamed response events
3. Cancellation when the client disconnects
4. Usage and cost persistence
5. Provider timeout and rate-limit tests using a fake client
6. OpenAI webhook receiver with signature verification and deduplication

The official SDK reads `OPENAI_API_KEY` from the environment. OpenAI webhook handlers must verify signatures using the webhook signing secret and should acknowledge quickly while offloading non-trivial processing. Streaming is treated as a sequence of typed lifecycle events rather than concatenating arbitrary chunks.

## Weekly Deliverables

Every week must produce:

- Working code
- Automated tests
- One architecture/design note
- One production failure analysis
- Two production scenario/incident drills
- At least one integration failure or contract test from Week 2 onward
- One timed pair-coding result
- Updated gap list
- Short verbal revision without reading notes

## Scoring Rubric

Score each dimension from 0 to 4.

```text
0 = cannot begin
1 = needs major prompting
2 = workable but misses important failures
3 = interview-ready for expected level
4 = strong, production-aware, and clearly explained
```

Dimensions:

- Requirement clarification
- Python correctness
- API and HTTP design
- Data modeling and SQL
- Concurrency and transactions
- Testing
- Security
- Reliability and observability
- Code organization
- Communication and tradeoffs

Interview-ready threshold:

```text
No dimension below 2
Core dimensions at 3 or higher
Overall average at least 3
Two consecutive mocks passed without rescue
```

Core dimensions are Python correctness, API/HTTP design, persistence, testing, and communication.

## Production Review Checklist

Use this on every feature.

### Correctness

- Are invariants explicit?
- Are retries safe?
- Is the transaction boundary correct?
- What happens under duplicate or concurrent requests?

### Security

- Is authentication required?
- Is authorization checked on the target object?
- Can input reach SQL, files, URLs, or subprocesses unsafely?
- Are secrets or PII exposed?

### Performance

- What is the complexity?
- Is there an N+1 query?
- Are queries indexed for their access paths?
- Is blocking I/O running on the event loop?
- Are pools and concurrency bounded?

### Reliability

- Are timeouts defined?
- Are retries bounded and safe?
- Does cleanup run on cancellation/failure?
- Can partial state survive?

### Observability

- Can one request/job be traced end to end?
- Are failures classified?
- Are latency and saturation measured?
- Will an alert be actionable?

### Maintainability

- Does each component have one clear reason to change?
- Are framework, domain, and persistence concerns separated appropriately?
- Are interfaces justified by replaceability or testing needs?
- Is complexity solving a current requirement?

## Official Reference Baseline

- FastAPI dependencies: https://fastapi.tiangolo.com/tutorial/dependencies/
- FastAPI concurrency and async: https://fastapi.tiangolo.com/async/
- FastAPI testing: https://fastapi.tiangolo.com/tutorial/testing/
- FastAPI deployment concepts: https://fastapi.tiangolo.com/deployment/concepts/
- Python documentation: https://docs.python.org/3/
- SQLAlchemy session basics: https://docs.sqlalchemy.org/en/20/orm/session_basics.html
- SQLAlchemy transaction management: https://docs.sqlalchemy.org/en/20/orm/session_transaction.html
- PostgreSQL documentation: https://www.postgresql.org/docs/current/
- OpenAI developer quickstart: https://developers.openai.com/api/docs/quickstart
- OpenAI streaming responses: https://developers.openai.com/api/docs/guides/streaming-responses
- OpenAI webhooks: https://developers.openai.com/api/docs/guides/webhooks

## Immediate Starting Point

Run the Day 1 diagnostic without revising first.

The first live task is the Python job-scheduler diagnostic. Its result determines whether Week 1 starts at full speed or compresses directly into async/FastAPI and persistence.
