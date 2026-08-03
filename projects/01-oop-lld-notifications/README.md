# Project 01: OOP + LLD Notification System

## Goal

Build a small notification system that teaches interfaces, dependency inversion, composition, and testable design.

## Requirements

- Support Email, SMS, and Slack senders.
- All senders should follow a common interface.
- `UserService` should depend on the interface, not concrete sender classes.
- `NotificationManager` should send through multiple channels.
- Adding WhatsApp later should require minimal changes.

## Design Questions

- What behavior belongs in a sender?
- Should the manager know about Email/SMS/Slack directly?
- How do we test without sending real messages?
- Should we use an abstract base class or a protocol?

## Commands

From this project folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -e ".[dev]"
pytest
```

