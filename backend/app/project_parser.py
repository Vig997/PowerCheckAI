import re


NUMBER_WORDS = {
    "a": 1,
    "an": 1,
    "one": 1,
    "two": 2,
    "three": 3,
    "four": 4,
    "five": 5,
    "six": 6,
    "seven": 7,
    "eight": 8,
    "nine": 9,
    "ten": 10,
    "twelve": 12,
    "twenty": 20,
    "thirty": 30,
    "sixty": 60,
}


MICROCONTROLLER_KEYWORDS = [
    ("esp32-cam", 5, "ESP32-CAM"),
    ("esp32 cam", 5, "ESP32-CAM"),
    ("esp32", 4, "ESP32 Dev Board"),
    ("arduino uno", 1, "Arduino Uno"),
    ("uno", 1, "Arduino Uno"),
    ("arduino nano", 2, "Arduino Nano"),
    ("nano", 2, "Arduino Nano"),
    ("arduino mega", 3, "Arduino Mega"),
    ("mega", 3, "Arduino Mega"),
    ("raspberry pi pico", 6, "Raspberry Pi Pico"),
    ("pico", 6, "Raspberry Pi Pico"),
]


COMPONENT_KEYWORDS = [
    ("ultrasonic", 7, "HC-SR04 Ultrasonic Sensor", 1),
    ("distance sensor", 7, "HC-SR04 Ultrasonic Sensor", 1),
    ("dht11", 8, "DHT11 Temperature/Humidity Sensor", 1),
    ("dht22", 9, "DHT22 Temperature/Humidity Sensor", 1),
    ("weather station", 9, "DHT22 Temperature/Humidity Sensor", 1),
    ("imu", 10, "MPU6050 IMU", 1),
    ("motion alarm", 11, "PIR Motion Sensor", 1),
    ("pir", 11, "PIR Motion Sensor", 1),
    ("soil monitor", 13, "Soil Moisture Sensor", 1),
    ("soil", 13, "Soil Moisture Sensor", 1),
    ("gas sensor", 15, "MQ-2 Gas Sensor", 1),
    ("oled", 21, "0.96 inch OLED Display", 1),
    ("lcd", 22, "16x2 LCD Display", 1),
    ("led matrix", 26, "LED Matrix 8x8", 1),
    ("rgb led", 28, "RGB LED", 1),
    ("neopixel", 30, "NeoPixel Strip", 1),
    ("led strip", 30, "NeoPixel Strip", 1),
    ("buzzer", 32, "Active Buzzer Module", 1),
    ("relay", 33, "Relay Module", 1),
    ("servo arm", 34, "SG90 Micro Servo", 4),
    ("servo", 34, "SG90 Micro Servo", 1),
    ("dc motor", 36, "Small DC Motor", 1),
    ("motor", 36, "Small DC Motor", 1),
    ("stepper", 38, "28BYJ-48 Stepper Motor", 1),
    ("pump", 40, "Mini Water Pump", 1),
    ("solenoid", 39, "Solenoid Lock", 1),
    ("rfid", 20, "RFID RC522 Module", 1),
    ("camera", 5, "ESP32-CAM", 1),
]


def _quantity_before(text: str, keyword: str, default: int) -> int:
    words = "|".join(NUMBER_WORDS)
    pattern = rf"(?:(\d+)|({words}))\s+(?:\w+\s+){{0,2}}{re.escape(keyword)}s?"
    match = re.search(pattern, text)
    if not match:
        return default
    if match.group(1):
        return int(match.group(1))
    return NUMBER_WORDS.get(match.group(2), default)


def parse_project_description(description: str) -> dict:
    text = description.lower()
    selected_microcontroller = None
    components: dict[int, dict] = {}

    for keyword, component_id, name in MICROCONTROLLER_KEYWORDS:
        if keyword in text:
            selected_microcontroller = {"component_id": component_id, "name": name, "quantity": 1}
            break

    if selected_microcontroller is None and any(word in text for word in ["robot car", "rover", "wifi", "iot"]):
        selected_microcontroller = {"component_id": 4, "name": "ESP32 Dev Board", "quantity": 1}

    if "robot car" in text or "rover" in text:
        components[36] = {"component_id": 36, "name": "Small DC Motor", "quantity": 2}
        components[43] = {"component_id": 43, "name": "TB6612FNG Motor Driver", "quantity": 1}

    for keyword, component_id, name, default_quantity in COMPONENT_KEYWORDS:
        if keyword in text:
            if selected_microcontroller and component_id == selected_microcontroller["component_id"]:
                continue
            quantity = _quantity_before(text, keyword, default_quantity)
            if component_id in components:
                components[component_id]["quantity"] = max(components[component_id]["quantity"], quantity)
            else:
                components[component_id] = {"component_id": component_id, "name": name, "quantity": quantity}

    return {
        "description": description,
        "selected_microcontroller": selected_microcontroller,
        "selected_components": list(components.values()),
    }
