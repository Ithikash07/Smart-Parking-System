''' reservation_service.py
import redis
import uuid
import time

# Connect to Redis (make sure Redis is running on localhost:6379)
r = redis.Redis(host="localhost", port=6379, db=0)

class ReservationService:
    def reserve_spot(self, license_plate, lot_id, ttl=300):
        """
        Reserve a spot for 'ttl' seconds (default 5 minutes).
        Uses Redis SETNX + expiry so reservations auto-expire.
        """
        reservation_id = f"{lot_id}-RES-{uuid.uuid4().hex[:6]}"
        key = f"reservation:{reservation_id}"

        # SETNX ensures we don’t overwrite an existing reservation
        try:
            success = r.set(key, license_plate, ex=ttl, nx=True)
        
        except redis.ConnectionError:
            return None  # or return {"error": "Redis unavailable"}

        if success:
            return {
                "reservation_id": reservation_id,
                "lot_id": lot_id,
                "license_plate": license_plate,
                "expires_in_seconds": ttl
            }
        return None

    def get_reservation(self, reservation_id):
        """Check if a reservation exists (and hasn’t expired)."""
        key = f"reservation:{reservation_id}"
        license_plate = r.get(key)
        if license_plate:
            return {
                "reservation_id": reservation_id,
                "license_plate": license_plate.decode("utf-8")
            }
        return None

    def cancel_reservation(self, reservation_id):
        """Cancel a reservation before TTL expires."""
        key = f"reservation:{reservation_id}"
        return r.delete(key) > 0

'''


# reservation_service.py
import redis
import uuid
import mysql.connector
from repositories import SpotRepository, get_connection

# Connect to Redis
r = redis.Redis(host="localhost", port=6379, db=0)

spot_repo = SpotRepository()

class ReservationService:
    def reserve_spot(self, license_plate, lot_id, vehicle_type="car", ttl=300):
        """
        Reserve a spot of specific vehicle_type in given lot.
        Marks it reserved in DB + Redis, expires after ttl seconds.
        """
        # Step 1: Find free spot in DB
        spot = spot_repo.find_and_lock_free_spot(lot_id, vehicle_type)
        if not spot:
            return None  # No spot available

        spot_id = spot["spot_id"]

        # Step 2: Mark spot as reserved in DB
        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE spots SET status='reserved' WHERE spot_id=%s AND lot_id=%s", (spot_id, lot_id))
        conn.commit()
        conn.close()

        # Step 3: Store reservation in Redis (auto-expire)
        reservation_id = f"{lot_id}-RES-{uuid.uuid4().hex[:6]}"
        key = f"reservation:{reservation_id}"
        value = f"{license_plate}|{spot_id}|{vehicle_type}|{lot_id}"

        try:
            r.set(key, value, ex=ttl, nx=True)
        except redis.ConnectionError:
            return None

        return {
            "reservation_id": reservation_id,
            "lot_id": lot_id,
            "spot_id": spot_id,
            "vehicle_type": vehicle_type,
            "license_plate": license_plate,
            "expires_in_seconds": ttl
        }

    def get_reservation(self, reservation_id):
        """Check if reservation exists in Redis."""
        key = f"reservation:{reservation_id}"
        data = r.get(key)
        if data:
            license_plate, spot_id, vehicle_type, lot_id = data.decode("utf-8").split("|")
            return {
                "reservation_id": reservation_id,
                "license_plate": license_plate,
                "spot_id": spot_id,
                "vehicle_type": vehicle_type,
                "lot_id": lot_id
            }
        return None

    def cancel_reservation(self, reservation_id):
        """Cancel reservation + free DB spot."""
        key = f"reservation:{reservation_id}"
        data = r.get(key)
        if not data:
            return False

        license_plate, spot_id, vehicle_type, lot_id = data.decode("utf-8").split("|")

        # Free DB spot
        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE spots SET status='free' WHERE spot_id=%s AND lot_id=%s", (spot_id, lot_id))
        conn.commit()
        conn.close()

        # Remove from Redis
        r.delete(key)
        return True