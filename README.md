**Enterprise Inventory & Financial Logistics System**
Overview
An advanced ERP-grade Backend designed to bridge the gap between physical warehouse operations and financial accounting. This system automates complex business workflows, ensuring that every stock movement is synchronized with financial ledgers in real-time.

Core Functionalities
1. Automated Financial Synchronization (Signals)
Zero-Manual Entry: Integrated Django Signals to auto-trigger Finance Transactions whenever a Purchase or Sales Order is validated.

Real-time Ledger: Dynamic balance updates for vendors and customers upon payment logging.

2. Intelligent Inventory Management
Multi-Warehouse Support: Track stock levels across different geographic locations.

Low-Stock Heuristics: Dedicated endpoints to identify and alert for products falling below critical thresholds.

Custom Stock Actions: Atomic operations for manual stock adjustments and audits.

3. Business Logic & Validation
Oversell Protection: Built-in validation prevents Sales Orders from being processed if stock is insufficient.

Data Integrity: Strict foreign key relationships and choice-field constraints ensure a clean database state.

🧪 Quality Assurance (Automated Testing)
This project follows Test-Driven Development (TDD) principles. I have implemented a comprehensive test suite using APITestCase to verify integration across all modules.

Bash

# Execute the full test suite
python manage.py test
Current Status: Ran 5 tests - OK

Tech Stack
Backend: Python, Django, Django REST Framework.

Database: SQLite (Dev), PostgreSQL (Configurable for Prod).

Architecture: Modular App structure (Inventory, Orders, Finance).

Installation
git clone https://github.com/your-username/your-repo.git

pip install -r requirements.txt

python manage.py migrate

python manage.py runserver
