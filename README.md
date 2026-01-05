Smart ERP: Real-time Inventory & Procurement System
An industry-standard Enterprise Resource Planning (ERP) solution built with Django, focusing on the full Procure-to-Pay (P2P) lifecycle, real-time stock monitoring, and automated asynchronous workflows.

 Key Highlights (Industry Level)
Real-time Monitoring: Integrated WebSockets (Django Channels) for instant low-stock alerts and procurement updates without page refresh.

Full P2P Cycle Automation: Handles everything from Purchase Requisitions (PR) and Approvals to Purchase Orders (PO) and Goods Receipt Notes (GRN).

Asynchronous Processing: Powered by Daphne ASGI server for handling high-concurrency real-time connections.

Signal-driven Architecture: Automated stock increments (via GRN) and deductions (via Sales) using Django Signals.

Data Integrity: ACID-compliant transactions ensuring strict validation for inventory levels and warehouse management.

🛠 Tech Stack
Backend: Django 5.x, Django REST Framework (DRF)

Real-time: Django Channels, WebSockets

Server: Daphne (ASGI)

Database: PostgreSQL (Production ready) / SQLite (Dev)

Testing: Automated Unit Testing for Procurement logic

 Core Workflows
1. The P2P (Procure-to-Pay) Lifecycle
The system automates the procurement journey to ensure zero manual errors:

Requisition: Automatic generation of unique PR numbers (e.g., PR-2026-0001).

Smart Approval: Role-based approval gates for Admins and Procurement Heads.

Inward Logistics: GRN (Goods Receipt Note) module that tracks partial deliveries and triggers Signals to instantly update warehouse stock levels.

2. Real-time Inventory Alerts
The system monitors inventory levels dynamically. When Stock falls below the min_stock_level:

A Django Signal is dispatched.

The Channel Layer broadcasts a message to the inventory_alerts group.

The WebSocket Consumer pushes live notifications to all connected dashboard clients.

 Quality Assurance
Reliability is the backbone of this project. The procurement module is backed by automated test cases covering PR creation, approval workflows, and data integrity.

Bash

python manage.py test procurement
Status: All Tests Passed 

🔧 Installation & Setup
Clone the Repository:

Bash

git clone https://github.com/svg-shubham/Inventory-Management-System.git
cd Inventory-Management-System
Setup Virtual Environment:

Bash

python -m venv my_venv
# Windows
my_venv\Scripts\activate
Install Dependencies & Migrate:

Bash

pip install -r requirements.txt
python manage.py migrate
Run the Development Server (ASGI):

Bash

daphne -p 8000 yogesh_inventory.asgi:application
🛠️ Project Status: Continuous Development
Note: This project is under active development. We are currently working on expanding the Order-to-Cash (O2C) module, including Customer Credit Limit validations and automated Dispatch/Delivery Challan generation. New features and architectural improvements are being pushed regularly. 