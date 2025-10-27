import mysql.connector

def init_db():
    conn = mysql.connector.connect(
        host="localhost",
        user="root",         
        password="2004@Ithikash",  
        database="parking_system"
    )
    c = conn.cursor()

    c.execute("DROP TABLE IF EXISTS tickets")
    c.execute("DROP TABLE IF EXISTS spots")


    # --- db_init.py (modified parts) ---
    # Create spots table (with lot_id and vehicle_type)
    c.execute("""
        CREATE TABLE spots (
            spot_id VARCHAR(20),
            level INT,
            number INT,
            status ENUM('free','occupied','reserved') DEFAULT 'free',
            lot_id VARCHAR(20),
            vehicle_type ENUM('car','bike','truck') DEFAULT 'car',
            PRIMARY KEY (spot_id, lot_id)
        )
    """)

    # Create tickets table (with lot_id and vehicle_type)
    c.execute("""
        CREATE TABLE tickets (
            ticket_id VARCHAR(36) PRIMARY KEY,
            spot_id VARCHAR(20),
            license_plate VARCHAR(20),
            in_time BIGINT,
            out_time BIGINT NULL,
            amount DECIMAL(10,2) NULL,
            status ENUM('active','closed') DEFAULT 'active',
            lot_id VARCHAR(20),
            vehicle_type ENUM('car','bike','truck') DEFAULT 'car',
            FOREIGN KEY (spot_id, lot_id) REFERENCES spots(spot_id, lot_id)
        )
    """)

    # Insert some free spots for multiple lots, assigning a vehicle_type for each spot
    spots = []
    lots = ["LOT1", "LOT2"]   # add more lots here if needed

    for lot in lots:
        for level in range(1, 3):      # levels
            for number in range(1, 6): # spots per level
                spot_id = f"L{level}-S{number}"
                # Assign vehicle type: spots 1-2 -> bike, 3-4 -> car, 5 -> truck
                if number <= 2:
                    vtype = "bike"
                elif number <= 4:
                    vtype = "car"
                else:
                    vtype = "truck"
                spots.append((spot_id, level, number, "free", lot, vtype))

    c.executemany(
        "INSERT INTO spots (spot_id, level, number, status, lot_id, vehicle_type) VALUES (%s, %s, %s, %s, %s, %s)",
        spots
    )

    conn.commit()
    conn.close()
    print("✅ MySQL database initialized with sample spots for multiple lots.")

if __name__ == "__main__":
    init_db()


