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
