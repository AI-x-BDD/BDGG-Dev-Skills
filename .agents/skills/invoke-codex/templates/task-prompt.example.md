# Role & Goal
You are Codex, acting as an automated coding agent.
Your goal is to refactor OrderService to extract tax calculation into a dedicated TaxCalculator class and write unit tests.

# Working Directory & Context
- Working Directory: /home/kevin/Desktop/Projects/learn/BDGG-Dev-Skills
- Task Background: OrderService is currently handling both order creation and tax logic, violating Single Responsibility Principle.

# Target Files
- Files to modify:
  - src/services/order_service.py
  - src/services/tax_calculator.py
  - tests/test_tax_calculator.py
- Reference files:
  - docs/architecture.md
  - tests/test_order_service.py

# Constraints & Boundaries
- Only modify the target files listed above. Do not touch unrelated files.
- TaxCalculator must implement the TaxCalculatorInterface and handle VAT rates correctly.
- Do not run interactive commands or launch long-running daemon servers.
- Keep all existing comments, docstrings, and formatting intact unless requested otherwise.

# Expected Deliverables & Verification
- Deliverables:
  - Extracted TaxCalculator class and updated OrderService using dependency injection.
- Verification criteria:
  - All tests in tests/test_tax_calculator.py and tests/test_order_service.py pass with 100% coverage.
