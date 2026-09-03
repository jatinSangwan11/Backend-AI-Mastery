# LLD Catalog

This is the locked Low-Level Design pattern catalog for Backend AI Mastery.

The goal is not to memorize pattern definitions or force every pattern into every project. A pattern is learned through real design pressure and is considered complete only when Jatin can explain:

1. What problem or pressure caused it.
2. Which responsibility it separates.
3. What simpler alternative could be used.
4. What complexity and tradeoffs it introduces.
5. When it should not be used.

## Completed Patterns

### Repository

Learned in Phase 2, Project 04: Inventory and Order Management.

```text
Business services own workflows and decisions.
Repositories own persistence lookup/save mechanics.
```

### Unit of Work

Learned in Phase 2, Project 04: Inventory and Order Management.

```text
One transaction boundary coordinates related repository changes
and commits or rolls them back as one unit.
```

## Core LLD Interview Patterns

These are the highest-priority remaining patterns for object-oriented and backend LLD interviews.

### Strategy

Use interchangeable algorithms or policies without changing the workflow that uses them.

Likely pressures:

- Pricing and discount policies
- Payment selection
- Routing
- Cache eviction
- Seat allocation

### Factory And Abstract Factory

Centralize selection or construction of concrete collaborators and related object families.

Likely pressures:

- Payment-provider construction
- Notification-channel creation
- Repository/Unit of Work construction
- Environment-specific implementations

### Adapter

Translate an external or incompatible interface into the contract expected by the application.

Likely pressures:

- Payment providers
- Shipping providers
- Notification vendors
- External AI services

### State

Move lifecycle-dependent behavior behind explicit state representations when conditionals become difficult to maintain.

Likely pressures:

- Order lifecycle
- Movie-ticket lifecycle
- Elevator
- Vending machine
- Delivery workflow

### Command

Represent an action as an object so it can be queued, logged, retried, scheduled, or undone.

Likely pressures:

- Place order
- Cancel order
- Process payment
- Background jobs

### Observer / Publisher-Subscriber

Notify interested components when a domain event occurs without making the source directly coordinate every reaction.

Likely pressures:

- Order-placed notification
- Inventory events
- Payment completion
- Audit and analytics reactions

### Decorator

Wrap an existing collaborator to add behavior without changing its core implementation.

Likely pressures:

- Logging
- Metrics
- Authorization
- Caching
- Retry behavior

### Template Method

Define a shared workflow skeleton while allowing selected steps to vary.

Likely pressures:

- Provider workflows with common stages
- Import and processing pipelines
- Similar checkout flows

### Chain Of Responsibility

Pass a request through a sequence of handlers, each of which may validate, handle, reject, or forward it.

Likely pressures:

- Request validation
- Authorization
- Fraud checks
- Checkout eligibility

### Specification

Represent business rules as composable predicates or eligibility objects.

Likely pressures:

- Product is active
- Inventory is sufficient
- Discount eligibility
- Search and filtering rules

### Builder

Construct complex objects incrementally when one constructor would have too many optional or conditional inputs.

Likely pressures:

- Checkout construction
- Complex search requests
- Configurable test data

### Facade

Expose a small, cohesive interface over several complicated subsystems.

Likely pressures:

- Checkout coordinating inventory, payment, order, and notification
- Simplifying external callers' access to a subsystem

## Important Structural Patterns

### Composite

Treat individual objects and groups through the same interface.

Likely pressures:

- Filesystems
- Menus
- Organizational hierarchies
- Nested product bundles

### Proxy

Stand in for another object to control access, loading, caching, or remote communication.

Likely pressures:

- Lazy loading
- Authorization
- Caching
- Remote-service clients

### Mediator

Coordinate interactions among several components without connecting every component directly to every other component.

### Bridge

Separate an abstraction from its implementation so both dimensions can vary independently.

## Persistence And Backend Patterns

### Data Mapper

Translate between persistence records and domain objects while keeping persistence behavior outside the domain objects.

### Identity Map

Ensure that one database row is represented by one in-memory object within a persistence session.

### Transaction Script

Implement a use case as a direct procedural transaction. Learn it as a valid simpler alternative and as a comparison with richer domain/service designs.

### Active Record

Place persistence operations on the data model itself. Learn its convenience and its coupling tradeoffs compared with Repository and Data Mapper.

### Optimistic Locking

Detect concurrent updates using a version or previously observed value instead of locking before work begins.

### Pessimistic Locking

Lock shared database rows before modifying them when concurrent access must be serialized.

## Advanced Distributed Backend Patterns

These belong mainly in Phase 3 and Phase 4 rather than being forced into Phase 2 LLD projects.

### Transactional Outbox

Persist a business change and its outgoing event in the same database transaction, then publish the event asynchronously.

### Saga

Coordinate a distributed business operation using multiple local transactions and compensating actions.

### CQRS

Separate command/write models from query/read models when their requirements materially diverge.

### Event Sourcing

Store state-changing events as the source of truth and derive current state from them.

### Circuit Breaker

Stop repeatedly calling an unhealthy dependency and allow controlled recovery attempts.

### Retry With Exponential Backoff

Retry transient failures with increasing delays and clear retry-safety/idempotency rules.

### Bulkhead

Isolate resources so failure or overload in one area does not consume the entire system.

### Cache-Aside

Let application code load missing data from the source and populate the cache explicitly.

### Idempotent Consumer

Ensure repeated delivery of the same message does not repeat its intended side effects.

### Dead Letter Queue

Move repeatedly failing messages aside for inspection or later repair.

### Distributed Locking And Leader Election

Coordinate work across processes or machines when exactly one participant should own a critical activity at a time.

## Patterns To Understand Without Forcing

### Singleton

Learn mostly as a caution around global mutable state, hidden dependencies, shared database sessions, and difficult tests.

### Service Locator

Understand how globally locating dependencies can hide a component's real requirements.

### Lower-Priority Specialized Patterns

- Memento
- Flyweight
- Prototype
- Visitor
- Interpreter

These should be learned when a project creates genuine pressure for them rather than delaying the core backend curriculum.

## SOLID Checkpoint

Explicitly learned:

- Single Responsibility Principle
- Dependency Inversion Principle

Still to cover explicitly:

- Open/Closed Principle
- Liskov Substitution Principle
- Interface Segregation Principle

## Curriculum Placement

### Phase 2

Prioritize:

- Repository
- Unit of Work
- Strategy
- Factory
- Adapter
- State
- Command
- Observer / Publisher-Subscriber
- Decorator
- Template Method
- Chain of Responsibility
- Specification
- Builder
- Facade
- Proxy
- Composite
- Database locking patterns

### Phase 3 And Phase 4

Prioritize:

- Transactional Outbox
- Saga
- Circuit Breaker
- Retry
- Bulkhead
- Cache-Aside
- CQRS basics
- Event Sourcing basics
- Idempotent Consumer
- Dead Letter Queue
- Distributed locking and leader election

## Interview Standard

Pattern recall alone is insufficient. For an LLD interview, practice this sequence:

```text
clarify requirements
identify invariants and lifecycle
assign responsibilities
design contracts and relationships
produce a simple working design
identify the new pressure
apply a pattern only if justified
explain its tradeoffs and alternatives
```

The pattern name is interview vocabulary. The reasoning that justifies or rejects it is the actual design skill.
