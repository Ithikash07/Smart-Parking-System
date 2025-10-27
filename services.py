import time
import uuid
from datetime import datetime
from repositories import SpotRepository, TicketRepository, IdempotencyRepository
from pricing import PerMinute, FlatRate, HourlyRate

# Instantiate repositories
spot_repo = SpotRepository()
ticket_repo = TicketRepository()
idempotency_repo = IdempotencyRepository()

# Pricing strategy(Strategy pattern)
pricing_strategy = PerMinute()

def format_time(ts: int) -> str:
    """Convert Unix timestamp -> human-readable string"""
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S")

# --- services.py (modified parts) ---


# services.py
class ParkingService:
    def enter(self, license_plate, lot_id, vehicle_type="car", idem_key=None):
        # Step 1: Idempotency check
        if idem_key:
            cached = idempotency_repo.get_response(idem_key)
            if cached:
                return cached, None

        # Step 2: Prevent duplicate active ticket
        existing_ticket = ticket_repo.find_active_ticket_by_plate(license_plate, lot_id)
        if existing_ticket:
            response = {
                "ticket_id": existing_ticket["ticket_id"],
                "spot_id": existing_ticket["spot_id"],
                "lot_id": existing_ticket["lot_id"],
                "license_plate": existing_ticket["license_plate"],
                "vehicle_type": existing_ticket["vehicle_type"],
                "in_time": existing_ticket["in_time"],
                "in_time_readable": format_time(existing_ticket["in_time"])
            }
            if idem_key:
                idempotency_repo.save_response(idem_key, response)
            return response, None

        # Step 3: Concurrency-safe spot allocation
        spot = spot_repo.find_and_lock_free_spot(lot_id, vehicle_type)
        if not spot:
            return None, f"No {vehicle_type} spots available in {lot_id}"

        # Step 4: Create new ticket
        ticket_id = str(uuid.uuid4())
        in_time = int(time.time())
        ticket_repo.create_ticket(ticket_id, spot["spot_id"], license_plate, in_time, vehicle_type, lot_id)

        response = {
            "ticket_id": ticket_id,
            "spot_id": spot["spot_id"],
            "lot_id": lot_id,
            "license_plate": license_plate,
            "vehicle_type": vehicle_type,
            "in_time": in_time,
            "in_time_readable": format_time(in_time)
        }

        if idem_key:
            idempotency_repo.save_response(idem_key, response)

        return response, None


    def exit(self, ticket_id, lot_id):
        # 🔹 Step 1: Find active ticket in that lot
        ticket = ticket_repo.find_active_ticket(ticket_id, lot_id)
        if not ticket:
            return None, f"Ticket not found in {lot_id} or already closed"

        # 🔹 Step 2: Free the spot
        spot_repo.free_spot(ticket["spot_id"], lot_id)

        # 🔹 Step 3: Calculate bill
        out_time = int(time.time())
        duration = out_time - ticket["in_time"]
        amount = pricing_strategy.calculate(duration)

        # 🔹 Step 4: Close ticket
        ticket_repo.close_ticket(ticket_id, out_time, amount)

        response = {
            "ticket_id": ticket_id,
            "spot_id": ticket["spot_id"],
            "lot_id": lot_id,
            "license_plate": ticket["license_plate"],
            "in_time": ticket["in_time"],
            "in_time_readable": format_time(ticket["in_time"]),
            "out_time": out_time,
            "out_time_readable": format_time(out_time),
            "amount": amount
        }

        return response, None

    def availability(self, lot_id):
        return spot_repo.count_free_spots(lot_id)

