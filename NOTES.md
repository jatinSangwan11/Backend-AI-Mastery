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
- Use spiral learning: learn enough, build with it, move on, and revisit the idea under harder pressure.
- Keep the pace dense but not shallow; avoid both rushing intuition and over-polishing toy projects.

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

## Pytest Fixtures

A pytest fixture is reusable test setup.

Example:

```python
@pytest.fixture
def user() -> User:
    return User("jatin@example.com", "8182828232", "device-token-123")
```

When pytest sees a test argument with the same name:

```python
def test_security_alert_happy_case(user, capsys) -> None:
    send_security_alert(user)
```

it does the matching for us:

```text
test argument name -> matching fixture -> fixture return value -> used inside test
```

So pytest runs the `user` fixture function, takes the returned `User` object, and passes that object into the test as the `user` argument. We do not call `user()` inside the test because pytest has already called the fixture.

Use fixtures when setup is common and boring. Create data inline when the specific value is the point of the test, such as invalid phone numbers.

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

Shared vocabulary:

- Event data: data that comes fresh for one action/request, such as `otp`, `reset_link`, `user.email`, or `user.phone_no`.
- Stable config: setup values reused across many actions, such as sender emails, provider names, API keys, timeouts, or retry counts.
- Mechanism: the low-level "how", such as `send_email_notification(...)` or `send_sms_notification(...)`.
- Business intent: the product-level "what", such as `send_welcome_email(...)`, `send_password_reset_email(...)`, or `send_security_alert(...)`.
- Data object: a simple grouping of values that travel together, such as `User(email, phone_no)`.
- Behavior object: behavior that remembers stable config/state while doing its job.

Current flow:

```text
business intent function
    receives event data
    chooses business-specific rules/config
    calls mechanism function
        performs the low-level action
```

Example:

- `send_welcome_email(user)` is a business intent.
- It can own the welcome subject/message and choose the marketing sender.
- `send_email_notification(...)` is the mechanism that performs the email send.

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

## Constant, Enum, Function, Class Ladder

Use the smallest structure that solves the current pressure:

- Constant: one repeated value.
- Enum: multiple fixed named choices.
- Separate functions: different mechanics/implementation per choice.
- Class/object: mechanics plus related config/state that should live together.

Intuition:

- Enum identifies a type; it does not own behavior.
- If behavior differs by type, avoid one large `if/elif` function owning every branch.
- A class becomes useful when an implementation needs remembered data/config/state across calls.

Example: sender email pressure

- One sender email: `DEFAULT_SENDER_EMAIL`.
- Multiple known sender emails: `SenderEmail` enum.
- Different sender mechanics: separate send functions.
- Sender mechanics plus config/state: sender class and sender objects.

Current sender-email pressure:

```text
welcome email        -> marketing@ourapp.com
password reset email -> support@ourapp.com
security alert       -> security@ourapp.com
```

For now, constants are enough. The important design pressure is visible in the mechanism signature:

```python
send_email_notification(user_email, subject, message, sender_email)
```

`sender_email` is stable config, while `user_email`, `subject`, and `message` are send-time details. If the email mechanism later needs more stable setup, such as `provider_name`, `api_key`, timeout, or retry config, then a configured behavior object like `EmailSender` will start to feel natural.

## First Behavior Objects

We introduced behavior objects when stable config started traveling with repeated behavior.

Examples:

- `EmailSender(sender_email, provider_name)` stores stable email setup.
- `SmsSender(provider_name)` stores stable SMS setup and owns phone validation.
- `PushSender(provider_name)` stores stable push setup.

The repeated rule:

```text
stable setup/config -> object __init__
event/send-time data -> method arguments
```

Example:

```python
security_email_sender = EmailSender(SECURITY_SENDER_EMAIL, AWS_SES_PROVIDER)

security_email_sender.send(
    user.email,
    "Security Alert",
    "New login detected on your account",
)
```

Here `SECURITY_SENDER_EMAIL` and `AWS_SES_PROVIDER` are stable config remembered by the object. `user.email`, subject, and message are send-time data passed into the method.

## Bottleneck 04: Channel-Specific Security Alert Logic

After adding email, SMS, and push security alerts naively, `send_security_alert` became crowded:

```python
security_email_sender.send(user.email, subject, message)
security_sms_sender.send(user.phone_no, message)
security_push_sender.send(user.device_token, title, message)
```

The function worked, but it knew too much about each channel:

- email needs `user.email`, subject, and message
- SMS needs `user.phone_no` and message
- push needs `user.device_token`, title, and message

The business intent is simpler:

```text
alert this user through all configured security-alert channels
```

So we introduced security-alert channel wrappers with a common method:

```python
channel.notify(user)
```

Each wrapper hides channel-specific details:

- `SecurityEmailAlertChannel` has an `EmailSender`.
- `SecuritySmsAlertChannel` has an `SmsSender`.
- `SecurityPushAlertChannel` has a `PushSender`.

This is composition:

```text
business-specific channel object has a lower-level sender object
```

This is also abstraction:

```text
different concrete channels, same common action: notify(user)
```

Now `send_security_alert` can depend on the common action:

```python
for channel in security_alert_channels:
    channel.notify(user)
```

Important intuition:

- `EmailSender`, `SmsSender`, and `PushSender` are lower-level mechanisms.
- `SecurityEmailAlertChannel`, `SecuritySmsAlertChannel`, and `SecurityPushAlertChannel` are business-specific wrappers for the security-alert use case.
- Passing the whole `User` into `notify(user)` gives every channel the same method shape; each channel chooses the contact field it needs.

## Protocols And Structural Typing

After security-alert channels shared the same action, we named that contract with a protocol:

```python
from typing import Protocol

class SecurityAlertChannel(Protocol):
    def notify(self, user: User) -> None:
        ...
```

Read this as:

```text
A security alert channel is anything that can notify a user.
```

Then:

```python
security_alert_channels: list[SecurityAlertChannel] = [
    SecurityEmailAlertChannel(security_email_sender),
    SecuritySmsAlertChannel(security_sms_sender),
    SecurityPushAlertChannel(security_push_sender),
]
```

Read this as:

```text
security_alert_channels is expected to be a list of objects that satisfy the SecurityAlertChannel protocol.
```

Important distinction:

- With normal inheritance, a class explicitly says it is a child of another class.
- With a `Protocol`, a class can satisfy the contract just by having the required shape.

So `SecurityEmailAlertChannel` does not need to inherit from `SecurityAlertChannel`. It satisfies the protocol because it has:

```python
def notify(self, user: User) -> None:
    ...
```

This is structural typing:

```text
If it has the required method shape, it can be treated as that protocol.
```

Do not say:

```text
the list elements are of this exact type
```

Prefer:

```text
the list elements satisfy this protocol
```

Runtime nuance:

- Plain Python mostly does not enforce this at runtime.
- If a bad object enters the list, runtime usually fails only when `channel.notify(user)` is called.
- The protocol mainly helps human readers, editors, and static type checkers such as mypy or pyright.

So the value is:

```text
named abstraction + documented contract + better type-checker/editor help
```

## Runtime Guards And Monkeypatch

A protocol documents the contract, but plain Python does not strongly enforce it at runtime. If we want a runtime guard, we can check each configured channel before calling it:

```python
def send_security_alert(user: User) -> None:
    for channel in security_alert_channels:
        notify = getattr(channel, "notify", None)

        if not callable(notify):
            raise TypeError("Invalid security alert channel")

        notify(user)
```

`getattr` syntax:

```python
getattr(object, attribute_name, default_value)
```

Example:

```python
notify = getattr(channel, "notify", None)
```

This means:

```text
Try to get channel.notify. If it does not exist, return None instead of raising AttributeError.
```

The `None` is not the return type of `notify`; it is only the fallback value when the attribute is missing.

Then:

```python
callable(notify)
```

checks whether the value can actually be called like a function/method.

To test the runtime guard, use `monkeypatch` to temporarily replace the module-level channel list:

```python
import notification

def test_send_security_alert_rejects_invalid_channel(user, monkeypatch) -> None:
    monkeypatch.setattr(notification, "security_alert_channels", ["oops"])

    with pytest.raises(TypeError, match="Invalid security alert channel"):
        send_security_alert(user)
```

Why this works:

```text
notification is a module object
security_alert_channels is an attribute on that module object
monkeypatch.setattr temporarily replaces that attribute for one test
pytest restores the original value after the test
```

We replace the whole list with `["oops"]` instead of appending because the test should focus only on the invalid-channel case and avoid running real channels first.

## Explicit Dependencies And Enabled Channels

New pressure:

```text
Security alerts should only be sent through channels enabled for this user/use case.
```

This created two separate concepts:

- Configured channels: what the system is capable of using for this call.
- Enabled channels: what this user/use case allows.

Example:

```text
configured channels -> email, SMS, push
enabled channels    -> email, push
```

So `send_security_alert` now receives both explicitly:

```python
def send_security_alert(
    user: User,
    configured_channels: list[SecurityAlertChannel],
    enabled_channels: list[str],
) -> None:
    ...
```

Important intuition:

```text
If a function needs something to do its job, make that dependency visible in the function signature.
```

Before, `send_security_alert` secretly depended on the module-level `security_alert_channels` list. That made tests patch global state with `monkeypatch`.

After, tests and callers can pass the channel list directly:

```python
send_security_alert(
    user,
    security_alert_channels,
    [EMAIL_CHANNEL, PUSH_CHANNEL],
)
```

Each channel also has a stable identity:

```python
channel.channel_type
```

The function can now filter:

```python
if channel.channel_type in enabled_channels:
    notify(user)
```

This is the pain relief that leads to dependency injection:

```text
stop reaching for hidden/global collaborators
pass required collaborators into the function/object that needs them
```
