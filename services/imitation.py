import requests
import time
import random

URL = "http://localhost/api/predict"

DISTRICTS = [
    "Рязанский район", "Хамовники", "Якиманка", "Тверской",
    "Люблино", "Марьино", "Арбат", "Пресненский", "Таганский"
]

TEST_DURATION_SECONDS = 15 * 60  # 15 minutes
ERROR_RATE = 0.2  # 20% of requests will be broken


def generate_valid_request(user_num):
    total_area = round(random.uniform(20.0, 150.0), 1)
    living_area = round(total_area * random.uniform(0.4, 0.7), 1)
    remaining = max(total_area - living_area, 0.1)
    kitchen_area = round(min(remaining * 0.8, random.uniform(5.0, 20.0)), 1)

    floors_total = random.randint(5, 40)
    floor = random.randint(1, floors_total)

    return {
        "user_id": f"LoadTest_User_{user_num}",
        "model_params": {
            "build_year": random.randint(1950, 2023),
            "building_type_int": random.randint(0, 6),
            "ceiling_height": round(random.uniform(2.5, 4.0), 2),
            "flats_count": random.randint(20, 500),
            "floors_total": floors_total,
            "has_elevator": random.choice([0, 1]),
            "floor": floor,
            "is_apartment": random.choice([0, 1]),
            "kitchen_area": kitchen_area,
            "living_area": living_area,
            "rooms": random.randint(1, 5),
            "total_area": total_area,
            "district": random.choice(DISTRICTS)
        }
    }


def generate_broken_request(user_num):
    """Intentionally broken payload"""
    broken_type = random.choice([
        "missing_field",
        "wrong_type",
        "invalid_value"
    ])

    base = generate_valid_request(user_num)

    if broken_type == "missing_field":
        # Remove mandatory field
        base["model_params"].pop("total_area", None)

    elif broken_type == "wrong_type":
        # Wrong type
        base["model_params"]["floor"] = "nine"

    elif broken_type == "invalid_value":
        # Invalid value
        base["model_params"]["ceiling_height"] = -1.0

    return base, broken_type


print(f"Starting load on {URL}")
print("15 minutes, ~20% errors\n")

start_time = time.time()
request_count = 0

while time.time() - start_time < TEST_DURATION_SECONDS:
    request_count += 1

    if random.random() < ERROR_RATE:
        data, error_type = generate_broken_request(request_count)
        label = f"BROKEN ({error_type})"
    else:
        data = generate_valid_request(request_count)
        label = "OK"

    try:
        t0 = time.time()
        response = requests.post(URL, json=data)
        dt = time.time() - t0

        print(
            f"#{request_count} {label} | "
            f"status={response.status_code} | "
            f"{dt:.3f}s"
        )

    except Exception as e:
        print(f"#{request_count} ERROR | {e}")

    time.sleep(random.uniform(0.3, 1.2))

print("\nLoad test completed")