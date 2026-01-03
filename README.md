# 📦 Inventory Management System (Real-time)

Industry-standard Inventory Management Solution built with **Django**, focusing on real-time stock monitoring and automated sales workflows.

---

## 🚀 Key Highlights (Industry Level)
- **Real-time Monitoring:** Integrated **WebSockets (Django Channels)** for instant low-stock alerts without page refresh.
- **Asynchronous Processing:** Powered by **Daphne** ASGI server for handling high-concurrency connections.
- **Signal-driven Architecture:** Automated stock deductions and notifications using **Django Signals**.
- **Data Integrity:** Strict validation for inventory levels and warehouse management.

---

## 🛠 Tech Stack
- **Backend:** Django 5.x, Django REST Framework (DRF)
- **Real-time:** Django Channels, WebSockets
- **Server:** Daphne (ASGI)
- **Database:** SQLite (Development) / PostgreSQL (Production ready)
- **Frontend:** JavaScript (Native WebSocket API), Bootstrap 5

---

## ⚡ Real-time Features
### 🔔 Low Stock Notifications
The system monitors inventory levels in real-time. When a `SalesOrder` is placed and the `Stock` falls below the `min_stock_level`:
1.  A **Django Signal** triggers.
2.  The **Channel Layer** broadcasts a message to the `inventory_alerts` group.
3.  The **WebSocket Consumer** pushes the notification to all connected dashboard clients.

---

## 🔧 Installation & Setup

1. **Clone the Repository:**
   ```bash
   git clone [https://github.com/svg-shubham/Inventory-Management-System.git](https://github.com/svg-shubham/Inventory-Management-System.git)
   cd Inventory-Management-System
Setup Virtual Environment:

Bash

python -m venv my_venv
# Windows
my_venv\Scripts\activate
Install Dependencies:

Bash

pip install -r requirements.txt
Database Migrations:

Bash

python manage.py migrate
Run the Development Server (ASGI):

Bash

daphne -p 8000 yogesh_inventory.asgi:application
Project Structure
inventory/: Core logic for stock, products, and real-time consumers.

orders/: Management of sales and purchase orders with signal triggers.

yogesh_inventory/: Project configuration and ASGI/WSGI routing.