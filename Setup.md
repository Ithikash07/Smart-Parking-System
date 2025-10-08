🧱 Database Schema

Tables:
	•	spots(spot_id, level, number, status, lot_id)
	•	tickets(ticket_id, spot_id, license_plate, in_time, out_time, amount, lot_id)

Supports multiple parking lots and vehicle types.

🧰 Setup Instructions
	1.	Clone Repository
  git clone https://github.com/<your-username>/smart-parking-system.git
cd smart-parking-system
  2.	Install Dependencies
  3.	Setup MySQL Database
	    •	Create a database:
       CREATE DATABASE parking_system;

  4.	Start Redis Server
  5.	Run Application
	6.	Test using Postman
	•	Base URL: http://127.0.0.1:5000
	•	Try /enter, /exit, /reserve, etc.

🧪 API Endpoints

<img width="1658" height="882" alt="image" src="https://github.com/user-attachments/assets/d17b491d-d722-4a80-8da5-5f81e6227e97" />

