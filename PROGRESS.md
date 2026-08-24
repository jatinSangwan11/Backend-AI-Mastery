# Progress

## 2026-08-03

Initialized the long-running coaching workspace at:

```text
/Users/jatin.sangwan/dev/backend-ai-mastery
```

Current focus:

- Phase 1: Python OOP and LLD
- Project 01: notification system

Workspace reset:

- Deleted the premature notification-system scaffold.
- Removed duplicate project-local virtual environments.
- Created one repo-level Python 3.11.7 virtual environment at `.venv`.
- Kept an empty project folder at `projects/01-oop-lld-notifications/` so we can build from scratch.

Next step:

- Design the notification system from first principles.
- Create production-style project structure intentionally.
- Implement the first thin slice with tests.
- Refactor after we understand the tradeoffs.

Session update:

- Started Phase 1.1 on branch `Phase-1.1`.
- Wrote the first naive implementation as a single function:
  `projects/01-oop-lld-notifications/notification.py`.
- Added one pytest test using `capsys` to capture printed output.
- Installed pytest in the single repo-level `.venv`.
- Recorded pytest in `requirements-dev.txt`.
- Ran the test suite for project 01: 1 test passed.

Current learning bottleneck:

- The function works, but its only observable behavior is `print()` output.
- Used pytest's `capsys` fixture to capture printed output and assert on it.
- Lesson: `print()` is a side effect; side effects are testable, but they create design pressure toward cleaner behavior boundaries.

Session update:

- Added a second notification type: OTP over SMS.
- Learned that Python imports execute the whole module once before selecting imported names.
- Introduced `if __name__ == "__main__":` to keep demo/manual code from running during imports.
- Current pressure: multiple notification functions are still fine, but repeated validation/formatting/delivery behavior may soon become uncomfortable.

Session update:

- Added a promotional email test using the generic email notification function.
- Clarified the responsibility lens: mechanism vs business intent vs caller-provided data.
- Current design idea: generic email sending can own delivery, while standard notifications may use small wrapper functions to own fixed subject/message.

Session update:

- Added standard welcome and password reset email functions on top of the generic email mechanism.
- Split OTP notification into validation, SMS mechanism, and OTP orchestration responsibilities.
- Learned not to catch validation exceptions when tests/callers need to observe them.
- Ran project tests: 7 passed.

## 2026-08-11

Session update:

- Clarified the shared vocabulary for the notification project: event data, stable config, mechanism, business intent, data object, and behavior object.
- Added sender-email stable config to the email mechanism using constants.
- Mapped sender emails by business intent:
  - welcome email uses `MARKETING_SENDER_EMAIL`
  - password reset email uses `SUPPORT_SENDER_EMAIL`
  - security alert uses `SECURITY_SENDER_EMAIL`
- Reinforced that business-intent functions decide product rules, then call lower-level mechanism functions with the required arguments.
- Noted the next design pressure: `send_email_notification(user_email, subject, message, sender_email)` now mixes send-time data with stable config, which prepares the ground for a future `EmailSender` behavior object if more config appears.
- Ran project tests: 8 passed.

Session update:

- Introduced the first behavior objects:
  - `EmailSender`
  - `SmsSender`
  - `PushSender`
- Practiced the core OOP split: stable config goes into `__init__`; event/send-time data stays as method arguments.
- Moved phone validation into `SmsSender.send(...)` so SMS callers do not have to remember validation.
- Added push notification support for security alerts using `device_token` on `User` and `FCM_PROVIDER` as stable config.
- First added push naively to make `send_security_alert` visibly crowded.
- Refactored security alert delivery behind a common `notify(user)` abstraction:
  - `SecurityEmailAlertChannel`
  - `SecuritySmsAlertChannel`
  - `SecurityPushAlertChannel`
- Learned composition through the wrapper objects: each security-alert channel has a lower-level sender.
- Current `send_security_alert(user)` now loops over configured security-alert channels instead of knowing each channel's argument details.
- Ran project tests: 8 passed.

Session update:

- Added `SecurityAlertChannel` as a `Protocol` to name the common `notify(user)` contract.
- Annotated `security_alert_channels` as `list[SecurityAlertChannel]`.
- Clarified that protocol conformance is structural: classes do not need to inherit from the protocol; they satisfy it by having the required method shape.
- Learned the distinction between runtime behavior and static typing: plain Python mostly does not enforce protocol membership at runtime, but editors/type checkers can use the contract.
- Current reading: `security_alert_channels` is expected to contain objects that satisfy the `SecurityAlertChannel` protocol.

Session update:

- Discussed the runtime limitation of protocols: a bad object can still enter the list at runtime and fail only when called.
- Added the mental model for explicit runtime guards using `getattr(channel, "notify", None)` and `callable(...)`.
- Clarified that the `None` in `getattr(..., None)` is a fallback when the attribute is missing, not the return type of `notify`.
- Learned how to test module-level configuration safely with `monkeypatch.setattr`.
- Key test idea: temporarily replace `notification.security_alert_channels` with `["oops"]` to verify the invalid-channel error path, then let pytest restore the original value.

## 2026-08-12

Session update:

- Introduced user/use-case channel preferences for security alerts.
- Split the security-alert inputs into:
  - configured channels: what the system can send through
  - enabled channels: what this user/use case allows
- Added channel identity constants such as `EMAIL_CHANNEL`, `SMS_CHANNEL`, and `PUSH_CHANNEL`.
- Extended `SecurityAlertChannel` to include `channel_type`.
- Changed `send_security_alert` so configured channels and enabled channels are passed explicitly instead of relying on the module-level global list.
- Added a test proving disabled channels are skipped: email + push enabled means SMS is not sent.
- Reinforced the dependency idea without naming it first: if a function needs collaborators to do its job, make those collaborators visible in the function signature.
- Ran project tests: 10 passed.

Session update:

- Converted security-alert sending into a configured workflow object: `SecurityAlertNotifier`.
- Used constructor injection: configured security-alert channels are passed into `SecurityAlertNotifier.__init__`.
- Kept event/use-case data as method arguments: `user` and `enabled_channels` are passed to `notify(...)`.
- Added a fake security-alert channel test double to verify notifier workflow without relying on `print()` output.
- Learned that test doubles are useful when testing orchestration rather than real side effects.
- Split the growing `notification.py` learning file into focused modules:
  - `models.py`
  - `constants.py`
  - `senders.py`
  - `security_alerts.py`
  - `notification.py`
- Current Project 01 checkpoint: behavior is preserved, module ownership is clearer, and tests pass.
- Ran project tests: 11 passed.

Closing statement:

- Project 01 is ready for weekend responsibility revision.
- Remaining cleanup is intentionally deferred unless it blocks learning.
- Next project direction: Project 02, Payment Provider System, to revisit these same ideas under provider/payment pressure.

Session update:

- Started Phase 1, Project 02: Payment Provider System.
- Clarified where the payment system fits in a backend pipeline:
  - product/order flow already knows the user, item, and price
  - payment system receives a valid user/payment request and tries to collect money
  - external providers such as Stripe/Razorpay sit outside our system
  - order/product flow later uses payment result to unlock/mark the purchase
- Clarified "charge a user" as: ask the payment system/provider to collect money for a user and amount.
- Created the first intentionally naive slice:
  - `projects/02-oop-lld-payments/payment.py`
  - `projects/02-oop-lld-payments/tests/test_payment.py`
- First function:
  - `charge_payment(user_id: str, amount: int) -> None`
  - currently only prints the charge action; it does not move real money or call a real provider
- First test uses `capsys` to assert the printed charge message.
- Current responsibility checkpoint: `charge_payment` owns only the basic "start a charge for this user and amount" action. It does not yet own provider choice, payment method, success/failure, retries, idempotency, database records, or real money movement.
- Ran project 02 tests: 1 passed.

Session update:

- Added the next pressure: payments can go through more than one provider, currently Stripe and Razorpay.
- First saw the naive `if/elif` shape inside `charge_payment`, where one function owned:
  - starting the payment charge flow
  - choosing the provider branch
  - knowing provider-specific charging behavior
- Discussed why this becomes painful as providers increase:
  - every new provider forces edits to the central payment function
  - the function becomes a place where too much provider knowledge accumulates
  - provider-specific behavior becomes more prone to developer mistakes
- Refactored to separate responsibilities:
  - `charge_payment(...)` owns the payment flow
  - `get_payment_provider(...)` owns provider selection by name
  - `StripePaymentProvider.charge(...)` owns Stripe charging behavior
  - `RazorpayPaymentProvider.charge(...)` owns Razorpay charging behavior
- Important nuance: the `if` did not disappear yet. It moved into a smaller function whose only responsibility is provider selection.
- Added tests for Stripe, Razorpay, and unsupported provider error behavior.
- Ran project 02 tests: 3 passed.

Session update:

- Added the next pressure: the caller needs to know whether the payment succeeded or failed.
- Changed provider `.charge(...)` methods so they still print the provider action, but now also return a provider-level result dict.
- Current provider result shape:
  - `status`
  - `provider_name`
  - `provider_message`
- Changed `charge_payment(...)` to return an app-level result dict:
  - success provider result becomes `{"status": "success", "message": "Payment successful"}`
  - failed provider result becomes `{"status": "failed", "message": "Payment failed"}`
- Responsibility checkpoint:
  - provider `.charge(...)` owns provider-level charging behavior and provider-level outcome
  - `charge_payment(...)` owns flow coordination and conversion into the app-level payment result
- Kept results as dicts intentionally; dataclasses may come later if repeated dict keys/stringly-typed access becomes painful.
- Updated tests to assert both printed provider behavior and returned app-level payment result.
- Ran project 02 tests: 3 passed.

## 2026-08-13

Session update:

- Picked up Project 02 from the clean checkpoint.
- Added the next pressure: provider result dicts depend on repeated string keys such as `status`, `provider_name`, and `provider_message`.
- Introduced `PaymentResult` as a dataclass to give provider results a named shape.
- Changed `StripePaymentProvider.charge(...)` and `RazorpayPaymentProvider.charge(...)` to return `PaymentResult` instead of plain dicts.
- Changed `charge_payment(...)` to read `provider_result.status` instead of `provider_result["status"]`.
- Added direct provider tests proving both providers return the expected `PaymentResult`.
- Responsibility checkpoint:
  - `PaymentResult` owns the provider result data shape
  - provider classes own creating provider-level results
  - `charge_payment(...)` owns interpreting the provider result into an app-level payment result
- Ran project 02 tests: 5 passed.

Session update:

- Added provider-specific raw response pressure:
  - Stripe-like raw response uses fields such as `paid`, `status: "succeeded"`, and `description`
  - Razorpay-like raw response uses fields such as `captured`, `status: "captured"`, and `description`
- Kept `charge_payment(...)` unchanged so it still only sees the common `PaymentResult`.
- Added provider-specific conversion helpers:
  - `StripePaymentProvider.convert_to_app_result(...)`
  - `RazorpayPaymentProvider.convert_to_app_result(...)`
- Responsibility checkpoint:
  - provider classes now own the fake provider charge call and the conversion from that provider's raw response into our payment system's `PaymentResult`
  - `charge_payment(...)` owns only interpreting `PaymentResult` into the app-level payment result
- Discussed the important boundary: provider-specific response shapes should not leak into the orchestrator.
- Ran project 02 tests: 5 passed.

Session update:

- Added provider-level payment failure pressure.
- Made fake providers configurable with `should_succeed: bool = True`.
- Stripe fake raw response now uses:
  - `paid: True/False`
  - `status: "succeeded"` or `"failed"`
  - success/failure description
- Razorpay fake raw response now uses:
  - `captured: True/False`
  - `status: "captured"` or `"failed"`
  - success/failure description
- Added tests proving Stripe and Razorpay convert failed raw responses into `PaymentResult(status="failed", ...)`.
- Current bottleneck left behind: `charge_payment(...)` already has a failed-result branch, but it is still hard to drive that branch because it creates/selects the provider internally.
- Ran project 02 tests: 7 passed.

Session update:

- Refactored `charge_payment(...)` so the provider collaborator is passed in explicitly instead of selected internally.
- Old shape:
  - `charge_payment(user_id, amount, provider_name)`
  - selected provider internally via `get_payment_provider(...)`
- New shape:
  - `charge_payment(user_id, amount, provider)`
  - caller/provider-selection layer passes an object satisfying the `Provider` protocol
- Kept `get_payment_provider(...)` as the provider-selection function; selection did not disappear, it moved outside the orchestrator.
- Added a test that passes `StripePaymentProvider(should_succeed=False)` into `charge_payment(...)` and proves the app-level failed result.
- Responsibility checkpoint:
  - `get_payment_provider(...)` owns provider selection
  - `charge_payment(...)` owns orchestration with a provided payment provider
  - tests can now control the provider collaborator directly
- This is the same pressure as dependency injection: make collaborators visible when hidden creation makes behavior hard to test or reason about.
- Ran project 02 tests: 8 passed.

## 2026-08-14

Session update:

- Picked up Project 02 with the goal of wrapping it carefully, one pressure at a time.
- Added a `FakePaymentProvider` test double inside the tests.
- The fake provider:
  - returns a controlled `PaymentResult`
  - records calls in `charged_users`
- Used the fake provider to test `charge_payment(...)` orchestration directly:
  - verifies `charge_payment(...)` calls `provider.charge(user_id, amount)`
  - verifies `charge_payment(...)` converts failed `PaymentResult` into app-level failed result
- Named the concept: test double. More specifically, this fake works as a stub and a spy.
- Added provider stable config pressure.
- Changed provider objects so stable setup lives in `__init__`:
  - Stripe gets `api_key` and `environment`
  - Razorpay gets `merchant_id` and `environment`
- Kept event data as method arguments:
  - `user_id`
  - `amount`
- Updated `get_payment_provider(...)` to wire default sandbox config for Stripe and Razorpay.
- Added tests proving provider objects store stable config.
- Ran project 02 tests: 11 passed.

Session update:

- Split Project 02's single `payment.py` file by responsibility after it started owning too many concepts.
- New module ownership:
  - `models.py` owns the `PaymentResult` data shape
  - `providers.py` owns the `Provider` protocol, concrete provider behavior, provider response conversion, and provider selection
  - `payment.py` owns payment orchestration via `charge_payment(...)`
  - `tests/test_payment.py` owns behavior tests and fake provider test double
- Updated imports so tests read from the module that owns each concept.
- Behavior stayed the same after the split.
- Ran project 02 tests: 11 passed.

Session update:

- Added provider/system error boundary.
- Clarified the distinction:
  - normal payment failure means the payment was processed and clearly failed, such as wrong OTP, insufficient balance, or card declined
  - provider/system error means the provider/integration could not reliably process the request, such as timeout, provider API down, network failure, bad API key, or unexpected response shape
- Added `PaymentProviderError` in `providers.py` to represent provider-boundary infra/integration failures.
- Updated `charge_payment(...)` to catch `PaymentProviderError` and return:
  - `{"status": "failed", "message": "Payment provider unavailable"}`
- Added `BrokenPaymentProvider` test double that raises `PaymentProviderError`.
- Added a test proving `charge_payment(...)` translates provider errors into the safe app-level provider-unavailable response.
- Ran project 02 tests: 12 passed.

Session update:

- Discussed idempotency as the final Project 02 production boundary, without implementing it yet.
- Clarified that idempotency means the same payment request retried with the same key should not create a duplicate money movement.
- Example pressure:
  - provider charges successfully
  - backend times out before receiving response
  - frontend/user retries
  - without idempotency the user may be charged twice
- Clarified retry flow:
  - clear payment failure can allow a new payment attempt
  - timeout/unknown status should reuse the same payment request identity and reconcile/check status
- Decided not to implement full idempotency in Project 02 because it requires storage, unique constraints, transactions, provider idempotency support, webhooks, retries, and reconciliation.
- Project 02 takeaway: payment charge operations must not be blindly retried; production workflows need stable payment request identity and durable state.

## 2026-08-17

Session update:

- Started Phase 1, Project 03: API Key Management System.
- Clarified the problem: API keys let a backend identify and authorize developer/client requests.
- First tiny flow:
  - create an API key for a user
  - validate that the created key is accepted
  - reject an unknown key
- Added the first naive implementation in `projects/03-oop-lld-api-keys/api.py`.
- Added tests in `projects/03-oop-lld-api-keys/tests/test_api.py`.
- Introduced `APIKeyRecord` as a dataclass when key strings needed metadata:
  - `api_key`
  - `user_id`
  - `created_at`
  - `revoked`
- Refined the meaning of validation:
  - valid does not only mean "exists"
  - valid means key exists and is not revoked
- Added revoke behavior:
  - `revoke_api_key(api_key, user_id)` marks a matching user's key as revoked
  - returns `True` when a matching key is found
  - returns `False` when the key is missing or belongs to another user
- Introduced `APIKeyStore` to own in-memory storage and lookup:
  - `add_api_key(...)`
  - `find_record(...)`
- Extracted `generate_api_key(user_id)` from `create_api_key(...)`.
- Added duplicate-key avoidance in `create_api_key(...)` by generating candidate keys until `APIKeyStore.find_record(...)` returns `None`.
- Responsibility checkpoint:
  - `APIKeyRecord` owns metadata for one API key
  - `APIKeyStore` owns storing and finding records
  - `generate_api_key(...)` owns key string generation
  - `create_api_key(...)` owns the creation workflow
  - `validate_api_key(...)` owns current usability check
  - `revoke_api_key(...)` owns user-safe revoke behavior
- Cleaned duplicate test name and removed unnecessary randomness from the revoked-key test.
- Ran project 03 tests: 7 passed.

Session update:

- Added a testable duplicate-key generation path.
- Clarified the pressure:
  - production key generation should be unpredictable
  - tests need deterministic control over generated keys
  - hidden randomness inside `create_api_key(...)` makes collision behavior hard to test
- Made key generation injectable at the function level:
  - `create_api_key(user, key_generator=generate_api_key)`
  - normal callers can keep using the real generator
  - tests can pass a fake generator
- Added a collision test where the fake generator returns:
  - first key: already exists
  - second key: unique
- Verified `create_api_key(...)` generates again and stores the unique key.
- Responsibility checkpoint:
  - `generate_api_key(...)` owns real random key generation
  - fake generator owns controlled test values
  - `create_api_key(...)` owns the creation workflow and duplicate avoidance
- Ran project 03 tests: 8 passed.

Session update:

- Added API key secrecy pressure.
- Replaced insecure `random.randint(...)` style generation with `secrets.token_urlsafe(32)`.
- Clarified why:
  - normal `random` is for simulation/general randomness
  - `secrets` uses OS-backed randomness through `SystemRandom`
  - API keys are bearer secrets and must be hard to guess
- Stopped embedding `user_id` inside the generated API key; ownership belongs in `APIKeyRecord.user_id`.
- Added hashing boundary:
  - raw API key is returned to the user once
  - backend stores `api_key_hash`, not the raw API key
  - validation/revoke hash incoming raw keys before lookup
- Added `hash_api_key(...)` using SHA-256 for the project-level secret-storage boundary.
- Updated tests to assert stored records contain the hash and do not store the raw key.
- Responsibility checkpoint:
  - `generate_api_key(...)` owns secure raw key generation
  - `hash_api_key(...)` owns raw key to stored hash conversion
  - `APIKeyRecord` stores `api_key_hash`
  - public functions still accept/return raw API keys at the boundary
- Ran project 03 tests: 9 passed.

Session update:

- Added API key expiry pressure.
- Changed `APIKeyRecord` metadata from only creation/revocation data to also include:
  - `created_at`
  - `expires_at`
- Switched the timestamp fields to `datetime.datetime` values instead of strings so expiry can be compared as time, not text.
- Added a default API key lifetime of 30 days.
- Updated `create_api_key(...)` so it stores both the creation time and expiry time.
- Updated `validate_api_key(...)` so valid now means:
  - key exists
  - key is not revoked
  - current time is before `expires_at`
- Kept current time injectable for tests:
  - production callers can omit it and use `datetime.datetime.now()`
  - tests can pass a fixed time and avoid flaky clock-dependent behavior
- Added an expired-key test.
- Added an autouse test fixture to clear the in-memory store between tests.
- Responsibility checkpoint:
  - `APIKeyRecord` owns expiry metadata
  - `create_api_key(...)` owns assigning expiry at creation time
  - `validate_api_key(...)` owns the final validity decision
  - tests own fixed time values to make time behavior deterministic
- Ran project 03 tests: 10 passed.

Session update:

- Added dashboard listing pressure.
- Clarified the split:
  - creation/revocation/listing are dashboard/admin management flows
  - validation is the real-time request-auth flow
- Added `APIKeyValidationResult` so validation returns a safe contract instead of only a bool:
  - `is_valid`
  - `user_id`
- Clarified why this matters:
  - incoming API requests usually only carry the raw API key
  - the backend learns the acting `user_id` by validating and looking up the key
  - downstream systems use that `user_id` for business logic, authorization, rate limiting, billing, and audit logs
- Added `APIKeyStore.find_records_for_user(user_id)`.
- Added `list_api_keys(user_id)` as the dashboard-facing listing use case.
- Listing returns stored metadata records for the user; it does not reveal raw API keys.
- Added tests for:
  - valid validation result includes `user_id`
  - invalid validation result has `user_id=None`
  - listing returns only the selected user's records
  - listing returns an empty list when the user has no keys
- Responsibility checkpoint:
  - `APIKeyValidationResult` owns the safe validation response shape
  - `APIKeyStore` owns storage lookup details
  - `list_api_keys(...)` owns the dashboard listing use case
- Ran project 03 tests: 12 passed.

Session update:

- Added dashboard-safe display contract pressure.
- Clarified the issue:
  - `APIKeyRecord` is an internal storage record
  - it contains `api_key_hash`
  - dashboard listing should not expose internal secret/hash storage details
- Added `APIKeyDisplayRecord` with safe dashboard fields:
  - `user_id`
  - `created_at`
  - `expires_at`
  - `revoked`
- Kept `APIKeyStore.find_records_for_user(...)` returning internal `APIKeyRecord` objects because the store owns storage data, not dashboard formatting.
- Updated `list_api_keys(...)` to convert internal records into `APIKeyDisplayRecord` objects.
- Responsibility checkpoint:
  - `APIKeyRecord` owns internal stored metadata
  - `APIKeyDisplayRecord` owns dashboard-safe display shape
  - `APIKeyStore` owns finding stored records
  - `list_api_keys(...)` owns converting stored records into dashboard output
- Ran project 03 tests: 12 passed.

Session update:

- Added public key identity pressure.
- Clarified the distinction:
  - raw API key secret is used for runtime authentication
  - `api_key_hash` is stored internally so the raw secret is not stored
  - `key_id` is a safe public/dashboard identity for managing a stored key
- Added `key_id` to `APIKeyRecord`.
- Added `key_id` to `APIKeyDisplayRecord` so dashboard rows can identify which key the user wants to manage.
- Updated revoke behavior to use the dashboard-safe identity:
  - `revoke_api_key(key_id, user_id)`
  - store finds the record by `key_id`
  - revoke still checks `user_id` ownership before mutating the record
- Added `APIKeyStore.find_record_by_key_id(...)`.
- Fixed the partial migration errors from changing revoke from raw-key based to key-id based.
- Responsibility checkpoint:
  - `key_id` owns safe public identity for one stored key
  - raw API key owns authentication proof at runtime
  - `api_key_hash` owns internal lookup for runtime validation
  - `revoke_api_key(...)` owns dashboard-safe revoke by key identity plus user ownership check
- Ran project 03 tests: 12 passed.

Session update:

- Added module responsibility split after `api.py` became too broad.
- Created `models.py` for data contracts:
  - `APIKeyRecord`
  - `APIKeyValidationResult`
  - `APIKeyDisplayRecord`
- Created `store.py` for storage responsibility:
  - `APIKeyStore`
  - `api_key_directory`
- Created `security.py` for secret-handling helpers:
  - `generate_api_key(...)`
  - `hash_api_key(...)`
- Kept `DEFAULT_API_KEY_LIFETIME` in `api.py` because the 30-day expiry is a key lifecycle policy applied by `create_api_key(...)`, not a secret-generation mechanism.
- Kept `api.py` focused on use cases:
  - `create_api_key(...)`
  - `validate_api_key(...)`
  - `revoke_api_key(...)`
  - `list_api_keys(...)`
- Updated tests to import concepts from the modules that now own them.
- Responsibility checkpoint:
  - models own data shape
  - store owns persistence-like behavior
  - security owns secret generation/hash conversion
  - api owns API-key workflows and lifecycle policy
- Ran project 03 tests: 12 passed.

Project 03 closing checkpoint:

- Project 03: API Key Management System is wrapped.
- Final behavior includes:
  - secure API key generation
  - hashing raw keys before storage
  - in-memory key store
  - key metadata with `key_id`, `user_id`, `created_at`, `expires_at`, and `revoked`
  - validation returning `APIKeyValidationResult`
  - dashboard-safe listing returning `APIKeyDisplayRecord`
  - dashboard-safe revoke by `key_id` plus `user_id` ownership check
  - module responsibility split across `models.py`, `store.py`, `security.py`, and `api.py`
- Final test result:
  - Project 03 tests: 12 passed.
- We are ready to move to the next Phase 1 project in a new session.

## 2026-08-18

Roadmap revision:

- Phase 1 is now officially treated as complete after three foundation projects:
  - Project 01: Notification System
  - Project 02: Payment Provider System
  - Project 03: API Key Management System
- Decided not to continue with the old Phase 1 sequence of Rate Limiter and Background Job Runner right now.
- Reason:
  - the current goal is to go deeper on OOP, LLD, SOLID, design patterns, and DB design
  - Rate Limiter and Background Job Runner are still valuable, but they fit better later with Redis, async workers, and advanced backend production topics
- Locked the new Phase 2:
  - Advanced OOP + LLD + DB Design + FastAPI
- Phase 2 learning sequence:
  - pure Python design first
  - DB design second
  - ORM/repository third
  - FastAPI last
- New Phase 2 projects:
  - Inventory and Order Management
  - Movie Ticket Booking
  - E-commerce Checkout Capstone if time allows, otherwise as the bridge into Phase 3
- Teaching style remains unchanged:
  - discussion first, code second
  - pressure before principle
  - let Jatin reason before naming patterns
  - after a concept lands, reveal the concept/pattern/principle name clearly for interview vocabulary
  - ask responsibility questions
  - Jatin types meaningful code when syntax muscle memory matters
  - Codex may edit notes/progress and mechanical scaffolding when explicitly asked
- Updated `ROADMAP.md` and `SESSION_CONTEXT.md` so future sessions resume from the new plan.

Phase 2 project count refinement:

- Decided Phase 2 should use 2-3 deeper projects instead of five thinner ones.
- Reason:
  - the goal is not to finish many project names
  - the goal is to deeply cover advanced OOP, SOLID, design patterns, DB design, ORM boundaries, FastAPI, and API tests
- Locked expectation:
  - Project 01 of Phase 2: Inventory and Order Management
  - Project 02 of Phase 2: Movie Ticket Booking
  - Project 03 of Phase 2: E-commerce Checkout Capstone if time allows

Phase 2 interview-readiness lock:

- Phase 2 should cover the advanced OOP, SOLID, design pattern, DB design, ORM, FastAPI, and API testing topics discussed above.
- Phase 2 is also expected to make Jatin capable enough for Big Tech-style LLD interviews, with one important condition:
  - project implementation must be paired with design explanation practice
  - after enough project depth, add timed LLD mock rounds
- Interview readiness means Jatin should be able to:
  - clarify requirements
  - identify actors/use cases
  - model entities and relationships
  - assign class/module/service responsibilities
  - design method/API contracts
  - reason about state transitions
  - explain DB tables, constraints, and transaction boundaries
  - discuss extensibility and tradeoffs
  - name the relevant SOLID principle or design pattern after the intuition is clear

Phase 3 and Phase 4 continuity rule:

- LLD does not stop after Phase 2.
- Phase 3 adds production backend pressure while keeping responsibility boundaries, SOLID, and design tradeoffs in the loop.
- Phase 4 adds AI backend pressure while continuing to use the same LLD lens.
- In later phases, every system should still ask:
  - what owns this behavior?
  - what does this component know?
  - what should it not know?
  - what changes together?
  - what boundary protects this failure mode?

## Working Agreement

- We prioritize projects over theory.
- Codex teaches through bottlenecks: introduce/notice pressure first, discuss Jatin's intuition, then name the principle or pattern.
- Codex should not lead with jargon such as dependency injection, Strategy, or SOLID. The name comes after the pain is visible in code.
- Codex gives exercises, reviews code, and updates progress, but Jatin should type substantial code when syntax muscle memory matters.
- Codex may code directly when Jatin explicitly asks, especially for mechanical refactors, test updates, note updates, or module splits.
- Codex should slow down when Jatin says a step feels too fast, revert only its own last change if asked, and return to discussion before coding.
- Codex should keep asking responsibility questions: what does this function/class/module own, what does it know, and what should it not know?
- Codex should preserve the Project 01 pattern: naive implementation, added requirement, visible pain, refactor, vocabulary, tests, notes and also once the topic is complete tell jatin the name of the topic we just learned or if jatin asks you for the topic we are learning then tell him
- You type substantial code for muscle memory whenever possible.
- Git will be managed like a production repo once initialized.

## 2026-08-20

Started Phase 2, Project 04: Inventory and Order Management.

Project path:

- `projects/04-inventory-order-management/`

Current files:

- `order.py`
- `tests/test_order.py`

Initial pressure:

- A user attempts to place an order.
- The system checks whether requested product quantity is available.
- If stock is available, inventory is reduced.
- If stock is unavailable or the product does not exist, inventory is not changed.

First result-contract pressure:

- `True` / `False` became too weak because failure can mean multiple things:
  - product not found
  - insufficient stock
- Introduced `OrderRecord` as a small dataclass result object:
  - `success`
  - `message`
  - `order_id`
- Tests compare deterministic dataclass values.

Second pressure: multi-product orders.

- `place_order(...)` now accepts a list of `UserOrder` items instead of one product and one quantity.
- Introduced `UserOrder` as the ordered-item input contract:
  - `product_name`
  - `quantity`
- Implemented all-or-nothing inventory update:
  - copy inventory
  - validate and apply every requested item to the copy
  - commit back to the original inventory only after every item succeeds
  - leave original inventory unchanged on any failure

Topics learned:

- Result Contract / Result Object
- Dataclass equality in tests
- Input contract for requested order items
- Python name binding vs mutating a shared dict
- Shallow copy is enough for the current flat inventory shape
- All-or-nothing update / commit-after-validation
- Early pure-Python version of transaction thinking

Current Project 04 test result:

- Ran project 04 tests: 6 passed.

Next pressure:

- `place_order(...)` still owns too much:
  - product existence check
  - stock validation
  - stock mutation
  - order workflow result
- Next discussion should ask who owns stock behavior:
  - raw inventory dict
  - order workflow
  - inventory object/service

Same-day Project 04 checkpoint:

- Introduced `InventoryService` as the owner of inventory behavior while keeping the inventory storage shape as `dict[str, int]`.
- Removed the premature `InventoryProduct` list shape for now because changing storage representation and introducing a service at the same time created too much pressure.
- Current responsibility split:
  - `place_order(...)` coordinates order placement.
  - `InventoryService` owns product existence checks, stock validation, stock reduction, copy-and-commit, and the raw inventory dict.
- Updated the caller boundary so `place_order(...)` receives an `InventoryService`, not a raw inventory dict.
- Discussed why `InventoryService.__init__(inventory: dict[str, int])` documents the current storage shape:
  - product name as `str`
  - available quantity as `int`
- Discussed `.copy()`:
  - creates a new shallow dict with the same key-value pairs
  - safe for the current flat inventory because values are integers
  - lets the workflow apply all changes to the copy before committing
- Discussed encapsulation:
  - `place_order(...)` knows what outcome it needs
  - `InventoryService` knows how inventory data should be checked and changed
  - inventory structure is hidden behind inventory behavior
- Topic learned:
  - Encapsulation / Responsibility Ownership
- Ran project 04 tests after the refactor: 6 passed.

Resume point:

- Continue from the `InventoryService` boundary.
- Next likely pressure: `InventoryService.reduce_stock_for_order(...)` returns `OrderRecord`, which may mean inventory logic is now leaking order-result language.
- Ask whether inventory should return order-level results or inventory-level results/status.

## 2026-08-24

Continued Phase 2, Project 04: Inventory and Order Management.

Resolved boundary leak:

- `InventoryService.reduce_stock_for_order(...)` no longer returns `OrderRecord`.
- Introduced `InventoryResult` as an inventory-level result contract:
  - `success`
  - `message`
- `InventoryService` now speaks inventory language:
  - `"Stock reduced"`
  - `"Product not found"`
  - `"Only N units available"`
- `place_order(...)` translates inventory result into order result:
  - inventory failure -> `OrderRecord(False, message, None)`
  - inventory success -> `OrderRecord(True, "Order placed", "order-1")`

Introduced richer inventory record:

- Added `InventoryProduct` dataclass:
  - `product_name`
  - `quantity`
  - `sku`
  - `category`
- Changed inventory storage from `dict[str, int]` to `dict[str, InventoryProduct]`.
- `place_order(...)` did not need to know about this storage change because it still only depends on `InventoryService`.
- Discussed SKU:
  - SKU means Stock Keeping Unit
  - it is a stable business/internal identifier for tracking a specific sellable item or variant

Deepened copy semantics:

- `dict.copy()` is shallow:
  - it creates a new dict container
  - nested/mutable objects inside are still shared
- Because inventory values are now `InventoryProduct` objects, directly mutating `inventory_copy[item].quantity` would also mutate the original product object.
- Current implementation replaces the copied dict entry with a new `InventoryProduct` to preserve all-or-nothing behavior.

Added invariant protection:

- `InventoryProduct.quantity` must never be negative.
- Added `InventoryProduct.__post_init__(...)` to raise `ValueError` when quantity is below zero.
- Discussed why the object should own this rule:
  - negative quantity makes the inventory product itself invalid
  - the rule is not only about order placement
  - putting the check inside `InventoryProduct` prevents invalid objects from existing anywhere

Topics learned:

- Boundary-specific result contracts
- Storage representation hidden behind a service boundary
- SKU as inventory/product identifier
- Shallow copy vs shared nested objects
- Invariant Protection
- `dataclass.__post_init__`

Current Project 04 test result:

- Ran project 04 tests: 7 passed.

Next pressure:

- Quantity is protected for `InventoryProduct`, but `UserOrder.quantity` can still be `0` or negative.
- Ask whether an ordered item with zero/negative quantity is meaningful, and where that rule should live.

Same-day continuation:

- Added `UserOrder.__post_init__(...)` to protect the ordered-item quantity invariant.
- `UserOrder.quantity` must be greater than zero.
- Discussed why `__post_init__` is used in dataclasses:
  - dataclass generates `__init__`
  - `__post_init__` runs after field assignment
  - it is the clean hook for validation/setup while keeping dataclass convenience
- Introduced `OrderService` as the owner of the order placement workflow.
- Removed the standalone `place_order(...)` function after tests were updated to call `OrderService.place_order(...)`.
- Current responsibility split:
  - `OrderService` owns order placement orchestration.
  - `InventoryService` owns inventory data and stock behavior.
  - `InventoryProduct` protects inventory-product validity.
  - `UserOrder` protects requested-item validity.
  - `OrderRecord` remains the caller-facing order result.
- Discussed the LLD mental model:
  - responsibility assignment: who owns each job
  - boundaries: what each component can see/touch
  - invariants: rules that must always be true
  - collaboration: how components ask each other to do work without stealing responsibilities
- Topic now visible:
  - Single Responsibility Principle intuition
- Ran project 04 tests after the `OrderService` refactor: 8 passed.

Next pressure:

- `OrderService` returns `order_id="order-1"`, but no real `Order` object is created or stored yet.
- Move from caller-facing `OrderRecord` to an internal `Order` domain object with `order_id`, `items`, and `status`.
