# Smart-Parking-System

🚀 Overview

A backend-based Smart Parking Management System built using Flask, MySQL, and Redis, designed with OOP and Low-Level Design (LLD) principles.
The system manages vehicle entry, exit, availability, and spot reservations while ensuring reliability through idempotency, concurrency control, and structured backend layering.

⸻

⚙️ Features
	•	🚗 Vehicle Entry / Exit with automatic ticket creation and bill generation.
	•	🏢 Supports multiple parking lots and levels with spot tracking.
	•	🧾 Maintains spot–ticket consistency using foreign keys in MySQL.
	•	🔄 Idempotency to safely handle duplicate API requests.
	•	🔐 Concurrency control using database transactions and row-level locks.
	•	⏳ Redis-based spot reservations with auto-expiry (TTL).
	•	💰 Flexible pricing strategy using the Strategy Pattern (Per-Minute, Hourly, etc.).

🧩 Architecture Overview

Layered Design (LLD Concepts Used):
Controller (Flask APIs)
   ↓
Service Layer (Business Logic)
   ↓
Repository Layer (MySQL Operations)

🗄️ Tech Stack
	•	Backend: Python (Flask)
	•	Database: MySQL
	•	Caching / Reservation: Redis
	•	Design: OOP, LLD, REST APIs
	•	Tools: Postman, MySQL Workbench
