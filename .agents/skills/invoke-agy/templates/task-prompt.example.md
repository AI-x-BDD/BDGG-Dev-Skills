# Role & Goal
You are Antigravity (AGY), acting as an automated coding assistant.
Your goal is to implement a new notification service module with email provider support and unit tests.

# Working Directory & Context
- Working Directory: /home/kevin/Desktop/Projects/learn/BDGG-Dev-Skills
- Task Background: The system needs an event-driven notification component to notify users upon order confirmation.

# Target Files
- Files to modify:
  - src/notifications/notifier.py
  - src/notifications/email_provider.py
  - tests/test_notifier.py
- Reference files:
  - docs/event_specs.md
  - src/orders/order_events.py

# Constraints & Boundaries
- Only modify the target files listed above. Do not touch unrelated files.
- Implement the NotifierInterface and ensure async send methods handle connection errors gracefully.
- Do not run interactive commands or launch long-running daemon servers.
- Keep all existing comments, docstrings, and formatting intact unless requested otherwise.

# Expected Deliverables & Verification
- Deliverables:
  - Implemented EmailProvider class and updated Notifier with unit tests.
- Verification criteria:
  - All unit tests in tests/test_notifier.py pass with 100% test coverage.
