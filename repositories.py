#repositories.py

import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",        
    "password": "2004@Ithikash", 
    "database": "parking_system"
}

def get_connection():
    return mysql.connector.connect(**DB_CONFIG)

'''
# Spot Repository
class SpotRepository:
    def find_free_spot(self, lot_id):
        conn = get_connection()
        c = conn.cursor(dictionary=True)
        c.execute("SELECT spot_id FROM spots WHERE status='free' AND lot_id=%s LIMIT 1", (lot_id,))
        row = c.fetchone()
        conn.close()
        return row

    def occupy_spot(self, spot_id, lot_id):
        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE spots SET status='occupied' WHERE spot_id=%s AND lot_id=%s", (spot_id, lot_id))
        conn.commit()
        conn.close()

    def free_spot(self, spot_id, lot_id):
        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE spots SET status='free' WHERE spot_id=%s AND lot_id=%s", (spot_id, lot_id))
        conn.commit()
        conn.close()

    def count_free_spots(self, lot_id):
        conn = get_connection()
        c = conn.cursor(dictionary=True)
        c.execute("""
            SELECT level, COUNT(*) as free_count 
            FROM spots 
            WHERE status='free' AND lot_id=%s 
            GROUP BY level
        """, (lot_id,))
        rows = c.fetchall()
        conn.close()
        return rows
'''

# --- repositories.py (modified parts) ---

# Spot Repository
class SpotRepository:

    def find_and_lock_free_spot(self, lot_id, vehicle_type):
        """
        Transactionally find and lock a free spot so no two clients get the same.
        """
        conn = get_connection()
        c = conn.cursor(dictionary=True)

        try:
            conn.start_transaction()

            # Lock one free spot row
            c.execute(
                "SELECT spot_id FROM spots WHERE status='free' AND lot_id=%s AND vehicle_type=%s LIMIT 1 FOR UPDATE",
                (lot_id, vehicle_type)
            )
            row = c.fetchone()

            if not row:
                conn.rollback()
                conn.close()
                return None

            # Mark spot occupied immediately inside transaction
            c.execute(
                "UPDATE spots SET status='occupied' WHERE spot_id=%s AND lot_id=%s",
                (row["spot_id"], lot_id)
            )

            conn.commit()
            conn.close()
            return row

        except Exception as e:
            conn.rollback()
            conn.close()
            raise e
    

    def occupy_spot(self, spot_id, lot_id):
        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE spots SET status='occupied' WHERE spot_id=%s AND lot_id=%s", (spot_id, lot_id))
        conn.commit()
        conn.close()

    def free_spot(self, spot_id, lot_id):
        conn = get_connection()
        c = conn.cursor()
        c.execute("UPDATE spots SET status='free' WHERE spot_id=%s AND lot_id=%s", (spot_id, lot_id))
        conn.commit()
        conn.close()

    def count_free_spots(self, lot_id):
        """
        Returns rows grouped by level and vehicle_type:
        [{ 'level':1, 'vehicle_type':'bike', 'free_count':2 }, ...]
        """
        conn = get_connection()
        c = conn.cursor(dictionary=True)
        c.execute("""
            SELECT level, vehicle_type, COUNT(*) as free_count
            FROM spots
            WHERE status='free' AND lot_id=%s
            GROUP BY level, vehicle_type
            ORDER BY level, vehicle_type
        """, (lot_id,))
        rows = c.fetchall()
        conn.close()
        return rows


# Ticket Repository
class TicketRepository:
    def create_ticket(self, ticket_id, spot_id, license_plate, in_time, vehicle_type, lot_id):
        conn = get_connection()
        c = conn.cursor()
        c.execute(
            "INSERT INTO tickets (ticket_id, spot_id, license_plate, in_time, vehicle_type, status, lot_id) VALUES (%s, %s, %s, %s, %s, 'active', %s)",
            (ticket_id, spot_id, license_plate, in_time, vehicle_type, lot_id)
        )
        conn.commit()
        conn.close()

    def close_ticket(self, ticket_id, out_time, amount):
        conn = get_connection()
        c = conn.cursor()
        c.execute(
            "UPDATE tickets SET out_time=%s, amount=%s, status='closed' WHERE ticket_id=%s",
            (out_time, amount, ticket_id)
        )
        conn.commit()
        conn.close()

    def find_active_ticket(self, ticket_id, lot_id):
        conn = get_connection()
        c = conn.cursor(dictionary=True)
        c.execute("SELECT * FROM tickets WHERE ticket_id=%s AND lot_id=%s AND status='active'", (ticket_id, lot_id))
        row = c.fetchone()
        conn.close()
        return row

    def find_active_ticket_by_plate(self, license_plate, lot_id):
        conn = get_connection()
        c = conn.cursor(dictionary=True)
        c.execute("SELECT * FROM tickets WHERE license_plate=%s AND lot_id=%s AND status='active'", (license_plate, lot_id))
        row = c.fetchone()
        conn.close()
        return row

class IdempotencyRepository:
    def save_response(self, key, response):
        conn = get_connection()
        c = conn.cursor()
        c.execute("INSERT INTO idempotency (idempotency_key, response_json) VALUES (%s, %s)", 
                  (key, json.dumps(response)))
        conn.commit()
        conn.close()

    def get_response(self, key):
        conn = get_connection()
        c = conn.cursor(dictionary=True)
        c.execute("SELECT response_json FROM idempotency WHERE idempotency_key=%s", (key,))
        row = c.fetchone()
        conn.close()
        if row:
            return json.loads(row["response_json"])
        return None


'''

def find_free_spot(self, lot_id, vehicle_type):
        """Return one free spot from given lot that fits the vehicle_type."""
        conn = get_connection()
        c = conn.cursor(dictionary=True)
        c.execute(
            "SELECT spot_id FROM spots WHERE status='free' AND lot_id=%s AND vehicle_type=%s LIMIT 1",
            (lot_id, vehicle_type)
        )
        row = c.fetchone()
        conn.close()
        return row
'''