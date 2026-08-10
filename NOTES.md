# Notes

## OOP And LLD Intuition

Good backend design usually asks:

- What are the domain concepts?
- Which objects own which behavior?
- Which dependencies should be interfaces?
- What should be easy to extend later?
- What should be easy to test without real external services?

## Learning Method

We learn design through pressure, not memorization.

- Start from requirements.
- Write the simplest working code first.
- Notice what becomes painful.
- Discuss what Jatin thinks the problem is.
- Refactor only when the code gives us a real reason.
- Name SOLID principles and design patterns after we have felt the problem they solve.
- Build Python syntax muscle memory by typing real project code, tests, and refactors.
- Jatin owns coding-file edits by default; Codex edits code only when explicitly asked.
- Codex keeps markdown notes/progress focused on important intuition and revision points.

We do not use noun/verb extraction as the main design method. It is only a beginner fallback. Our stronger questions are:

- What decision is this code making?
- What changes together?
- What should be replaceable?
- What behavior needs isolated tests?
- What external dependency should be hidden?
- What would future engineers accidentally break?

## First Design Rule

Route handlers and top-level scripts should orchestrate. Domain and service objects should hold most business behavior.

## Bottleneck 01: Testing `print()`

Our first naive notification function used `print()` to show the email output.

Intuition:

- `print()` is a side effect.
- Side effects are harder to test than returned values.
- Since the function returns nothing, the only observable behavior is terminal output.
- Pytest's `capsys` fixture captures printed output so tests can assert on it.

This is a temporary solution. The awkwardness is useful: it shows pressure toward code that exposes behavior more cleanly.

## Bottleneck 02: Code Running During Import

We added a second notification type: OTP over SMS.

While testing imports, we learned:

- `from notification import send_welcome_notification` still loads and executes the whole `notification.py` module once.
- Function bodies are defined during import, but not called.
- Top-level code outside functions/classes runs during import.
- Direct demo/manual code should go under `if __name__ == "__main__":`.

Intuition:

- A module should usually be safe to import.
- Importing reusable code should not accidentally send messages, call APIs, start servers, or print surprise output.
- The `__name__ == "__main__"` guard separates reusable module code from direct script execution.

New design pressure:

- One notification function was easy.
- Two notification functions are still okay.
- Multiple notification types will start creating pressure around shared formatting, validation, and delivery behavior.

## Responsibility Lens: Mechanism, Intent, Data

When a function grows, ask what it owns:

- Mechanism: how the action is performed.
- Business intent: what should happen for a known use case.
- Data: variable values provided from outside.

Example:

- `send_email_notification(email, subject, message)` owns the email delivery mechanism.
- `send_welcome_email(email)` would own the standard welcome subject/message.
- A custom promotional email can keep subject/message caller-owned.

Useful question: if product changes this rule tomorrow, where should the edit live?

## Bottleneck 03: Mixed Responsibilities In One Function

`send_otp_notification` worked, but it owned too many jobs:

- phone number validation
- OTP notification intent
- SMS delivery mechanism

Refactor:

- `validate_otp_notification(phone_no)` owns validation rules.
- `send_sms_notification(phone_no, message)` owns SMS delivery mechanism.
- `send_otp_notification(phone_no, otp)` owns OTP intent and orchestration.

Intuition:

- Working code can still be hard to reason about if one function owns too many responsibilities.
- Split by responsibility before jumping to classes.
- Let exceptions bubble up when the caller/test should see the failure.
