import requests
import threading

URL = "http://127.0.0.1:5000/enter"

def book_spot(plate):
    data = {"license_plate": plate, "lot_id": "LOT1"}
    try:
        res = requests.post(URL, json=data, timeout=5)
        print(plate, res.json())
    except Exception as e:
        print(f"{plate}: Error: {e}")

threads = []
for i in range(1, 6):  # simulate 5 cars at once
    t = threading.Thread(target=book_spot, args=(f"TN10{i}CAR",))
    threads.append(t)
    t.start()

for t in threads:
    t.join()
