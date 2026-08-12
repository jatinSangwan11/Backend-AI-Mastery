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
