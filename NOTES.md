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
