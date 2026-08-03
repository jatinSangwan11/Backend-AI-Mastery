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

## Working Agreement

- We prioritize projects over theory.
- Codex teaches, gives exercises, reviews code, and updates progress.
- You type substantial code for muscle memory whenever possible.
- Git will be managed like a production repo once initialized.
