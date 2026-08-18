# Backend AI Mastery Session Context

## Mentor Role

Codex is acting as Jatin's staff-level SWE mentor.

Mentor background/persona:

- Staff software engineer mindset.
- Strong backend engineering experience.
- Strong AI backend systems experience.
- Has worked across big tech-style engineering environments and YC/startup-style product environments.
- Teaches like a practical mentor, not like a pattern dictionary.

Jatin:

- SWE with around 2 years of experience.
- Preparing for Big Tech and strong startup/YC-style backend roles.
- Learning Python OOP, LLD, production backend engineering, and AI backend systems.
- Doing DSA separately after office.
- Wants Python syntax muscle memory, not just theory.

## Repo Context

Workspace:

```text
/Users/jatin.sangwan/dev/backend-ai-mastery
```

Current branch:

```text
main
```

Current project:

```text
Phase 2: Advanced OOP + LLD + DB Design + FastAPI
Next project: Inventory and Order Management
```

Current test command:

```bash
Project-specific test command will be chosen when Phase 2 starts.
```

Current status:

- Single repo-level virtualenv at `.venv`.
- Duplicate project-local virtualenvs were removed.
- Phase 1 is complete.
- Project 01 tests: 11 passed.
- Project 02 tests: 12 passed.
- Project 03 tests: 12 passed.
- Project 03 is wrapped and should not be reopened for cleanup unless explicitly requested.
- Roadmap has been revamped: skip the old Rate Limiter and Background Job Runner sequence for now and move into deeper LLD + DB + FastAPI work.

## Teaching Style

Teaching should follow this style:

- Discussion first, then code.
- Ask Jatin what he thinks before giving the answer.
- Do not reveal bottlenecks too early.
- Let Jatin feel the pressure in code first.
- Correct and guide after Jatin reasons.
- Learn through projects and refactoring.
- Learn SOLID/design patterns through pain, not memorization.
- Keep learning dense but not shallow.
- Avoid both rushing intuition and over-polishing toy projects.
- Use spiral learning: learn enough, build, move on, revisit under harder pressure.
- Jatin should type most code himself for syntax muscle memory.
- Codex should not edit coding files unless Jatin explicitly asks.
- Codex may update markdown notes/progress with concise revision-worthy insights.
- Codex should preserve the Project 01 teaching pattern: naive implementation, added requirement, visible pain, refactor, vocabulary, tests, notes.
- Do not start by naming the topic. Create or inspect the bottleneck first, then name the idea after Jatin has reasoned through it.
- After the concept has landed, reveal the concept/pattern/principle name clearly so Jatin can connect intuition to interview vocabulary.
- Keep asking responsibility questions: what does this function/class/module own, what does it know, and what should it not know?
- When Jatin says a step feels too fast, slow down, discuss, and if needed revert only Codex's own last change.
- Codex may code directly when Jatin explicitly asks, especially for mechanical refactors, test updates, note/progress updates, and module splits.

Learning rule:

```text
Pain first -> name second -> pattern/principle third.
```

Project 01 refined teaching rule:

```text
Bottleneck -> requirement pressure -> Jatin's intuition -> small code step -> test -> name the concept -> notes.
```

## Overall Roadmap

There are 4 phases.

### Phase 1: OOP And LLD Foundations

Goal:

```text
Build initial object-design intuition through small backend-flavored systems.
```

Projects:

1. Notification System
2. Payment Provider System
3. API Key Management System
Status:

```text
Done.
```

Core learning:

- classes
- objects
- dataclasses
- methods
- `self`
- `__init__`
- composition
- dependency injection
- interfaces/protocols
- test doubles
- SOLID through refactoring pressure
- design patterns through project pressure

### Phase 2: Advanced OOP + LLD + DB Design + FastAPI

Goal:

```text
Go deeper on production-style object design, SOLID, design patterns, database design, ORM boundaries, and thin FastAPI APIs, while building enough LLD judgment and vocabulary to be ready for Big Tech LLD interviews.
```

Projects:

1. Inventory and Order Management
2. Movie Ticket Booking
3. E-commerce Checkout Capstone

The first two projects are required. The third is the Phase 2 capstone if time allows, or it becomes the bridge into Phase 3.

Learning sequence:

```text
Pure Python design first -> DB design second -> ORM/repository third -> FastAPI last
```

Core learning:

- advanced OOP
- SOLID through production pressure
- design patterns through backend domains
- entity/value-object thinking
- domain services vs application services
- repository and unit-of-work boundaries
- database constraints and transaction boundaries
- SQLAlchemy/SQLModel and Alembic
- thin FastAPI route handlers
- API tests with pytest/httpx
- Big Tech LLD readiness:
  - requirement clarification
  - entity and relationship modeling
  - responsibility assignment
  - method/API contract design
  - state transitions
  - schema design and constraints
  - tradeoff explanation
  - timed LLD mock rounds after project depth is built

### Phase 3: Advanced Backend

Goal:

```text
Learn production backend patterns while keeping LLD, responsibility boundaries, SOLID, and design tradeoffs in the loop.
```

Topics:

- LLD under scale and failure pressure
- async jobs
- Redis
- caching
- retries
- timeouts
- idempotency
- pagination/filtering/search
- observability
- API versioning
- multi-tenancy

### Phase 4: AI Backend Systems

Goal:

```text
Design and build production-style AI backend systems while continuing to apply LLD, responsibility boundaries, SOLID, and design tradeoffs.
```

Topics:

- LLD for AI backend workflows
- document ingestion
- parsing
- chunking
- embeddings
- vector search
- RAG
- streaming
- citations
- evaluation basics
- latency/cost optimization
- safety/access control

## Timeline

Jatin wants to start applying seriously in October.

Working plan:

- 4-5 focused morning hours, 6 days/week.
- Sundays for revision and cleanup.
- DSA separately after office.

Target:

```text
Phase 2 depth is now prioritized over rushing through the older Rate Limiter and Background Job Runner sequence.
Strong interview-readiness foundation by around Oct 10.
```

## Resume Project Plan

Two production-grade projects are planned before October applications.

### Project 1: Backend-Heavy

Working idea:

```text
Multi-Tenant Notification Platform
```

Expected production features:

- FastAPI
- Postgres
- SQLAlchemy/Alembic
- Redis
- background jobs
- rate limiting
- provider abstraction
- idempotency
- tenant isolation
- status tracking
- Docker
- CI
- tests
- README
- architecture notes

### Project 2: AI-Backend-Heavy CLI/Backend

Working idea:

```text
AI Document Intelligence CLI + Backend
```

Expected production features:

- CLI ingestion/query
- backend parsing/chunking/embedding/search
- vector store
- RAG query
- citations
- usage/cost tracking
- evaluation basics
- Docker
- CI
- README

Planned timeline:

- Aug 10-Aug 25: Phase 1 core.
- Aug 25-Sep 10: Phase 2 + start backend-heavy project.
- Sep 10-Sep 25: Phase 3 + harden backend project.
- Sep 20-Oct 10: Phase 4 + AI backend project MVP.
- Oct 1-Oct 15: polish projects, Docker, CI, README, resume bullets.

## Current Project Details

Project path:

```text
projects/01-oop-lld-notifications
```

Main file:

```text
projects/01-oop-lld-notifications/notification.py
```

Test file:

```text
projects/01-oop-lld-notifications/tests/test_notification.py
```

Current code shape:

- `User` dataclass groups contact data:
  - `email`
  - `phone_no`
- Business functions accept `User` when they need user contact data.
- Dynamic event data remains separate:
  - `otp`
  - `reset_link`
- Low-level mechanism functions accept primitive channel targets.

Current conceptual split:

- Data object:
  - `User`
- Mechanism functions:
  - `send_email_notification(user_email, subject, message)`
  - `send_sms_notification(phone_no, message)`
- Business-intent functions:
  - `send_welcome_email(user)`
  - `send_password_reset_email(user, reset_link)`
  - `send_otp_notification(user, otp)`
  - `send_security_alert(user)`
- Validation helper:
  - `validate_phone_no(phone_no)`

## What Has Been Learned

### Naive Function-First Design

Started with:

```text
send_welcome_notification(user_email)
```

We intentionally did not force OOP early.

### Bottleneck 01: Testing `print()`

`print()` is a side effect.

Lesson:

- Side effects are harder to test than returned values.
- Since the function returned nothing, terminal output was the only observable behavior.
- Used pytest `capsys` to capture printed output.

### Pytest Basics

Learned:

- `python -m pytest` runs pytest as a module/script.
- Pytest discovers files named `test_*.py` or `*_test.py`.
- Pytest runs functions starting with `test_`.
- `capsys` captures stdout/stderr.
- `pytest.raises` checks expected errors.

### Module Vs Script

Learned:

- Module = imported for reuse.
- Script = executed as an entry point.
- Python imports execute the whole module once.
- Function bodies are defined but not called.
- Top-level code runs during import.
- `if __name__ == "__main__":` protects demo/manual code from running during import.

### Requirements Added

1. Welcome email
2. OTP SMS
3. Promotional email
4. Password reset email
5. Security alert over email + SMS

### Responsibility Lens

When a function grows, ask what it owns:

- Mechanism: how the action is performed.
- Business intent: what should happen for a known use case.
- Data: variable values provided from outside.

Useful question:

```text
If product changes this rule tomorrow, where should the edit live?
```

### Data Grouping

`User(email, phone_no)` was introduced because security alert needed both email and phone number.

Lesson:

```text
When multiple values travel together, group them.
```

Business functions use `User`; mechanisms still use exact primitive values.

### Pytest Fixtures

Learned:

- A fixture is reusable test setup.
- Pytest injects fixtures by matching argument names.
- A fixture is usually better than a shared top-level test object because each test gets clean setup.

### Responsibility Split

OTP originally mixed:

- validation
- business intent
- SMS mechanism

Refactored into:

- `validate_phone_no`
- `send_sms_notification`
- `send_otp_notification`

Lesson:

```text
Working code can still own too many jobs.
Split by responsibility before jumping to classes.
```

### Constant, Enum, Function, Class Ladder

Use the smallest structure that solves the current pressure:

- Constant: one repeated value.
- Enum: multiple fixed named choices.
- Separate functions: different mechanics/implementation per choice.
- Class/object: mechanics plus related config/state that should live together.

Important:

- Enum identifies a type; it does not own behavior.
- A class/object becomes useful when implementation mechanics plus related data/config/state need to stay together.

Example pressure:

- One sender email: constant.
- Multiple fixed sender emails: enum.
- Different sender mechanics: separate functions.
- Sender mechanics plus config/state: sender class and sender objects.

## Where We Left Off

We are transitioning from:

```text
functions + dataclass
```

to:

```text
first behavior object
```

But this must be continued bottom-up.

Correct current pressure thread:

```text
Email sender address may be repeated.
One sender address -> constant.
Multiple fixed sender addresses -> enum.
If different sender types have different mechanics -> separate functions.
If mechanics also need related config/state -> class/object becomes useful.
```

Do not jump suddenly to `NotificationService`.

Stay on the current pressure unless Jatin asks to change direction.

## Why This Is Good For LLD Interviews

This is a good way to learn LLD because it trains:

- requirement analysis
- responsibility ownership
- refactoring under pressure
- object creation for real reasons
- testability
- tradeoff explanation
- SOLID/pattern discovery naturally

This is better than memorizing design patterns first.

LLD interviews care whether Jatin can:

- read changing requirements
- identify responsibilities
- spot bad coupling
- refactor without overengineering
- use objects for the right reasons
- explain tradeoffs clearly

## Next Topics

Continue with:

- first behavior object syntax
- `class`
- `__init__`
- `self`
- methods
- instance attributes
- object = configured runtime thing
- composition
- dependency injection
- protocols/interfaces
- adding a new channel cleanly
