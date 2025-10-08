
from flask import Flask, request, jsonify
from services import ParkingService
import reservation_service
import mysql.connector

app = Flask(__name__)
service = ParkingService()


DB_CONFIG = {
    "host": "localhost",
    "user": "root",
    "password": "2004@Ithikash", 
    "database": "parking_system"
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)


# --- app.py (modified enter route) ---

@app.route("/enter", methods=["POST"])
def enter():
    data = request.get_json()
    license_plate = data.get("license_plate")
    lot_id = data.get("lot_id")
    vehicle_type = data.get("vehicle_type", "car")   # default 'car'
    idem_key = request.headers.get("Idempotency-Key")

    if not license_plate or not lot_id:
        return jsonify({"error": "license_plate and lot_id required"}), 400

    result, error = service.enter(license_plate, lot_id, vehicle_type, idem_key)
    if error:
        return jsonify({"error": error}), 409

    return jsonify(result), 201

'''@app.route("/enter", methods=["POST"])
def enter():
    data = request.get_json()
    license_plate = data.get("license_plate")
    lot_id = data.get("lot_id")  
    idem_key = request.headers.get("Idempotency-Key")

    if not license_plate or not lot_id:
        return jsonify({"error": "license_plate and lot_id required"}), 400

    result, error = service.enter(license_plate, lot_id, idem_key)  
    if error:
        return jsonify({"error": error}), 409

    return jsonify(result), 201'''

@app.route("/exit", methods=["POST"])
def exit_parking():
    data = request.get_json()
    ticket_id = data.get("ticket_id")
    lot_id = data.get("lot_id")

    if not ticket_id or not lot_id:
        return jsonify({"error": "ticket_id and lot_id required"}), 400

    result, error = service.exit(ticket_id, lot_id)
    if error:
        return jsonify({"error": error}), 404

    return jsonify(result), 200

from reservation_service import ReservationService

reservation_service = ReservationService()


@app.route("/reserve", methods=["POST"])
def reserve():
    data = request.get_json()
    license_plate = data.get("license_plate")
    lot_id = data.get("lot_id")
    vehicle_type = data.get("vehicle_type", "car")
    ttl = data.get("ttl", 300)  # optional, default 5 min

    if not license_plate or not lot_id:
        return jsonify({"error": "license_plate and lot_id required"}), 400

    reservation = reservation_service.reserve_spot(license_plate, lot_id, vehicle_type, ttl)
    if not reservation:
        return jsonify({"error": "Reservation failed"}), 409

    return jsonify(reservation), 201

@app.route("/reservation/<reservation_id>", methods=["GET"])
def get_reservation(reservation_id):
    res = reservation_service.get_reservation(reservation_id)
    if not res:
        return jsonify({"error": "Reservation not found or expired"}), 404
    return jsonify(res), 200


@app.route("/reservation/<reservation_id>", methods=["DELETE"])
def cancel_reservation(reservation_id):
    success = reservation_service.cancel_reservation(reservation_id)
    if not success:
        return jsonify({"error": "Reservation not found"}), 404
    return jsonify({"message": "Reservation cancelled"}), 200

@app.route("/availability", methods=["GET"])
def availability():
    lot_id = request.args.get("lot_id")  
    if not lot_id:
        return jsonify({"error": "lot_id required"}), 400
    return jsonify(service.availability(lot_id)), 200

@app.route("/stats/revenue", methods=["GET"])
def revenue():
    conn = get_connection()
    c = conn.cursor(dictionary=True)
    c.execute("SELECT DATE(FROM_UNIXTIME(out_time)) as day, SUM(amount) as revenue FROM tickets WHERE status='closed' GROUP BY day")
    rows = c.fetchall()
    conn.close()
    return jsonify(rows), 200

if __name__ == "__main__":
    app.run(debug=True)