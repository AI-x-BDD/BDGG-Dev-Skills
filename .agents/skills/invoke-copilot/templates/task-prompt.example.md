# Role & Goal
You are GitHub Copilot CLI, acting as an automated coding assistant.
Your goal is to fix the edge-case discount calculation bug in checkout service and add regression tests.

# Working Directory & Context
- Working Directory: /home/kevin/Desktop/Projects/learn/BDGG-Dev-Skills
- Task Background: When cart total is equal to discount threshold, a zero-division error occurs during checkout.

# Target Files
- Files to modify:
  - src/checkout/discount_calculator.py
  - tests/test_discount_calculator.py
- Reference files:
  - docs/discount_policy.md
  - src/checkout/checkout_service.py

# Constraints & Boundaries
- Only modify the target files listed above. Do not touch unrelated files.
- Ensure all currency values remain formatted as decimal with two decimal places.
- Do not run interactive commands or launch long-running daemon servers.
- Keep all existing comments, docstrings, and formatting intact unless requested otherwise.

# Expected Deliverables & Verification
- Deliverables:
  - Fixed boundary check in discount calculator and added unit tests for boundary scenarios.
- Verification criteria:
  - All tests in tests/test_discount_calculator.py pass without errors.
