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

## Constructor Injection And Test Doubles

When `send_security_alert` started receiving too many repeated setup arguments, we moved the workflow into a configured object:

```python
class SecurityAlertNotifier:
    def __init__(self, configured_channels: list[SecurityAlertChannel]) -> None:
        self.configured_channels = configured_channels

    def notify(self, user: User, enabled_channels: list[str]) -> None:
        ...
```

This is constructor injection:

```text
SecurityAlertNotifier receives its channel collaborators through __init__.
```

The split stayed consistent:

```text
stable collaborators/config -> __init__
event/use-case data -> method arguments
```

So:

- `configured_channels` belongs in `SecurityAlertNotifier.__init__`.
- `user` and `enabled_channels` belong in `notify(...)`.

This made tests cleaner. Instead of patching a global list, a test can create a local notifier with fake channels:

```python
class FakeSecurityAlertChannel:
    def __init__(self, channel_type: str) -> None:
        self.channel_type = channel_type
        self.notified_users = []

    def notify(self, user: User) -> None:
        self.notified_users.append(user)
```

The fake channel records which users were notified. This lets the test assert workflow behavior directly:

```python
assert email_channel.notified_users == [user]
assert sms_channel.notified_users == []
assert push_channel.notified_users == [user]
```

This is a test double:

```text
a simple test-only object that stands in for a real collaborator
```

Use fake/test-double collaborators when the behavior being tested is orchestration, not the real side effect.

## Module Responsibility Split

When `notification.py` grew into a pile of data models, constants, senders, security-alert workflow, configured objects, and business functions, we split by responsibility:

```text
models.py          -> data shapes such as User
constants.py       -> stable named values
senders.py         -> low-level delivery mechanisms
security_alerts.py -> security-alert abstraction, wrappers, notifier
notification.py    -> wiring/configured objects and business intent functions
```

This is a module responsibility split:

```text
same behavior, clearer file ownership
```

Do not create one file per class by default. Group code by cohesive responsibility and navigation needs.

## Project 01 Closing Checkpoint

Project 01 started from one naive print-based function and grew through requirement pressure into a small object design.

Core ideas learned:

- side effects and `capsys`
- module import behavior and `if __name__ == "__main__"`
- event data vs stable config
- data objects vs behavior objects
- composition
- protocols and structural typing
- runtime guards
- dependency injection
- test doubles
- module responsibility

Weekend revision goal:

```text
For each object/module, say what responsibility it owns and what it should not know.
```

## Project 02 Starting Context: Payment Provider System

The payment system sits between the product/order flow and the external payment provider.

Pipeline:

```text
User clicks Buy
-> product/order system knows user, item, and price
-> payment system receives user_id and amount
-> payment system talks to an external provider later
-> payment result comes back as success/failure/pending
-> order system marks purchase paid, failed, or still waiting
```

So Project 02 is not building the product catalog, price calculation, cart, article/course ownership, or UI checkout page.

Project 02 is building this responsibility:

```text
Given a valid user/payment request, try to collect money through a payment provider and report what happened.
```

Meaning of "charge a user":

```text
Ask the payment system/provider to collect an amount from that user.
```

Example:

```python
charge_payment(user_id="40", amount=500)
```

In the first toy slice, no real money moves. The function only prints:

```text
Charging user 40 amount 500
```

In a real backend, this would eventually mean:

```text
For user 40, collect amount 500 through a payment method/provider, then return or record the result.
```

Important starting expectation:

```text
Make the simplest payment action visible first.
Notice what becomes awkward.
Add requirements one at a time.
Only then introduce names like provider abstraction, dependency injection, test double, or adapter.
```

Current responsibility checkpoint:

```text
charge_payment owns only the basic "start a charge for this user and amount" action.
```

It does not yet own:

- provider choice
- card/UPI/payment-method details
- provider-specific response shapes
- success/failure handling
- retries
- idempotency
- database records
- real money movement

## Project 02 Bottleneck 01: Provider Logic In The Main Flow

The first provider pressure:

```text
All payments do not have to use the same provider forever.
Some payments may use Stripe.
Some payments may use Razorpay.
```

The naive shape is:

```python
def charge_payment(user_id: str, amount: int, provider_name: str) -> None:
    if provider_name == "stripe":
        print(...)
    elif provider_name == "razorpay":
        print(...)
```

This works for two tiny providers, but the responsibility starts to blur.

`charge_payment` begins to own:

- starting/coordinating the payment charge flow
- choosing which provider branch to use
- knowing provider-specific charging behavior

The pain:

```text
Every new provider forces us to edit the central payment function.
Provider details collect in one place.
The function becomes easier to break as branches increase.
```

First refactor:

```python
def charge_payment(user_id: str, amount: int, provider_name: str) -> None:
    provider = get_payment_provider(provider_name)
    provider.charge(user_id, amount)
```

Responsibility split:

```text
charge_payment               -> payment flow coordination
get_payment_provider         -> provider selection
StripePaymentProvider        -> Stripe charging behavior
RazorpayPaymentProvider      -> Razorpay charging behavior
```

Important nuance:

```text
The if/elif did not disappear yet.
It moved to get_payment_provider, where provider selection is the only job.
```

This is useful progress because `charge_payment` no longer knows how every provider charges. It only asks the selected provider to charge.

## Project 02 Bottleneck 02: Payment Needs A Result

The next pressure:

```text
The order/product flow cannot act on a print statement.
It needs to know whether the payment succeeded or failed.
```

So provider methods now return a provider-level result:

```python
{
    "status": "success",
    "provider_name": "stripe",
    "provider_message": "Stripe charge completed",
}
```

Then `charge_payment` converts that into the app-level result:

```python
{
    "status": "success",
    "message": "Payment successful",
}
```

Responsibility split:

```text
provider.charge(...) -> provider charging behavior and provider-level outcome
charge_payment(...)  -> payment flow coordination and app-level result decision
```

Important boundary:

```text
The provider can speak in provider-specific details.
The payment flow should return a cleaner result that the rest of the app can use.
```

We are using dicts first on purpose:

```text
dicts make the shape visible quickly.
dataclasses become useful later if repeated keys and string-based access become awkward.
```

## Project 02 Bottleneck 03: Repeated Dict Shape

The provider result first used a plain dict:

```python
{
    "status": "success",
    "provider_name": "stripe",
    "provider_message": "Stripe charge completed",
}
```

That worked, but the shape depended on repeated string keys:

```python
provider_result["status"]
provider_result["provider_name"]
provider_result["provider_message"]
```

The pain:

```text
A typo in a key fails at runtime.
Every provider has to remember the same keys manually.
The result shape is important, but it has no name in the code.
```

So we introduced a small data object:

```python
@dataclass
class PaymentResult:
    status: str
    provider_name: str
    provider_message: str
```

Now providers return:

```python
PaymentResult(
    "success",
    "stripe",
    "Stripe charge completed",
)
```

And the orchestrator reads:

```python
if provider_result.status == "success":
    ...
```

Responsibility split:

```text
PaymentResult          -> provider result data shape
provider classes       -> create provider-level results
charge_payment(...)    -> interpret provider result into app-level result
```

Name of the idea:

```text
PaymentResult is a data object.
```

Use a dataclass when related values travel together and the shape deserves a name.

## Project 02 Bottleneck 04: Provider-Specific Raw Responses

The next pressure:

```text
Stripe and Razorpay do not speak the same response language.
```

Example Stripe-like raw response:

```python
{
    "id": "pi_123",
    "object": "payment_intent",
    "amount": 500,
    "currency": "inr",
    "status": "succeeded",
    "paid": True,
    "description": "Payment completed successfully",
}
```

Example Razorpay-like raw response:

```python
{
    "id": "pay_456",
    "entity": "payment",
    "amount": 500,
    "currency": "INR",
    "status": "captured",
    "captured": True,
    "description": "Payment captured successfully",
}
```

The app does not want to care that Stripe means success with `paid == True` while Razorpay means success with `captured == True`.

So each provider class translates its own raw response:

```python
class StripePaymentProvider:
    def convert_to_app_result(self, raw_result: dict) -> PaymentResult:
        ...
```

```python
class RazorpayPaymentProvider:
    def convert_to_app_result(self, raw_result: dict) -> PaymentResult:
        ...
```

Responsibility split:

```text
provider.charge(...)             -> fake provider call for now
provider.convert_to_app_result   -> translate provider raw response into PaymentResult
charge_payment(...)              -> interpret PaymentResult into app-level result
```

Important boundary:

```text
Provider-specific response details stay inside provider classes.
charge_payment should not know about Stripe's `paid` field or Razorpay's `captured` field.
```

Current provider class responsibility:

```text
The provider class owns charging through that provider and converting that provider's response into our common payment result.
```

This is acceptable for now because both responsibilities are closely related to the provider boundary. If the conversion grows large later, it may become its own helper/object.

## Project 02 Bottleneck 05: Provider-Level Failure

The orchestrator already had this branch:

```python
if provider_result.status == "success":
    return {
        "status": "success",
        "message": "Payment successful",
    }

return {
    "status": "failed",
    "message": "Payment failed",
}
```

But both real fake providers always returned success, so we could not prove failure behavior.

First pressure to add:

```text
Can each provider translate its own failed raw response into PaymentResult?
```

We made fake providers configurable:

```python
StripePaymentProvider(should_succeed=False)
RazorpayPaymentProvider(should_succeed=False)
```

So Stripe can produce:

```python
{
    "paid": False,
    "status": "failed",
    "description": "Payment failed",
}
```

and Razorpay can produce:

```python
{
    "captured": False,
    "status": "failed",
    "description": "Payment failed",
}
```

Both convert into:

```python
PaymentResult(
    "failed",
    "<provider>",
    "Payment failed",
)
```

Responsibility checkpoint:

```text
Provider classes own provider-level success/failure translation.
charge_payment owns app-level success/failure interpretation.
```

Remaining bottleneck:

```text
charge_payment has a failure branch, but we cannot cleanly force it to receive a failed provider result because it selects/creates providers internally.
```

That pressure points toward passing collaborators into the flow instead of hiding them inside it.

## Project 02 Bottleneck 06: Hidden Provider Collaborator

The previous `charge_payment` shape was:

```python
def charge_payment(user_id: str, amount: int, provider_name: str) -> dict:
    provider = get_payment_provider(provider_name)
    provider_result = provider.charge(user_id, amount)
    ...
```

This worked, but it hid an important collaborator:

```text
charge_payment needed a provider object to do its job.
```

The visible pain was testing:

```text
How do we force charge_payment to receive a failed provider result?
```

The deeper design pain:

```text
charge_payment was doing both provider selection and payment orchestration.
```

Refactor:

```python
def charge_payment(user_id: str, amount: int, provider: Provider) -> dict:
    provider_result = provider.charge(user_id, amount)
    ...
```

Now provider selection happens outside:

```python
provider = get_payment_provider("stripe")
result = charge_payment("40", 500, provider)
```

Responsibility split:

```text
get_payment_provider(...) -> provider selection
charge_payment(...)       -> orchestration with a provided provider
Provider protocol         -> expected provider behavior shape
```

The name of this idea:

```text
dependency injection
```

In plain words:

```text
If a function/object needs a collaborator, pass that collaborator in instead of creating/selecting it hidden inside.
```

Use this when hidden collaborator creation makes behavior hard to test, replace, or reason about.

### Collaborator And Dependency Injection Vocabulary

A collaborator is:

```text
another object/function this code needs in order to do its job
```

In Project 02:

```text
charge_payment needs a payment provider to charge money.
```

So the provider object is a collaborator of `charge_payment`.

A dependency is:

```text
something this function/object depends on to work
```

In Project 02:

```text
charge_payment depends on a Provider.
```

Injection means:

```text
we pass/give that dependency from outside
```

Before dependency injection:

```python
def charge_payment(user_id: str, amount: int, provider_name: str) -> dict:
    provider = get_payment_provider(provider_name)
    provider_result = provider.charge(user_id, amount)
    ...
```

Here `charge_payment` creates/selects its provider collaborator internally.

After dependency injection:

```python
def charge_payment(user_id: str, amount: int, provider: Provider) -> dict:
    provider_result = provider.charge(user_id, amount)
    ...
```

Here the provider collaborator is passed in from outside.

How to recognize the pressure:

```text
If hidden creation/selection of another object makes behavior hard to test, replace, or reason about, consider passing that object in.
```

Plain definition:

```text
dependency injection = pass required collaborators/dependencies from outside instead of creating them hidden inside.
```

## Project 02 Bottleneck 07: Testing Orchestration With A Fake Provider

After dependency injection, `charge_payment(...)` can receive any object that follows the `Provider` protocol.

This lets tests avoid real Stripe/Razorpay behavior when the goal is only to test orchestration.

Fake provider:

```python
class FakePaymentProvider:
    def __init__(self, payment_result: PaymentResult) -> None:
        self.payment_result = payment_result
        self.charged_users = []

    def charge(self, user_id: str, amount: int) -> PaymentResult:
        self.charged_users.append((user_id, amount))
        return self.payment_result
```

What it proves:

```text
charge_payment calls provider.charge(user_id, amount)
charge_payment converts PaymentResult into app-level result
```

This fake has two testing roles:

```text
stub -> returns controlled PaymentResult
spy  -> records how it was called
```

General name:

```text
test double
```

Use a test double when the thing being tested is orchestration, not the real side effect or real provider behavior.

## Project 02 Bottleneck 08: Stable Provider Config

Real payment providers need stable setup/config:

```text
Stripe api_key
Stripe environment
Razorpay merchant_id
Razorpay environment
```

These values do not change for every payment charge, so they belong on the provider object:

```python
class StripePaymentProvider:
    def __init__(self, api_key: str, environment: str, should_succeed: bool = True) -> None:
        self.api_key = api_key
        self.environment = environment
        self.should_succeed = should_succeed
```

Event data still belongs in the method call:

```python
provider.charge(user_id, amount)
```

Responsibility split:

```text
stable provider setup/config -> provider __init__
event/payment data           -> charge(...) arguments
```

`get_payment_provider(...)` currently owns wiring default sandbox config:

```python
return StripePaymentProvider("stripe-test-api-key", "sandbox")
```

This is the same rule from Project 01:

```text
stable config goes into the behavior object.
event data stays as method arguments.
```

## Project 02 Bottleneck 09: Module Responsibility Split

`payment.py` started to own too many different things:

```text
PaymentResult data shape
Provider protocol
Stripe/Razorpay provider behavior
provider-specific response conversion
provider selection
charge_payment orchestration
```

The code still worked, but navigation and ownership were becoming blurry.

So we split by responsibility:

```text
models.py          -> PaymentResult data shape
providers.py       -> Provider protocol, concrete providers, provider selection
payment.py         -> charge_payment orchestration
tests/test_payment.py -> tests and fake provider test double
```

Important rule:

```text
Do not split just because classes exist.
Split when a file has multiple responsibilities and navigation/ownership starts becoming unclear.
```

Current responsibility checkpoint:

```text
models.py owns data shape.
providers.py owns provider boundary behavior.
payment.py owns payment flow orchestration.
```

## Project 02 Bottleneck 10: Payment Failure Vs Provider Error

There are two different failure categories.

Normal payment failure:

```text
The provider processed the payment attempt and clearly told us the payment failed.
```

Examples:

```text
wrong OTP
wrong UPI PIN
insufficient balance
card declined
bank declined transaction
```

Provider/system error:

```text
The provider/integration could not reliably process the payment attempt.
```

Examples:

```text
provider timeout
provider API down
network failure
bad API key
unexpected provider response shape
our provider integration crashed
```

Key distinction:

```text
normal payment failure -> we know payment failed
provider/system error  -> we may not know what happened
```

Code boundary:

```python
class PaymentProviderError(Exception):
    pass
```

`PaymentProviderError` lives in `providers.py` because it describes a provider-boundary infra/integration failure.

`charge_payment(...)` translates that provider error into a safe app-level response:

```python
try:
    provider_result = provider.charge(user_id, amount)
except PaymentProviderError:
    return {
        "status": "failed",
        "message": "Payment provider unavailable",
    }
```

Responsibility split:

```text
provider boundary -> raises PaymentProviderError for infra/integration failures
charge_payment    -> converts provider error into app-level response
```

Important:

```text
Do not catch every Exception by default.
Catch the boundary error you intentionally understand.
```

## Project 03 Starting Context: API Key Management System

API keys solve this backend problem:

```text
When a client calls our API, how do we know who is calling and whether they are allowed?
```

Basic request pipeline:

```text
client request includes API key
-> backend validates API key
-> request is allowed or rejected
```

Without API key management:

```text
anyone can call the API
we do not know who is calling
we cannot revoke access
we cannot attach usage/billing/permissions to a caller
```

Project 03 starts with the smallest flow:

```text
create API key for a user
validate that key
reject unknown key
```

## Project 03 Bottleneck 01: Key String Vs Key Metadata

The first naive store held only key strings.

That was enough to answer:

```text
does this key exist?
```

But it could not cleanly answer:

```text
who owns this key?
when was it created?
has it been revoked?
```

So we introduced a data object:

```python
@dataclass
class APIKeyRecord:
    api_key: str
    user_id: str
    created_at: str
    revoked: bool
```

Responsibility:

```text
APIKeyRecord owns stored metadata for one API key.
```

This is a data object, like `PaymentResult` in Project 02.

## Project 03 Bottleneck 02: Existence Vs Validity

Once `APIKeyRecord` had `revoked`, validation needed a sharper meaning.

Old meaning:

```text
valid = key exists
```

New meaning:

```text
valid = key exists and is not revoked
```

Responsibility:

```text
validate_api_key owns deciding whether an incoming key is currently usable.
```

## Project 03 Bottleneck 03: Revoke Behavior And Caller Signal

Adding `revoked` as data was not enough. The system needed behavior:

```text
user wants to revoke an API key
```

`revoke_api_key(api_key, user_id)` now owns:

```text
find the matching key
make sure it belongs to the user
mark it revoked
tell caller whether a matching key was found
```

Return value:

```text
True  -> matching key found and revoked
False -> no matching key for that user
```

Important distinction:

```text
revoked usually means the record still exists but cannot be used.
deleted usually means the record is removed or hidden.
```

For API keys, revoke is often better than delete because audit/security systems may need to remember that the key existed.

## Project 03 Bottleneck 04: Store Responsibility

The first implementation used a global list directly.

The problem was not that in-memory storage is bad. For this project, an in-memory store is fine.

The pressure was:

```text
storage access logic was spreading across functions
```

So we introduced:

```python
class APIKeyStore:
    def add_api_key(self, api_key_record: APIKeyRecord) -> str:
        ...

    def find_record(self, api_key: str) -> APIKeyRecord | None:
        ...
```

Responsibility:

```text
APIKeyStore owns storing and finding API key records.
```

The current module has one shared store instance:

```python
api_key_directory = APIKeyStore()
```

This represents one in-memory system store, not one store per user. It can hold records for many users.

## Project 03 Bottleneck 05: Creation Workflow And Key Generation

`create_api_key(...)` began by directly generating the key string inside itself.

We extracted:

```python
def generate_api_key(user_id: str) -> str:
    ...
```

Responsibility:

```text
generate_api_key owns key string generation.
create_api_key owns the creation workflow.
```

Current `create_api_key(...)` does multiple steps:

```text
generate candidate key
check store for duplicate
create APIKeyRecord
save record in APIKeyStore
return key string
```

This is a reasonable tradeoff for now because `create_api_key(...)` is orchestrating the creation workflow and delegating details:

```text
key generation detail -> generate_api_key(...)
storage detail        -> APIKeyStore.add_api_key/find_record
metadata shape        -> APIKeyRecord
```

This is not "one function doing everything" in the same bad way as before. It is a workflow function coordinating smaller responsibility owners.

Remaining pressure:

```text
The duplicate-key loop exists, but testing it is hard because generate_api_key uses random internally.
```

## Project 03 Bottleneck 06: Hidden Randomness And Test Control

Production API keys should be unpredictable.

But tests need control.

The pressure:

```text
How do we test duplicate-key handling if generate_api_key(...) uses random internally?
```

Scenario we need to force:

```text
store already has "sk-existing-user_40"
first generated key  -> "sk-existing-user_40"  # collision
second generated key -> "sk-unique-user_40"    # unique
```

If random generation is hidden inside `create_api_key(...)`, the test cannot reliably force that sequence.

So we made key generation injectable:

```python
def create_api_key(
    user: str,
    key_generator: Callable[[str], str] = generate_api_key,
) -> str:
    ...
```

Normal code can still call:

```python
create_api_key("user_40")
```

Tests can pass a fake generator:

```python
generated_keys = ["sk-existing-user_40", "sk-unique-user_40"]

def fake_key_generator(user_id: str) -> str:
    return generated_keys.pop(0)
```

Responsibility split:

```text
generate_api_key(...) -> real key generation
fake generator        -> controlled test key generation
create_api_key(...)   -> creation workflow and duplicate avoidance
APIKeyStore           -> lookup/storage
```

This is dependency injection again:

```text
create_api_key depends on key generation, so tests can pass that dependency in.
```

Important distinction:

```text
Business behavior still wants unpredictable keys.
Tests want deterministic keys.
Good design lets both exist.
```

## Project 03 Bottleneck 07: API Keys Are Secrets

The old key generation style was not appropriate for secrets:

```python
random.randint(0, 1000)
```

Problems:

```text
small search space
predictable/general-purpose randomness
user_id embedded in the key
```

API keys are bearer secrets:

```text
whoever has the key can act as that caller
```

So generation should use secure randomness:

```python
import secrets

def generate_api_key(user_id: str) -> str:
    return f"sk-{secrets.token_urlsafe(32)}"
```

Important distinction:

```text
random.randint(...) uses normal pseudo-random generation.
secrets.token_urlsafe(...) uses OS-backed randomness through SystemRandom.
```

`user_id` is no longer embedded in the raw key. Ownership lives in metadata:

```python
APIKeyRecord.user_id
```

## Project 03 Bottleneck 08: Do Not Store Raw API Keys

Storing raw API keys is dangerous.

If the store leaks and raw keys are present:

```text
attackers can use those keys directly
```

Better boundary:

```text
raw API key -> shown/returned to user once
hashed API key -> stored by backend
```

Current helper:

```python
def hash_api_key(api_key: str) -> str:
    return hashlib.sha256(api_key.encode()).hexdigest()
```

Creation flow:

```text
generate raw API key
hash raw API key
store APIKeyRecord(api_key_hash=...)
return raw API key to caller
```

Validation flow:

```text
receive raw API key
hash incoming raw key
find record by hash
valid if record exists and is not revoked
```

Revoke flow:

```text
receive raw API key
hash incoming raw key
find record by hash
revoke only if user_id matches
```

Responsibility split:

```text
generate_api_key(...) -> secure raw key generation
hash_api_key(...)     -> raw key to stored hash conversion
APIKeyRecord          -> stores api_key_hash, not raw api_key
APIKeyStore           -> finds records by stored hash
public functions      -> accept/return raw keys at the system boundary
```

This is similar to password storage:

```text
do not store raw secret; store a hash.
```

## Project 03 Bottleneck 09: API Key Expiry And Current Time

The next pressure:

```text
API keys should not always live forever.
```

So validity grew again.

Before:

```text
valid = key exists and is not revoked
```

Now:

```text
valid = key exists and is not revoked and is not expired
```

That means the stored record needs expiry metadata:

```python
@dataclass
class APIKeyRecord:
    api_key_hash: str
    user_id: str
    created_at: datetime.datetime
    expires_at: datetime.datetime
    revoked: bool
```

Important responsibility split:

```text
APIKeyRecord        -> owns stored metadata, including expiry
create_api_key(...) -> decides created_at and expires_at when the key is created
validate_api_key(...) -> decides whether the key is valid at the current time
```

The subtle pressure is time.

This works in production:

```python
datetime.datetime.now()
```

But if `validate_api_key(...)` always reads the real clock internally, tests become harder to control.

Example:

```text
test wants to prove "this key is expired"
```

If the function secretly uses the real current time, the test has to wait for real time or build awkward setup around the wall clock.

So we made current time injectable:

```python
def validate_api_key(
    api_key: str,
    current_time: datetime.datetime | None = None,
) -> bool:
    if current_time is None:
        current_time = datetime.datetime.now()
```

Normal runtime usage can stay simple:

```python
validate_api_key(api_key)
```

Tests can freeze time:

```python
validate_api_key(api_key, datetime.datetime(2026, 9, 17, 10, 0, 0))
```

Mental model:

```text
validate_api_key owns the validity decision.
It does not need to hide the source of current time.
```

This is the same kind of dependency pressure we saw with random key generation:

```text
hidden randomness -> hard to test collisions
hidden current time -> hard to test expiry
```

## Project 03 Bottleneck 10: Validation Result And Dashboard Listing

The runtime validation flow needs more than a bool.

Incoming request:

```text
client sends raw API key
backend hashes it
backend finds the stored record
backend decides whether the key is usable
```

If validation returns only `True`, the backend still does not know who the request is acting as.

So validation now returns a safe result contract:

```python
@dataclass
class APIKeyValidationResult:
    is_valid: bool
    user_id: str | None
```

Valid result:

```python
APIKeyValidationResult(True, "user_40")
```

Invalid result:

```python
APIKeyValidationResult(False, None)
```

Why `user_id` matters after validation:

```text
authorization -> can this user access this resource?
business logic -> fetch this user's data
rate limiting -> count requests for this user
billing/usage -> charge or track usage for this user
audit logs -> record who performed the action
```

This also clarified the two sides of the API key system:

```text
dashboard/admin flow:
create key, revoke key, list keys

runtime request flow:
validate key on every incoming request
```

Dashboard listing pressure:

```text
user wants to see their API keys
```

But raw API keys are secrets. After creation, the dashboard should not show the full raw key again.

For now, listing returns stored metadata records:

```python
def list_api_keys(user_id: str) -> list[APIKeyRecord]:
    return api_key_directory.find_records_for_user(user_id)
```

Storage lookup belongs in the store:

```python
def find_records_for_user(self, user_id: str) -> list[APIKeyRecord]:
    return [
        api_key_record
        for api_key_record in self.api_keys_directory
        if api_key_record.user_id == user_id
    ]
```

Responsibility split:

```text
APIKeyValidationResult -> safe validation response
APIKeyStore            -> knows how records are stored/searched
list_api_keys(...)     -> dashboard use case for listing user's key records
validate_api_key(...)  -> runtime auth use case
```

Current limitation:

```text
listing returns APIKeyRecord, which includes api_key_hash.
```

That created the next pressure:

```text
dashboard output should not expose internal hash storage details
```

So we introduced a dashboard-safe display contract:

```python
@dataclass
class APIKeyDisplayRecord:
    key_id: str
    user_id: str
    created_at: datetime.datetime
    expires_at: datetime.datetime
    revoked: bool
```

The store still returns internal records:

```python
def find_records_for_user(self, user_id: str) -> list[APIKeyRecord]:
    ...
```

Then the dashboard use case converts them:

```python
def list_api_keys(user_id: str) -> list[APIKeyDisplayRecord]:
    records = api_key_directory.find_records_for_user(user_id)
    return [
        APIKeyDisplayRecord(
            record.key_id,
            record.user_id,
            record.created_at,
            record.expires_at,
            record.revoked,
        )
        for record in records
    ]
```

Responsibility split:

```text
APIKeyRecord        -> internal storage shape
APIKeyDisplayRecord -> safe dashboard output shape
APIKeyStore         -> finds stored records
list_api_keys(...)  -> converts internal records into dashboard output
```

Production dashboards usually include a safer display model with fields like:

```text
key id
key prefix
created_at
expires_at
revoked
last_used_at
```

The next pressure is the difference between:

```text
secret value used for authentication
public key identity used for dashboard management
```

## Project 03 Bottleneck 11: Public Key Identity Vs Secret Value

Dashboard management needs to identify one key row.

Example:

```text
user opens dashboard
dashboard lists API keys
user clicks revoke on one row
backend receives: revoke this specific key
```

The dashboard cannot send the full raw API key back, because raw API keys are secrets and are only shown once at creation time.

So we added a safe public identity:

```text
key_id
```

Important distinction:

```text
raw API key secret -> used by clients at runtime for authentication
api_key_hash       -> stored internally for validation lookup
key_id             -> safe dashboard identity for managing a key
```

`key_id` belongs in the stored record because the backend must be able to find the same key later:

```python
@dataclass
class APIKeyRecord:
    key_id: str
    api_key_hash: str
    user_id: str
    created_at: datetime.datetime
    expires_at: datetime.datetime
    revoked: bool
```

The display contract also exposes it:

```python
@dataclass
class APIKeyDisplayRecord:
    key_id: str
    user_id: str
    created_at: datetime.datetime
    expires_at: datetime.datetime
    revoked: bool
```

Revoke can now use the dashboard-safe id:

```python
def revoke_api_key(key_id: str, user_id: str) -> bool:
    record = api_key_directory.find_record_by_key_id(key_id)
    if record and record.user_id == user_id:
        record.revoked = True
        return True

    return False
```

Responsibility split:

```text
APIKeyRecord        -> stores both secret hash and public key identity
APIKeyDisplayRecord -> exposes safe dashboard fields, including key_id
APIKeyStore         -> finds records by hash, user_id, or key_id
validate_api_key    -> uses raw key -> hash for runtime auth
revoke_api_key      -> uses key_id + user_id for dashboard management
```

This is a common production shape:

```text
authentication path uses secrets
management path uses safe ids
```

## Project 03 Bottleneck 12: Module Responsibility Split

`api.py` started as a simple learning file.

Over time it accumulated:

```text
data contracts
in-memory storage
secret generation
hashing
creation workflow
validation workflow
revoke workflow
listing workflow
expiry policy
```

The code worked, but the module responsibility became too broad.

So we split by ownership:

```text
models.py
-> APIKeyRecord
-> APIKeyValidationResult
-> APIKeyDisplayRecord

store.py
-> APIKeyStore
-> api_key_directory

security.py
-> generate_api_key(...)
-> hash_api_key(...)

api.py
-> DEFAULT_API_KEY_LIFETIME
-> create_api_key(...)
-> validate_api_key(...)
-> revoke_api_key(...)
-> list_api_keys(...)
```

Why `DEFAULT_API_KEY_LIFETIME` stayed in `api.py`:

```text
generate_api_key(...) owns making a secure secret.
hash_api_key(...) owns converting raw secret to stored hash.
create_api_key(...) owns the lifecycle policy for a newly created key.
```

So the 30-day lifetime is a workflow/policy decision, not a secret-generation detail.

Responsibility split:

```text
models  -> data shapes
store   -> persistence-like lookup/storage behavior
security -> secret handling
api     -> use-case workflows and lifecycle policy
```

## Project 03 Closing Notes

Project 03 is wrapped.

What we built:

```text
API Key Management System
```

It owns two sides of API key behavior:

```text
dashboard/admin side
-> create API key
-> list API keys safely
-> revoke API key safely

runtime request side
-> receive raw API key
-> hash it
-> find stored record
-> check revoked/expired state
-> return validation result with user_id
```

Final mental model:

```text
raw API key secret -> shown once and used by clients for runtime authentication
api_key_hash       -> stored internally for validation lookup
key_id             -> safe public identity for dashboard management
```

Final module responsibilities:

```text
models.py
-> data contracts

store.py
-> in-memory persistence-like behavior

security.py
-> secret generation and hashing

api.py
-> use-case workflows and API key lifecycle policy
```

Main topics covered:

```text
dataclasses as contracts
in-memory store as temporary DB
secure secret generation
hashing secrets before storage
creation vs validation flow
dashboard management vs runtime auth flow
expiry with datetime
injecting current time for testability
validation result contracts
internal storage model vs display model
public key id vs secret value
module responsibility split
```

Production gaps intentionally left out:

```text
real database persistence
unique constraints/indexes
proper key-id generation
scopes/permissions
rate limiting
last_used_at tracking
audit logs
rotation workflow
service object with injected store
```

These are not forgotten. They are future pressure points for later projects.

## Phase 2 Direction: Advanced OOP, LLD, DB Design, And FastAPI

Phase 1 is complete after the first three foundation projects.

The next learning target is not more small isolated OOP examples. The next target is larger backend domains where object responsibilities, SOLID, design patterns, database design, and API boundaries all create real pressure.

New Phase 2 rule:

```text
Pure Python design first -> DB design second -> ORM/repository third -> FastAPI last
```

Why:

- If FastAPI comes first, route handlers can hide weak domain design.
- If SQLAlchemy comes first, ORM shape can accidentally become the domain model.
- If DB tables come first without domain pressure, schema design becomes memorization.
- If pure Python design comes first, we can ask what the objects own before adding persistence and HTTP.

Guardrails:

```text
No FastAPI route until we can explain what the route orchestrates.
No ORM model until we can explain what the domain object owns.
No database table until we can explain what invariant the database must protect.
```

Phase 2 should go deeper on:

```text
encapsulation
invariants
entities vs value objects
domain services vs application services
abstract base classes vs protocols
inheritance vs composition
polymorphism
state transitions
domain exceptions
SOLID principles
database constraints
transaction boundaries
repositories
unit of work
thin route handlers
```

Phase 2 should also build Big Tech LLD interview readiness.

That means Jatin should practice not only writing the code, but also explaining the design:

```text
requirements
actors/use cases
entities and relationships
class responsibilities
method/API contracts
state transitions
schema design
constraints and transactions
extensibility
tradeoffs
pattern/principle vocabulary
```

Phase 2 is considered successful only if the project work is paired with design explanation and timed LLD mock rounds after enough depth is built.

Design patterns will be learned through backend pressure, not as isolated trivia:

```text
Strategy
Factory
Adapter
Repository
Unit of Work
State
Command
Observer / Publisher-Subscriber
Decorator
Template Method
Chain of Responsibility
Specification
Builder
Singleton mostly as a caution
```

Phase 2 projects:

```text
1. Inventory and Order Management
2. Movie Ticket Booking
3. E-commerce Checkout Capstone if time allows
```

The first two projects are required. The third is the capstone if time allows, or it becomes the bridge into the Advanced Backend phase.

Teaching rule refinement:

```text
Pressure first -> Jatin reasons -> code/refactor -> reveal the concept name clearly.
```

The concept name matters for interviews, but it should come after the intuition. For example, first feel why replaceable pricing logic is useful, then name Strategy.

The old Rate Limiter and Background Job Runner ideas are not discarded. They move naturally into the Advanced Backend phase, where Redis, async workers, retries, concurrency, and production infrastructure make them more useful.

## LLD Continuity Across Later Phases

LLD remains in the loop during Phase 3 and Phase 4.

Phase 3 adds production backend pressure:

```text
scale
failure
async execution
queues
Redis
caching
retries
timeouts
idempotency
observability
multi-tenancy
```

Phase 4 adds AI backend pressure:

```text
ingestion
parsing
chunking
embeddings
vector search
RAG
streaming
citations
evals
cost/latency tracking
safety and access control
```

But the design questions stay:

```text
What owns this behavior?
What does this component know?
What should it not know?
What changes together?
What boundary protects this failure mode?
What invariant should code protect?
What invariant should storage protect?
```

## Project 04 Starting Context: Inventory And Order Management

Phase 2 starts with Inventory and Order Management.

Learning rule:

```text
Pure Python design first -> DB design second -> ORM/repository third -> FastAPI last
```

Current project boundary:

```text
Cart = user intent
Order = business commitment
Inventory = stock truth
Order workflow = coordinates whether the commitment can happen
```

For now, the project starts when the user attempts to place an order or checkout. It is not building the cart UI or cart-management system.

Starter responsibility:

```text
accept requested items -> check inventory -> update inventory if valid -> return result to caller
```

## Project 04 Bottleneck 01: Boolean Result Is Too Weak

The first naive version returned only `True` or `False`.

That worked while there was one failure reason, but quickly became weak:

```text
False could mean product not found.
False could mean insufficient stock.
False could mean invalid requested quantity later.
```

The caller needs a stable result contract, not only a boolean.

Introduced:

```text
OrderRecord(success, message, order_id)
```

Concept name:

```text
Result Contract / Result Object
```

Why it matters:

- the caller gets a clear success/failure signal
- the caller gets a human-readable reason
- tests can assert deterministic result values
- future API responses have a clearer shape

## Project 04 Bottleneck 02: Single-Item Order Is Too Small

The next requirement was multi-product order placement.

A real order can request:

```text
2 iphones
1 macbook
3 airpods
```

So the input needed a new contract:

```text
UserOrder(product_name, quantity)
```

The workflow now accepts:

```text
list[UserOrder]
```

This moved the design from:

```text
one product + one quantity
```

to:

```text
many requested order items
```

## Project 04 Bottleneck 03: Partial Inventory Update

Multi-product orders created a more serious pressure.

Bad behavior:

```text
reduce iphone stock
then discover macbook stock is insufficient
return failure
but iphone stock is already changed
```

That creates a half-updated system.

Jatin proposed the right pure-Python shape:

```text
copy inventory -> apply requested changes to the copy -> commit only if the whole order succeeds
```

Important Python detail:

```python
inventory = inventory_copy
```

only rebinds the local function name. It does not update the caller's dict.

To commit into the same dict object held by the caller:

```python
inventory.clear()
inventory.update(inventory_copy)
```

Concept name:

```text
All-or-nothing update / commit-after-validation
```

This is the pure-Python intuition behind a later database transaction:

```text
try changes inside a protected boundary -> commit only if all checks pass
```

Current Project 04 tests cover:

- single-item success
- single-item insufficient stock
- missing product
- multi-item success
- multi-item failure when one item is unavailable
- multi-item failure when one item does not exist

Current test result:

```text
6 passed
```

Next pressure:

```text
place_order(...) owns both order workflow and inventory mutation.
Who should own stock behavior?
```

## Project 04 Bottleneck 04: Order Workflow Knows Inventory Internals

After multi-product all-or-nothing updates worked, `place_order(...)` still knew too much.

It knew:

```text
inventory is a dict
product names are keys
quantities are values
how to copy inventory
how to check stock
how to reduce stock
how to commit copied inventory
```

That means order workflow was coupled to inventory storage details.

Jatin's intuition:

```text
place_order should ask whether the order can be fulfilled.
Inventory behavior should live in an inventory service that owns the inventory data.
```

Introduced:

```text
InventoryService
```

Current responsibility split:

```text
place_order:
  coordinates order placement
  asks inventory service to apply the stock behavior
  returns the order result

InventoryService:
  owns the raw inventory dict
  checks product existence
  checks available quantity
  applies all-or-nothing stock reduction
  commits inventory changes only after validation succeeds
```

Important learning:

```text
Do not change too many boundaries at once.
```

The attempted move to `list[InventoryProduct]` plus `InventoryService` made the refactor harder to reason about. We kept the storage shape as:

```python
dict[str, int]
```

and first wrapped behavior around it.

## Python Detail: `.copy()` On A Dict

For the current inventory:

```python
inventory = {"iphone": 5, "macbook": 3}
inventory_copy = inventory.copy()
```

`.copy()` creates a new shallow dict with the same key-value pairs.

Changing the copy:

```python
inventory_copy["iphone"] = 2
```

does not change the original dict.

Because the current values are integers, a shallow copy is enough. If values become nested mutable objects later, shallow vs deep copy will matter more.

## Encapsulation

Working definition:

```text
I know what outcome I need, but I delegate to the object/service that knows how its own data should be handled.
```

Sharper definition:

```text
Encapsulation hides internal data structure and exposes behavior through methods.
```

In Project 04:

```text
place_order(...) no longer directly reads or updates inventory[item.product_name].
```

Instead:

```text
place_order(...) asks InventoryService to handle stock behavior.
```

Concept name:

```text
Encapsulation / Responsibility Ownership
```

Current test result:

```text
6 passed
```

Next pressure for tomorrow:

```text
InventoryService currently returns OrderRecord.
Is that inventory responsibility, or is order result language leaking into the inventory boundary?
```

## Project 04 Bottleneck 05: Inventory Service Speaks Order Language

`InventoryService.reduce_stock_for_order(...)` originally returned:

```text
OrderRecord
```

That meant inventory code knew order-level language:

```text
order_id
"Order placed"
```

But inventory should not know whether an order was placed. It should only report whether inventory work succeeded.

Introduced:

```text
InventoryResult(success, message)
```

Responsibility split:

```text
InventoryService:
  returns inventory-level result

place_order:
  translates inventory-level result into order-level result
```

Concept:

```text
Boundary-specific result contracts
```

## Project 04 Bottleneck 06: Raw Quantity Dict Is Too Weak

The inventory shape:

```python
dict[str, int]
```

could only express:

```text
product name -> quantity
```

But inventory records often need richer fields:

```text
product name
quantity
SKU
category
other metadata later
```

Introduced:

```text
InventoryProduct(product_name, quantity, sku, category)
```

SKU means:

```text
Stock Keeping Unit
```

It is a stable business/internal identifier for tracking a specific sellable item or variant.

Storage changed to:

```python
dict[str, InventoryProduct]
```

Important design win:

```text
place_order(...) did not need to know that inventory storage changed.
```

That is the payoff from the `InventoryService` boundary.

## Python Detail: Shallow Copy With Object Values

With:

```python
inventory_copy = self.inventory.copy()
```

Python creates a new dict container, but it does not clone the `InventoryProduct` objects inside.

Mental model:

```text
self.inventory["iphone"] ----\
                              > InventoryProduct(quantity=5)
inventory_copy["iphone"] ----/
```

So this would mutate the shared product object:

```python
inventory_copy["iphone"].quantity -= 2
```

That means the original inventory would change before commit, breaking all-or-nothing behavior.

Current implementation avoids that by replacing the copied entry with a new product object:

```python
inventory_copy[item.product_name] = InventoryProduct(...)
```

## Project 04 Bottleneck 07: Quantity Invariant

Line-level workflow checks prevent an order from subtracting too much stock, but they do not prevent invalid inventory records from existing in the first place.

Bad object:

```python
InventoryProduct("iphone", -5, "IPHONE-15", "phone")
```

This should not exist.

Invariant:

```text
InventoryProduct.quantity >= 0
```

An invariant is a rule that must always remain true for an object or system.

Why `InventoryProduct` owns this check:

```text
negative quantity makes the inventory product itself invalid
```

The rule is not only about `place_order(...)`; it also matters for future workflows such as stock imports, admin edits, warehouse syncs, and repository loading.

Implemented with:

```text
InventoryProduct.__post_init__
```

Concept:

```text
Invariant Protection
```

Current test result:

```text
7 passed
```

Next pressure:

```text
UserOrder.quantity can still be zero or negative.
Should an ordered item protect its own quantity rule too?
```

## Project 04 Bottleneck 08: Requested Quantity Invariant

After protecting `InventoryProduct.quantity`, another invalid state was still possible:

```python
UserOrder("iphone", 0)
UserOrder("iphone", -2)
```

That is dangerous because negative requested quantity can accidentally increase stock:

```text
5 - (-2) = 7
```

Invariant:

```text
UserOrder.quantity > 0
```

Why `UserOrder` owns this check:

```text
zero or negative quantity makes the requested order item itself invalid
```

Implemented with:

```text
UserOrder.__post_init__
```

Dataclass detail:

```text
__init__ = generated constructor that assigns fields
__post_init__ = hook that runs after generated field assignment
```

Use `__post_init__` when a dataclass should keep generated constructor convenience but also enforce validation/setup.

Concept:

```text
Input Invariant Protection
```

## Project 04 Bottleneck 09: Order Workflow Needs An Owner

The standalone `place_order(...)` function had grown into an order workflow.

It coordinated:

```text
requested order items
inventory stock reduction
inventory result -> order result translation
caller-facing OrderRecord
```

Jatin's intuition:

```text
There should be an OrderService, and place_order should be part of it.
OrderService should hold InventoryService and orchestrate the workflow.
```

Introduced:

```text
OrderService
```

Current collaboration:

```text
OrderService.place_order(order_list)
  -> asks InventoryService.reduce_stock_for_order(order_list)
  -> receives InventoryResult
  -> returns OrderRecord
```

Responsibility split:

```text
OrderService:
  owns order placement workflow

InventoryService:
  owns inventory data and stock behavior

InventoryProduct:
  protects inventory-product validity

UserOrder:
  protects requested-item validity

OrderRecord:
  caller-facing operation result
```

LLD mental model:

```text
LLD = responsibility assignment + boundaries + invariants + collaboration
```

Meaning:

```text
responsibility assignment = who owns each job
boundaries = what each component can see or touch
invariants = rules that must always stay true
collaboration = how components ask each other to do work
```

Concept now visible:

```text
Single Responsibility Principle intuition
```

Current test result:

```text
8 passed
```

Next pressure:

```text
OrderService returns order_id="order-1", but no real Order object exists yet.
```

## Project 04 Bottleneck 10: Order Id Without An Order

`OrderService.place_order(...)` returned:

```python
OrderRecord(True, "Order placed", "order-1")
```

But no actual order existed inside the system.

That created a mismatch:

```text
caller receives an order_id
but backend has no Order object tied to that id
```

Why this matters:

After order placement, later workflows need the order id as a handle:

```text
view order details
cancel order
track order
retry payment
support lookup
refund later
```

If no internal order exists, the id is meaningless.

Important distinction:

```text
OrderRecord = caller-facing operation result / receipt
Order = internal domain object / business record
```

`OrderRecord` answers:

```text
Did the operation succeed?
What message should the caller see?
What order id should the caller receive?
```

`Order` answers:

```text
What was ordered?
What is the order id?
What is the current status?
```

Introduced:

```text
Order(order_id, items, status)
```

Current creation rule:

```text
inventory failure -> do not create Order
inventory success -> create Order with status PLACED
```

Current collaboration:

```text
OrderService.place_order(order_list)
  -> InventoryService.reduce_stock_for_order(order_list)
  -> if failure, return OrderRecord failure
  -> if success, create Order
  -> store Order in self.orders
  -> return OrderRecord success
```

Important correction:

```text
Order should not be created from OrderRecord.
```

`Order` should be created from business facts:

```text
order_id
items
status
```

Current test result:

```text
8 passed
```

Next pressure:

```text
Orders are stored in an internal list, but there is no retrieval by order_id yet.
```

## Project 04 Bottleneck 11: Order Storage Responsibility

After `Order` existed, `OrderService` still directly owned:

```text
order list
order id generation
saving orders
finding orders by id
```

That gave `OrderService` multiple reasons to change:

```text
workflow rules change
storage representation changes
lookup mechanics change
id generation changes
```

Introduced:

```text
OrderRepository
```

Current split:

```text
OrderService:
  owns order workflow/orchestration

OrderRepository:
  owns order storage mechanics
  generates next order id
  saves order
  gets order by id
```

Concept:

```text
Single Responsibility Principle
```

Meaning:

```text
A class should have one main responsibility, or one main reason to change.
```

## Project 04 Bottleneck 12: Order Retrieval

The caller received:

```text
order_id
```

but should not inspect:

```python
order_repository.orders
```

directly.

Added:

```text
OrderService.get_order(order_id)
```

This lets callers ask for behavior instead of knowing the internal storage structure.

Tests cover:

```text
known order id -> Order
unknown order id -> None
```

## Project 04 Bottleneck 13: Cancellation Lifecycle

Next lifecycle requirement:

```text
A placed order can be cancelled.
```

Added:

```text
OrderStatus.CANCELLED
OrderService.cancel_order(order_id)
```

Current cancellation behavior:

```text
missing order -> failure
placed order -> status becomes CANCELLED
already cancelled order -> failure
```

Concept:

```text
State transition
```

Current valid transition:

```text
PLACED -> CANCELLED
```

Invalid/no-op transition:

```text
CANCELLED -> CANCELLED
```

## Project 04 Bottleneck 14: Cancellation Has Inventory Side Effect

Cancelling an order only changed status at first.

But after placement:

```text
inventory 5 -> place order for 3 -> inventory 2
```

cancellation should restore stock:

```text
cancel order -> inventory 5
```

Added:

```text
InventoryService.restore_stock_for_order(order.items)
```

Current cancellation sequence:

```text
find order
reject missing/already-cancelled order
restore inventory
if restore succeeds, mark order CANCELLED
return OrderRecord
```

Concept:

```text
State transition with side effects
```

Important deeper pressure:

```text
cancellation now changes inventory and order status
```

If one succeeds and the other fails, the system can become inconsistent.

This reveals:

```text
atomicity / transaction boundary
```

Atomicity means:

```text
either all related changes happen, or none happen
```

## Project 04 Bottleneck 15: Inventory Storage Responsibility

After splitting order storage, inventory had a similar smell.

`InventoryService` owned:

```text
inventory behavior
raw inventory dict
dict lookup
dict updates
commit mechanics
```

Introduced:

```text
InventoryRepository
```

First split:

```text
InventoryRepository owns raw dict, copy, replace
```

Then Jatin noticed a subtle leak:

```text
InventoryService still indexed the dict directly
```

Refined split:

```text
InventoryService:
  loops over requested order items
  owns stock business behavior
  asks storage to get/save/commit products

InventoryRepository:
  owns how inventory products are stored and found
  begins a change set
  gets product by name from that change set
  saves product into that change set
  commits change set
```

Introduced:

```text
InventoryChangeSet
```

Intuition:

```text
temporary pending inventory changes before commit
```

Earlier:

```python
inventory_copy = inventory.copy()
```

Now:

```text
change_set = InventoryChangeSet(inventory.copy())
```

This makes the temporary all-or-nothing update boundary explicit.

Current test result:

```text
13 passed
```

Resume point:

```text
Formalize repository-shaped storage boundaries, then deepen transaction/atomicity.
```

## Project 04 Concept: Repository Pattern

`OrderRepository` and `InventoryRepository` are currently in-memory repository objects.

They sit between business logic and stored data.

Repository answers this responsibility question:

```text
Who should know how domain objects are saved and fetched?
```

Answer:

```text
Repository.
```

In the current pure-Python project:

```text
OrderRepository stores orders in an in-memory list.
InventoryRepository stores inventory products in an in-memory dict.
```

That is fine for now because the project is still in the pure-Python design phase.

In production, the storage mechanism may become:

```text
Postgres
Redis
files
external services
```

At that point, the repository acts as a layer between:

```text
business layer / services
```

and:

```text
database or persistence calls
```

Why this matters:

```text
OrderService should not know whether orders are stored in a list, dict, Postgres table, Redis key, or external service.
```

Instead, business code should depend on repository behavior:

```text
save order
get order by id
save inventory product
get inventory product
commit inventory changes
```

This keeps responsibilities separate:

```text
Service = business workflow
Repository = persistence/storage access
Domain object = business state and invariants
```

This also reduces coupling:

```text
Changing database/storage mechanics should mostly change the repository, not the business workflow.
```

Current vocabulary:

```text
OrderRepository -> in-memory order repository
InventoryRepository -> in-memory inventory repository
```

Current code now uses repository names because the design role is clear.

Practical LLD takeaway:

```text
When business logic needs to save/fetch domain objects, add a repository boundary instead of coupling services directly to DB/list/dict mechanics.
```

In production:

```text
Service -> Repository -> DB/Redis/file/external service
```

This keeps the business layer from knowing persistence details.

## Project 04 Bottleneck 16: Save Failure After Inventory Change

After repository boundaries were introduced, a deeper workflow pressure became visible.

Current placement flow:

```text
OrderService.place_order(order_list)
  -> InventoryService.reduce_stock_for_order(order_list)
  -> OrderRepository.next_order_id()
  -> OrderRepository.save(order)
```

The dangerous failure case:

```text
inventory reduction succeeds
order save fails
```

Bad final state:

```text
stock is reduced
but no saved order exists
```

This is not an inventory validation failure. Inventory did its job correctly. The problem is that `place_order(...)` is a multi-step workflow touching more than one piece of state.

Starter-level recovery:

```text
reduce stock
if stock reduction fails, return failure

try to create and save the order
if order save fails:
  restore the stock that was reduced
  return order-placement failure
```

This recovery belongs in `OrderService.place_order(...)` because `OrderService` owns the placement workflow. `InventoryService` should not know that order saving failed; it should only provide the behavior needed to reduce or restore stock.

Concept name:

```text
manual rollback / compensating action
```

Mental model:

```text
If step B fails after step A already changed state,
undo step A before returning failure.
```

In this project:

```text
step A = reduce inventory
step B = save order
undo A = restore inventory
```

This is still not a full database transaction or full Unit of Work. It is the pure-Python intuition behind why transaction boundaries matter.

## Project 04 Bottleneck 17: Broad Exception Handling Hides Bugs

The first rollback implementation used:

```python
except Exception:
```

That fixed the rollback pressure, but created a new one:

```text
Every failure was treated as order-placement failure.
```

Different failures should not always be handled the same way.

Useful split:

```text
business failure -> normal failed result
known recoverable technical failure -> rollback and return safe failed result
unexpected bug -> allow it to surface
```

In this project:

```text
stock unavailable / product missing
  -> business failure
  -> InventoryResult(False, ...)
  -> no exception needed

order repository save/id failure after inventory changed
  -> known recoverable persistence failure
  -> restore inventory
  -> return OrderRecord(False, "Order placement failed", None)

programming bug / unexpected runtime error
  -> do not hide it under OrderRecord
  -> let the real error move upward to tests, logs, framework, or monitoring
```

So we introduced:

```python
class OrderRepositoryError(Exception):
    pass
```

Mental model:

```text
Exception = broad parent category
OrderRepositoryError = specific child category
```

Now `OrderService.place_order(...)` catches only:

```python
except OrderRepositoryError:
```

This means:

```text
OrderService only catches the repository failure it knows how to recover from.
```

Allowed to surface means:

```text
do not catch that error here
let it travel upward to a higher boundary
```

In tests, that higher boundary is pytest.

In a backend API, that higher boundary may be the route/controller/framework, which usually logs the stack trace and returns a safe `500 Internal Server Error` response.

Current DB-design distance:

```text
about 4-5 focused topics away
```

Likely remaining topics before DB design:

```text
rollback failure pressure
cleaner transaction boundary / Unit of Work intuition
service interfaces / dependency inversion basics
idempotency basics
module split when file pressure appears
```

## Project 04 Bottleneck 18: Rollback Failure Still Leaves Broken State

After handling order-save failure with manual rollback, we asked the next deeper question:

```text
What if rollback itself fails?
```

The dangerous flow:

```text
reduce inventory
order save fails
try to restore inventory
inventory restore also fails
```

Bad final state:

```text
order was not saved
inventory is still reduced
```

Returning a clearer failure message is useful, but it does not fix the broken state.

The message:

```text
Order placement failed and inventory restore failed
```

only tells the caller/backend layer:

```text
this is not a clean business failure
state may now need repair
```

This is the limitation of manual rollback:

```text
do step A
do step B
if B fails, manually undo A
```

The undo step can also fail.

This pressure is what pushes the design toward a real transaction boundary.

Transactional boundary:

```text
the set of operations that must succeed or fail together
```

For order placement:

```text
reduce inventory
save order
```

These two operations belong in the same transaction boundary because one without the other breaks business correctness.

With a relational database, the mental model becomes:

```text
BEGIN TRANSACTION

update inventory
insert order

COMMIT
```

If anything fails:

```text
ROLLBACK
```

The database gives atomicity:

```text
both changes happen
or neither change happens
```

Refined takeaway:

```text
Pure in-memory Python design helped reveal the pressure.
The pressure is multi-step state consistency.
To handle it properly in production, we need transactional storage.
A relational DB gives us transactions and atomicity.
```

This is the bridge from LLD into DB design.

## Project 04 Bottleneck 20: Retrying Order Placement Can Duplicate Work

The client may retry an order request when the first response is lost even though the server completed the operation.

Without a stable request identity, the retry can:

```text
create a second order
reduce inventory a second time
```

The caller now supplies one `idempotency_key` for one logical order-placement operation. It reuses that key for network retries and generates a different key for a genuinely new operation.

Responsibility split:

```text
Caller = generate and reuse the key
OrderRepository = save and find orders by the key
OrderService = decide whether the call is new, a retry, or a conflict
```

Current rules:

```text
new key + valid order -> create the order
same key + same items -> return the original order
same key + different items -> reject as a conflict
failed attempt with no saved order -> allow a later retry
```

Concept name:

```text
Idempotency
```

An idempotent operation can be repeated without repeating its intended side effects.

The current in-memory lookup is educational but not concurrency-safe. In the database version, a unique constraint must enforce key uniqueness, and the idempotency check and state changes must share the transaction boundary.

## Project 04 Bottleneck 19: OrderService Owns Transaction Mechanics

After rollback failure, the next pressure was inside `OrderService.place_order(...)`.

The method was owning both:

```text
order placement workflow
rollback / recovery mechanics
```

That made `OrderService` responsible for too many zones:

```text
ask inventory to reduce stock
create order id
create order
save order
decide when rollback should happen
perform rollback
handle rollback failure
```

The business workflow belongs in `OrderService`.

The transaction boundary belongs somewhere else.

Concept name:

```text
Unit of Work pattern
```

Unit of Work means:

```text
one object that tracks or coordinates a group of related changes
and commits or rolls them back as one unit
```

In Project 04, one unit of work is:

```text
place one order
```

That unit includes:

```text
reduce inventory
save order
```

Responsibility split:

```text
OrderService = order placement business workflow
InventoryService = inventory business behavior
OrderRepository = order storage access
InventoryRepository = inventory storage access
UnitOfWork = transaction boundary / commit / rollback mechanics
```

Why Unit of Work owns both repositories:

```text
Repository owns one storage area.
UnitOfWork owns the transaction boundary across repositories.
```

For order placement, both storage areas must move together:

```text
inventory reduced + order saved
```

or:

```text
inventory unchanged + order not saved
```

In the current pure-Python version, `InMemoryUnitOfWork` snapshots:

```text
inventory_repository.inventory
order_repository.orders
```

Then:

```text
begin() -> take snapshots
commit() -> discard snapshots because changes are accepted
rollback() -> restore repositories from snapshots
```

With a DB later, the same shape becomes:

```text
begin() -> open DB transaction/session
commit() -> db commit
rollback() -> db rollback
```

Important distinction:

```text
Unit of Work = application/code-level transaction owner
DB transaction = storage-level atomicity mechanism
```

The DB transaction does not remove the Unit of Work object. Usually, the DB-backed Unit of Work controls the DB transaction.

Current `except Exception` intuition:

```python
except Exception:
    self.unit_of_work.rollback()
    raise
```

This does not hide unexpected bugs. It restores state first, then re-raises the original error so it can surface to tests/logs/framework.

Python object-reference reminder:

```python
self.inventory_repository = inventory_repository
```

stores a reference to the same repository object.

And:

```python
self.inventory_repository.inventory.clear()
```

does not make the inventory `None`.

It mutates the same dict object into:

```python
{}
```

Then:

```python
self.inventory_repository.inventory.update(snapshot)
```

refills the same dict object with the snapshot contents.

Why not assign a new dict?

```python
self.inventory_repository.inventory = snapshot
```

Because external code/tests may still hold a reference to the original inventory dict. `clear()` + `update()` preserves the original dict object and changes its contents.

## Project 04 Important Concept: Dataclass vs Protocol

This distinction is important for LLD.

A dataclass is for real objects that carry data.

Example:

```python
@dataclass
class Order:
    order_id: str
    items: list[UserOrder]
    status: OrderStatus
```

This creates actual runtime objects:

```python
order = Order("order-1", items, OrderStatus.PLACED)
```

The dataclass gives useful generated methods such as:

```text
__init__
__eq__
__repr__
```

Mental model:

```text
dataclass = real object / data shape
```

A protocol describes expected behavior or shape.

Example:

```python
class UnitOfWork(Protocol):
    inventory_repository: InventoryRepository
    order_repository: OrderRepository

    def begin(self) -> None:
        ...

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...
```

This says:

```text
Any object with these attributes and methods can be treated as a UnitOfWork.
```

Mental model:

```text
Protocol = behavior contract / promise
Concrete class = actual implementation
```

In Project 04:

```text
Order = dataclass
because it is real order data.

InventoryProduct = dataclass
because it is real inventory-product data.

InMemoryUnitOfWork = concrete class
because it actually snapshots, commits, and rolls back.

UnitOfWork = Protocol
because OrderService only needs the transaction-boundary behavior,
not the exact implementation.
```

Key difference:

```text
Dataclass answers: what data does this object hold?
Protocol answers: what behavior must this object provide?
```

This connects to Dependency Inversion Principle.

Dependency Inversion Principle:

```text
High-level business code should not depend on low-level concrete details.
Both should depend on abstractions/contracts.
```

In this project:

```text
OrderService = high-level business workflow
InMemoryUnitOfWork = low-level in-memory transaction implementation
UnitOfWork protocol = abstraction / contract
```

Old dependency:

```text
OrderService -> InMemoryUnitOfWork
```

Better dependency:

```text
OrderService -> UnitOfWork protocol
InMemoryUnitOfWork -> satisfies UnitOfWork protocol
```

Why it is called inversion:

```text
Instead of high-level code pointing directly at a low-level implementation,
both sides point toward a stable contract.
```

Practical payoff:

```text
Later we can introduce DatabaseUnitOfWork without changing the core idea of OrderService.
```

Runtime vs type expectation:

```python
unit_of_work = InMemoryUnitOfWork(inventory_repository, order_repository)
order_service = OrderService(inventory_service, unit_of_work)
```

At runtime, we still initialize a concrete object:

```text
InMemoryUnitOfWork
```

But `OrderService` is typed against the contract:

```python
def __init__(self, inventory_service: InventoryService, unit_of_work: UnitOfWork):
```

So:

```text
runtime object = InMemoryUnitOfWork
type/expectation = UnitOfWork protocol
```

This is abstraction.

```text
Abstraction = what behavior is needed
Implementation = how that behavior is done
```

In Project 04:

```text
Abstraction:
  begin()
  commit()
  rollback()
  order_repository

Implementation:
  copy snapshots
  clear/update dict
  restore list
```

Protocol is one way to express abstraction in Python. Dependency Inversion uses this abstraction so high-level workflow code does not depend directly on low-level concrete classes.

## Project 04 DB Design 01: Derive Tables From Persistent Business Information

Database design did not start by converting each dataclass into a table.

The starting question was:

```text
Which business information must still exist after the Python process stops or restarts?
```

This prevents database design from becoming a mechanical class-to-table exercise.

The first persistent requirement was inventory:

```text
The system must remember which products are stocked
and how many units of each product are available.
```

Two concepts were distinguished:

```text
Inventory = the overall collection of stocked products
InventoryProduct = one individual stocked product in that collection
```

The current requirements describe only one inventory. There is no warehouse, seller, shop, or location dimension yet. Therefore, a separate `inventories` table would add structure without solving a current requirement.

One row in `inventory_products` can represent one stocked product, while all rows collectively represent the current inventory.

Persistent fields derived so far:

```text
sku
product_name
category
quantity
```

### Business identity versus database identity

SKU was selected as the reliable business identifier because a product name is descriptive and may change or be duplicated.

However, SKU was not selected as the primary key.

The design separates:

```text
id  = stable internal database identity
sku = unique business identity
```

Other tables should reference the stable internal `id`. If a SKU changes later, the relationships still point to the same product row.

A foreign key could technically reference SKU, and PostgreSQL could restrict or cascade updates. The problem is not that consistency would be impossible. The problem is that relationships would become coupled to a mutable business value.

Current table design:

```text
inventory_products
------------------
id            primary key
sku           unique, not null
product_name  not null
category      nullable
quantity      not null
```

The database must also protect the existing domain invariant:

```sql
CHECK (quantity >= 0)
```

Python validation gives fast domain feedback, while the PostgreSQL constraint protects stored data even if another service, script, migration, admin tool, direct SQL statement, or programming bug bypasses that Python object.

## Project 04 DB Design 02: Persisting An Order With Multiple Items

The order information that must survive a restart currently includes:

```text
order id
status
idempotency key
created_at
ordered items
```

`created_at` was added as a database-design requirement even though it is not yet present in the Python domain model. It supports history, ordering, operational queries, and possible expiry rules for idempotency records.

The main pressure was this Python field:

```python
items: list[UserOrder]
```

Each item contains a product reference and requested quantity.

PostgreSQL can technically store this information in JSON, arrays, or custom composite structures. The reason not to use one nested `orders.items` column here is relational protection and access—not an inability to store nested data.

If items are embedded in one column, ordinary PostgreSQL constraints cannot cleanly protect every embedded value:

```text
Does every embedded product_id reference a real product?
Is every embedded quantity greater than zero?
```

It also makes routine relational operations more specialized:

```text
find every order containing a product
sum ordered quantities for a product
update one item
join item data with product data
index common product lookups
```

The solution is a separate `order_items` table.

Example Python representation:

```python
items = [
    UserOrder("iphone", 2),
    UserOrder("macbook", 1),
]
```

Equivalent relational representation:

```text
orders
------
id
1

order_items
------------------------------------
id   order_id   product_id   quantity
1    1          42           2
2    1          81           1
```

Both item rows belong to order `1`. Each item row points to one inventory-product row.

Proposed table shape:

```sql
CREATE TABLE order_items (
    id BIGSERIAL PRIMARY KEY,
    order_id BIGINT NOT NULL REFERENCES orders(id),
    product_id BIGINT NOT NULL REFERENCES inventory_products(id),
    quantity INTEGER NOT NULL CHECK (quantity > 0),
    UNIQUE (order_id, product_id)
);
```

Constraint meanings:

```text
order_id foreign key
  -> an item cannot belong to an order that does not exist

product_id foreign key
  -> an item cannot reference a product that does not exist

quantity check
  -> an ordered quantity must be greater than zero

unique order_id + product_id
  -> one product appears at most once in one order under the current model
```

The Python list has not disappeared. Its storage representation has changed:

```text
Python domain representation:
one Order object containing a list of UserOrder objects

Relational representation:
one orders row connected to multiple order_items rows
```

The repository or ORM will query the related rows and reconstruct the list when loading an order.

Current relationship model:

```text
orders             one -> many order_items
inventory_products one -> many order_items
```

The larger relationship between orders and products is many-to-many, with `order_items` acting as the connecting record and carrying relationship-specific data such as `quantity`.

Key lesson:

```text
Arrays and JSON conveniently store nested data.
Separate relational rows let PostgreSQL directly protect identities,
relationships, constraints, and common query paths.
```

Next database-design pressure:

```text
Derive the orders table and decide how PostgreSQL should protect
order identity, lifecycle status, idempotency, and timestamps.
```

## Project 04 DB Design 03: Designing The Orders Table From Business Rules

This section records the complete reasoning used to derive the first version of the `orders` table. It is intentionally detailed because this is the first database-design project.

### What one row represents

One row in `orders` represents one successfully created order.

Information belonging to the overall order includes:

```text
identity
lifecycle status
idempotency key
creation time
last-update time
```

The products and requested quantities do not live directly in this row. They are represented by related `order_items` rows.

### Internal identity versus public order identity

Two identifiers were chosen:

```text
id           = internal database identity
order_number = public business identity
```

Example:

```text
id = 1
order_number = ORD-2026-000001
```

`orders.id` is the primary key. Related tables use it as their foreign key:

```text
order_items.order_id -> orders.id
```

`order_number` is used by callers, APIs, customers, and support staff:

```text
GET /orders/ORD-2026-000001
```

It must be both `UNIQUE` and `NOT NULL` so one public number identifies at most one order and every order has one.

The separation prevents database relationships from depending on business formatting. If new orders later change from:

```text
order-1
```

to:

```text
ORD-2026-000001
```

the foreign-key design remains unchanged because `order_items` still references the stable numeric `id`.

### Protecting lifecycle status

The current domain permits:

```text
PLACED
CANCELLED
```

PostgreSQL must reject missing or invalid values such as:

```text
PLACEDD
UNKNOWN
cancel
```

Two valid designs were discussed.

PostgreSQL enum:

```sql
CREATE TYPE order_status AS ENUM ('PLACED', 'CANCELLED');
```

Then:

```sql
status order_status NOT NULL
```

Alternative text design:

```sql
status TEXT NOT NULL
CHECK (status IN ('PLACED', 'CANCELLED'))
```

The enum gives a clear named PostgreSQL type and strong domain vocabulary. The tradeoff is that adding, renaming, or removing enum values requires a database migration. Text with a check constraint is more portable and can be easier to reshape through ordinary constraint migrations.

Because this project explicitly targets PostgreSQL and currently has a small, known lifecycle, the starter design uses a PostgreSQL enum.

No database default is assigned to `status`.

Reason:

```text
OrderService decides that the completed business workflow creates a PLACED order.
PostgreSQL validates that the supplied state is present and allowed.
```

If the application forgets to provide a status, the insert should fail instead of silently creating a placed order.

This preserves the boundary:

```text
business service = chooses business state
database          = protects stored-state validity
```

### Enforcing idempotency

Every successfully created order stores the caller-provided logical request identity:

```sql
idempotency_key ... UNIQUE NOT NULL
```

The two constraints solve different problems:

```text
NOT NULL
  -> no successful order can omit its idempotency identity

UNIQUE
  -> no two orders can represent the same logical request
```

The unique constraint also closes a concurrency gap that application-only lookup cannot close safely:

```text
Request A checks key -> missing
Request B checks key -> missing
Request A inserts
Request B inserts
```

Without database enforcement, both requests might create orders. With the unique constraint, PostgreSQL allows only one persisted row for that key. The application must later handle the losing insert appropriately within the transaction workflow.

### Choosing the authority for creation time

Application code could generate a UTC timestamp, but different backend machines can have slightly different clocks.

For the time at which the database record was created, PostgreSQL is the chosen authority:

```sql
created_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

Meaning:

```text
TIMESTAMPTZ
  -> stores a timezone-aware point in time

NOT NULL
  -> every order has a creation time

DEFAULT now()
  -> PostgreSQL supplies the time when the application omits it
```

The timestamp can later be displayed in the user's local timezone.

This does not mean PostgreSQL must generate every possible business timestamp. A time supplied by an external event may have different semantics. Here, `created_at` specifically represents creation of the persisted order record.

### Recording later changes

The current design also includes:

```sql
updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
```

Initially, `created_at` and `updated_at` have the same value.

Important PostgreSQL behavior:

```text
DEFAULT now() runs for insertion.
It does not automatically update the column on every UPDATE.
```

When order status changes, the starter repository/update statement must explicitly do:

```sql
updated_at = now()
```

A database trigger could automate this later, but explicit repository behavior is simpler and more visible for the current learning stage.

Semantic distinction:

```text
updated_at
  -> time of any latest change to the order row

status_updated_at
  -> time of the latest status transition specifically

cancelled_at
  -> time of cancellation specifically
```

The current project uses general `updated_at` because status is presently the main mutable order field. More specific lifecycle timestamps should be introduced only when their requirement appears.

### Current derived orders table

```text
orders
----------------------------------------------
id               primary key
order_number     unique, not null
status           order_status, not null, no default
idempotency_key  unique, not null
created_at       timestamptz, not null, default now()
updated_at       timestamptz, not null, default now()
```

Every field came from a requirement:

```text
id
  -> stable relational identity

order_number
  -> unique public identity

status
  -> valid lifecycle state explicitly chosen by business logic

idempotency_key
  -> one stored order per logical request

created_at
  -> authoritative record-creation time

updated_at
  -> latest row-change time
```

Next database-design question:

```text
If an orders row is deleted, what should PostgreSQL do with its order_items rows?
```

This introduces foreign-key deletion behavior such as `CASCADE` and `RESTRICT`.

## Project 04 DB Design 04: Deletion Is Not Cancellation

The next pressure came from the foreign-key relationship:

```text
order_items.order_id -> orders.id
```

If PostgreSQL deleted an order but retained its items, those item rows would point to a parent that no longer exists:

```text
orders
  no row with id = 1

order_items
  order_id = 1
  order_id = 1
```

These would be orphaned rows.

Two foreign-key behaviors were considered:

```text
RESTRICT
  -> refuse to delete the parent while child rows exist

CASCADE
  -> delete dependent child rows automatically with the parent
```

An order item has no independent meaning after its parent order is physically removed. Therefore:

```sql
order_id BIGINT NOT NULL
    REFERENCES orders(id)
    ON DELETE CASCADE
```

### Physical deletion versus business cancellation

Physical deletion means:

```text
remove the orders row
automatically remove its order_items rows
```

Cancellation is a business state transition:

```text
retain the order
retain its order_items
change status from PLACED to CANCELLED
restore inventory
update updated_at
```

Cancelled item history must remain available to answer:

```text
What did the customer order?
Which quantities were restored?
What should customer support display?
What happened in the original transaction?
```

The parent order's `CANCELLED` status currently applies to every item. A status column on each `order_items` row would add no information under the current whole-order cancellation requirement.

Item-level status may become necessary if requirements later include:

```text
partial cancellation
partial fulfilment
individual returns
backordered items
```

Cancellation must be transactional:

```text
restore inventory
+ set order status to CANCELLED
+ set updated_at to now()
= commit all changes together
```

If any part fails, the transaction must roll back all parts.

## Project 04 DB Design 05: Historical Products Must Not Disappear

The next relationship was:

```text
order_items.product_id -> inventory_products.id
```

Using `ON DELETE CASCADE` here would be dangerous. Deleting a product could erase item rows from historical orders and corrupt their meaning.

The selected rule is restrictive deletion:

```sql
product_id BIGINT NOT NULL
    REFERENCES inventory_products(id)
    ON DELETE RESTRICT
```

Meaning:

```text
product is referenced by an old order item
-> PostgreSQL rejects physical product deletion
-> order history remains intact
```

`NO ACTION`, PostgreSQL's default behavior, can also reject the deletion through the foreign-key constraint, with timing differences for deferrable constraints. `RESTRICT` is written here to make the intended policy explicit at this learning stage.

### Quantity zero is not deletion

These states mean different things:

```text
quantity = 0
  -> product exists but is currently out of stock
  -> product may be restocked later

physical deletion
  -> product row no longer exists
```

Even if `quantity = 0`, a referenced product cannot be deleted. Quantity does not remove historical foreign-key references.

An order attempt for a zero-quantity product should produce no persistent side effects:

```text
detect insufficient stock
-> create no order
-> create no order_items
-> do not reduce inventory
```

### Stock availability versus business sellability

Another distinction became visible:

```text
quantity
  -> how many physical units are available

is_active
  -> whether the business currently permits this product to be sold
```

Examples:

```text
active + quantity 0
  -> temporarily out of stock, but may be restocked

inactive + quantity 10
  -> stock physically exists, but the product is discontinued or disabled
```

The inventory-product design therefore gains:

```sql
is_active BOOLEAN NOT NULL DEFAULT true
```

The default makes newly created products sellable unless explicitly disabled. The `NOT NULL` constraint avoids an unclear third state where activity is unknown.

New order placement must satisfy both business conditions:

```text
product is active
requested quantity is available
```

The row remains stored when inactive, so historical order relationships stay valid.

## Project 04 DB Design: Current Table Revision Sheet

### `inventory_products`

```text
id            primary key
sku           unique, not null
product_name  not null
category      nullable
quantity      not null, check quantity >= 0
is_active     boolean, not null, default true
```

Responsibilities:

```text
identify a stocked product
preserve product information
record current available stock
record whether new sales are allowed
```

### `orders`

```text
id               primary key
order_number     unique, not null
status           order_status, not null, no default
idempotency_key  unique, not null
created_at       timestamptz, not null, default now()
updated_at       timestamptz, not null, default now()
```

Responsibilities:

```text
identify the order internally and publicly
record its lifecycle state
protect one order per logical request
record creation and latest-update times
```

### `order_items`

```text
id          primary key
order_id    not null, foreign key -> orders.id, on delete cascade
product_id  not null, foreign key -> inventory_products.id, on delete restrict
quantity    not null, check quantity > 0
unique      (order_id, product_id)
```

Responsibilities:

```text
connect one order to one product
record the quantity requested in that order
preserve relational integrity
```

Relationship summary:

```text
orders             one -> many order_items
inventory_products one -> many order_items

orders and inventory_products are many-to-many through order_items
```

Deletion and lifecycle summary:

```text
physically delete order
  -> cascade-delete its order_items

cancel order
  -> retain order and items, restore inventory transactionally

delete historically referenced product
  -> reject deletion

disable product
  -> retain row and history, reject new sales
```

Next topic:

```text
Derive indexes from actual lookup and query paths.
```

## Project 04 DB Design 06: Index Fundamentals And B-Trees

An index is an additional database structure that helps PostgreSQL locate rows without examining every row in the table.

Without an index, a lookup may require a sequential scan:

```text
check row 1
check row 2
check row 3
...
```

The work grows with the number of rows.

An index is similar to a book index:

```text
Idempotency -> page 184
Repository  -> page 91
Transaction -> page 143
```

The reader searches the organized index and follows its reference instead of reading the entire book.

PostgreSQL's default general-purpose index type is called a B-tree. It is related to an ordered binary search tree but is not binary.

```text
Binary search tree
  -> one key per node in the simple model
  -> at most two children

B-tree
  -> many keys per node/page
  -> many children
  -> balanced and shallow
```

Databases favor this wide structure because reading another storage page is relatively expensive. Comparing many keys already loaded in one page is generally cheaper than traversing many separate pages.

B-tree ordering supports operations such as:

```sql
WHERE sku = 'IPHONE-15'
WHERE created_at >= some_time
WHERE price BETWEEN 100 AND 500
ORDER BY created_at
```

### Index tradeoff

Indexes are not free.

They consume:

```text
disk space
memory when cached
maintenance during INSERT
maintenance during UPDATE
maintenance during DELETE
```

An index should be justified by an actual query, join, sort, or uniqueness rule. It should not be added merely because a column exists.

Useful questions are:

```text
Which queries run frequently?
Which columns appear in WHERE?
Which columns participate in JOIN?
Which columns are used for sorting?
Which uniqueness rule must PostgreSQL enforce?
Does an existing index already cover the lookup?
```

PostgreSQL automatically creates an index for:

```text
PRIMARY KEY constraints
UNIQUE constraints
```

It does not automatically create an index on the referencing column for every foreign key. For example, `orders.id` is indexed as the referenced primary key, but that alone does not index `order_items.order_id`.

## Project 04 DB Design 07: Composite Unique Constraint And Query Execution

The current order-item rule is:

```text
Within one order, one product should appear in one row
with its total requested quantity.
```

Instead of storing:

```text
order_id   product_id   quantity
101        42           2
101        42           3
```

the application should combine the quantity:

```text
order_id   product_id   quantity
101        42           5
```

PostgreSQL protects this with:

```sql
UNIQUE (order_id, product_id)
```

This does not make each column independently unique.

Allowed combinations:

```text
(101, 42)
(101, 81)
(102, 42)
```

Rejected combination:

```text
(101, 42)
(101, 42)
```

The same order can contain different products, and the same product can belong to different orders. Only the combined pair must not repeat.

### Precise key terminology

The current design uses:

```text
id
  -> single-column primary key

UNIQUE(order_id, product_id)
  -> composite unique constraint
```

A composite constraint or index contains more than one column.

This pair is not the table's primary key because `id` remains the primary key. PostgreSQL creates one composite unique index on `(order_id, product_id)` to enforce the additional uniqueness rule.

It does not automatically create both of these independent indexes:

```text
(order_id)
(product_id)
```

### Leftmost-column behavior

The composite index is organized first by `order_id` and then by `product_id`:

```text
order_id   product_id
101        10
101        42
101        81
102        42
103        81
```

It can efficiently support:

```sql
WHERE order_id = 101
```

and:

```sql
WHERE order_id = 101
  AND product_id = 42
```

Because all entries for an `order_id` are grouped together, the composite unique index already supports loading an order's items. A duplicate standalone `order_items(order_id)` index is not currently needed.

The same index is not generally efficient for this lookup:

```sql
WHERE product_id = 42
```

because `product_id` is not the leftmost column and its values are scattered across different order groups.

### How the quantity query runs

Example query:

```sql
SELECT quantity
FROM order_items
WHERE order_id = 101
  AND product_id = 42;
```

Simplified PostgreSQL flow:

```text
1. Parse and validate the SQL.
2. Plan possible execution strategies.
3. Compare estimated sequential-scan and index-scan costs.
4. If selected, search the composite B-tree for (101, 42).
5. Obtain the stored reference to the matching table tuple.
6. Read quantity from the actual table row.
7. Return the value.
```

The index conceptually holds:

```text
(order_id, product_id) -> table-row location
```

It does not currently hold `quantity`. Therefore, a normal index scan locates the row through the index and then reads the requested quantity from the table heap.

A covering index could include the value:

```sql
CREATE INDEX some_index
ON order_items(order_id, product_id)
INCLUDE (quantity);
```

This can sometimes support an index-only scan, subject to PostgreSQL visibility rules. It is not part of the current design because extra index data adds storage and write cost, and no performance evidence currently justifies it.

PostgreSQL is also not forced to use an available index. For a tiny table, the planner may determine that scanning a few rows costs less than traversing the index. `EXPLAIN` shows the chosen plan:

```sql
EXPLAIN
SELECT quantity
FROM order_items
WHERE order_id = 101
  AND product_id = 42;
```

Key takeaway:

```text
UNIQUE(order_id, product_id)
  -> protects one product line per order
  -> creates one composite unique index
  -> supports order_id-only and order_id-plus-product_id lookups
  -> locates the row from which quantity can be read
```

Next index pressure:

```text
Do we need to find all historical order items for one product?
If yes, the product_id-only lookup may need its own index.
```

## Project 04 DB Design 08: Non-Unique Product Lookup And Selectivity

The existing composite unique index is organized as:

```text
(order_id, product_id)
```

It supports queries beginning with `order_id`, but it is not generally efficient for:

```sql
SELECT *
FROM order_items
WHERE product_id = 42;
```

`product_id` values are scattered across different `order_id` groups because it is the second index column.

Product-based queries are realistic requirements:

```text
Which orders contained this product?
How many units of this product have been ordered?
Is this product referenced by historical orders?
Which customers purchased this product once customers exist?
```

The design therefore adds an independent ordinary index:

```sql
CREATE INDEX idx_order_items_product_id
ON order_items(product_id);
```

This index is not unique. The same product is expected to appear in many order-item rows.

Important distinction:

```text
inventory_products.id
  -> uniquely identifies one product

order_items.product_id
  -> repeats as a foreign-key reference across many orders

INDEX(product_id)
  -> makes matching references easier to locate
  -> does not make the values unique
```

Conceptual index entries:

```text
product_id   table-row location
42           row A
42           row C
42           row F
81           row B
```

For `product_id = 42`, PostgreSQL can navigate the B-tree to the beginning of the `42` group and then read the matching entries.

Conceptual cost:

```text
O(log n) to locate the beginning
+ O(k) to process k matching entries
= O(log n + k)
```

It avoids a linear scan of all `n` rows, but it must still process all `k` rows requested by the query.

### Selectivity

Selectivity describes how narrowly a condition filters the table.

```text
High selectivity
  -> matches relatively few rows
  -> an index is often valuable

Low selectivity
  -> matches a large percentage of rows
  -> a sequential scan may be cheaper
```

Example:

```text
1,000,000 total order-item rows
100 reference product 42
-> index is likely useful

1,000,000 total order-item rows
800,000 reference product 42
-> PostgreSQL may prefer a sequential scan
```

The query planner chooses based on estimated cost; creating an index does not force every query to use it.

## Project 04 DB Design 09: Recent Orders And Deterministic Ordering

A realistic admin dashboard or order-history query is:

```sql
SELECT *
FROM orders
ORDER BY created_at DESC
LIMIT 20;
```

An index on creation time lets PostgreSQL begin near the newest end of the B-tree and stop after obtaining the requested rows. A B-tree created with normal ascending order can generally be scanned backward for descending results.

However, multiple orders can have the same `created_at`. Ordering only by time does not give those tied rows a deterministic relative order.

The query therefore uses internal `id` as a stable tie-breaker:

```sql
SELECT *
FROM orders
ORDER BY created_at DESC, id DESC
LIMIT 20;
```

Matching index:

```sql
CREATE INDEX idx_orders_created_at_id
ON orders(created_at, id);
```

This provides:

```text
created_at
  -> primary chronological ordering

id
  -> deterministic ordering among identical timestamps
```

The shape is also suitable groundwork for cursor-based pagination later.

Because the composite index begins with `created_at`, a separate overlapping `orders(created_at)` index is not currently added.

## Project 04 DB Design: Current Index Revision Sheet

Indexes automatically created by constraints:

```text
inventory_products.id
  -> primary-key index

inventory_products.sku
  -> unique index

orders.id
  -> primary-key index

orders.order_number
  -> unique index

orders.idempotency_key
  -> unique index

order_items.id
  -> primary-key index

order_items(order_id, product_id)
  -> composite unique index
```

Explicit ordinary indexes derived from query requirements:

```text
order_items.product_id
  -> find historical order items for one product

orders(created_at, id)
  -> list recent orders with deterministic ordering
```

Important coverage detail:

```text
UNIQUE(order_id, product_id)
  -> already supports WHERE order_id = ...
  -> no duplicate standalone order_items(order_id) index needed currently
```

Index-design rule learned:

```text
Start from a real query or constraint.
Check whether an existing index already supports it.
Add the smallest useful index.
Avoid overlapping indexes without measured need.
Remember that reads become faster at the cost of storage and write maintenance.
```

Next database-design topic:

```text
Define the PostgreSQL transaction boundary for order placement
and protect the final inventory units from concurrent buyers.
```
