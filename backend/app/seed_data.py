from sqlalchemy.orm import Session

from app.models import Component, ExampleProject, PowerSource, Regulator


COMPONENTS = [
    {
        "id": 1,
        "name": "Arduino Uno",
        "category": "microcontroller",
        "voltage_min": 5.0,
        "voltage_max": 5.0,
        "typical_current_mA": 50,
        "max_current_mA": 100,
        "recommended_gpio_current_mA": 20,
        "logic_voltage": 5.0,
        "gpio_safe": False,
        "requires_driver": False,
        "is_high_current": False,
        "is_logic_sensitive": True,
        "is_inductive": False,
        "notes": "5V Arduino board for beginner projects.",
        "common_warning": "Do not power motors or high-current loads directly from GPIO pins.",
        "beginner_tip": "Use GPIO pins for signals and separate power for motors, servos, and LED strips.",
    },
    {
        "id": 2,
        "name": "Arduino Nano",
        "category": "microcontroller",
        "voltage_min": 5.0,
        "voltage_max": 5.0,
        "typical_current_mA": 30,
        "max_current_mA": 100,
        "recommended_gpio_current_mA": 20,
        "logic_voltage": 5.0,
        "gpio_safe": False,
        "is_logic_sensitive": True,
        "notes": "Compact 5V Arduino board.",
        "common_warning": "GPIO pins are not power outputs for motors or servos.",
        "beginner_tip": "Keep high-current loads off the Nano 5V pin unless you know the regulator can handle it.",
    },
    {
        "id": 3,
        "name": "Arduino Mega",
        "category": "microcontroller",
        "voltage_min": 5.0,
        "voltage_max": 5.0,
        "typical_current_mA": 70,
        "max_current_mA": 200,
        "recommended_gpio_current_mA": 20,
        "logic_voltage": 5.0,
        "gpio_safe": False,
        "is_logic_sensitive": True,
        "notes": "Large 5V Arduino board with many GPIO pins.",
        "common_warning": "More pins does not mean more power capacity.",
        "beginner_tip": "Use drivers for motors and external supplies for servo banks.",
    },
    {
        "id": 4,
        "name": "ESP32 Dev Board",
        "category": "microcontroller",
        "voltage_min": 3.3,
        "voltage_max": 5.0,
        "typical_current_mA": 100,
        "max_current_mA": 500,
        "startup_current_mA": 500,
        "recommended_gpio_current_mA": 12,
        "logic_voltage": 3.3,
        "gpio_safe": False,
        "is_logic_sensitive": True,
        "notes": "3.3V logic board that is commonly powered from USB 5V.",
        "common_warning": "GPIO pins are 3.3V logic and should not drive high-current loads directly.",
        "beginner_tip": "Use level shifting or voltage dividers for 5V sensor outputs.",
    },
    {
        "id": 5,
        "name": "ESP32-CAM",
        "category": "microcontroller",
        "voltage_min": 3.3,
        "voltage_max": 5.0,
        "typical_current_mA": 180,
        "max_current_mA": 500,
        "startup_current_mA": 500,
        "recommended_gpio_current_mA": 12,
        "logic_voltage": 3.3,
        "gpio_safe": False,
        "is_logic_sensitive": True,
        "notes": "ESP32 board with camera and WiFi.",
        "common_warning": "Camera and WiFi can cause current spikes.",
        "beginner_tip": "Use a stable 5V supply with enough current for WiFi bursts.",
    },
    {
        "id": 6,
        "name": "Raspberry Pi Pico",
        "category": "microcontroller",
        "voltage_min": 3.3,
        "voltage_max": 5.0,
        "typical_current_mA": 30,
        "max_current_mA": 100,
        "recommended_gpio_current_mA": 12,
        "logic_voltage": 3.3,
        "gpio_safe": False,
        "is_logic_sensitive": True,
        "notes": "RP2040 board with 3.3V GPIO.",
        "common_warning": "GPIO is 3.3V only.",
        "beginner_tip": "Do not connect 5V sensor outputs directly to Pico GPIO.",
    },
    {"id": 7, "name": "HC-SR04 Ultrasonic Sensor", "category": "sensor", "voltage_min": 5.0, "voltage_max": 5.0, "typical_current_mA": 15, "max_current_mA": 20, "logic_voltage": 5.0, "gpio_safe": True, "requires_driver": False, "is_high_current": False, "is_logic_sensitive": True, "is_inductive": False, "notes": "Distance sensor with 5V echo output.", "common_warning": "Echo pin may output 5V, which can be unsafe for ESP32 without level shifting.", "beginner_tip": "Use a divider or level shifter before 3.3V GPIO."},
    {"id": 8, "name": "DHT11 Temperature/Humidity Sensor", "category": "sensor", "voltage_min": 3.3, "voltage_max": 5.0, "typical_current_mA": 2, "max_current_mA": 5, "logic_voltage": 3.3, "gpio_safe": True, "requires_driver": False, "is_high_current": False, "is_logic_sensitive": False, "is_inductive": False, "notes": "Basic humidity and temperature sensor.", "common_warning": "Slow update rate.", "beginner_tip": "Good for low-current projects."},
    {"id": 9, "name": "DHT22 Temperature/Humidity Sensor", "category": "sensor", "voltage_min": 3.3, "voltage_max": 5.0, "typical_current_mA": 2, "max_current_mA": 5, "logic_voltage": 3.3, "gpio_safe": True, "requires_driver": False, "is_high_current": False, "is_logic_sensitive": False, "is_inductive": False, "notes": "More accurate humidity and temperature sensor.", "common_warning": "Needs a pull-up resistor on many modules.", "beginner_tip": "Safe for Arduino and ESP32 when wired correctly."},
    {"id": 10, "name": "MPU6050 IMU", "category": "sensor", "voltage_min": 3.3, "voltage_max": 3.3, "typical_current_mA": 4, "max_current_mA": 10, "logic_voltage": 3.3, "gpio_safe": True, "requires_driver": False, "is_high_current": False, "is_logic_sensitive": True, "is_inductive": False, "notes": "3.3V accelerometer and gyro.", "common_warning": "Some breakout boards tolerate 5V input, but the chip itself is 3.3V.", "beginner_tip": "Check your module before powering from 5V."},
    {"id": 11, "name": "PIR Motion Sensor", "category": "sensor", "voltage_min": 5.0, "voltage_max": 5.0, "typical_current_mA": 50, "max_current_mA": 65, "logic_voltage": 3.3, "gpio_safe": True, "requires_driver": False, "is_high_current": False, "is_logic_sensitive": False, "is_inductive": False, "notes": "Motion detector module.", "common_warning": "Needs stable power during warm-up.", "beginner_tip": "Usually okay from a 5V rail."},
    {"id": 12, "name": "Photoresistor Module", "category": "sensor", "voltage_min": 3.3, "voltage_max": 5.0, "typical_current_mA": 1, "max_current_mA": 5, "logic_voltage": 3.3, "gpio_safe": True, "requires_driver": False, "is_high_current": False, "is_logic_sensitive": False, "is_inductive": False, "notes": "Simple light sensor module.", "common_warning": "Analog output range follows supply voltage.", "beginner_tip": "When using ESP32, power it from 3.3V for safer analog readings."},
    {"id": 13, "name": "Soil Moisture Sensor", "category": "sensor", "voltage_min": 3.3, "voltage_max": 5.0, "typical_current_mA": 20, "max_current_mA": 35, "logic_voltage": 3.3, "gpio_safe": True, "requires_driver": False, "is_high_current": False, "is_logic_sensitive": False, "is_inductive": False, "notes": "Moisture probe module.", "common_warning": "Powered probes can corrode over time.", "beginner_tip": "Power only while measuring to reduce corrosion."},
    {"id": 14, "name": "IR Obstacle Sensor", "category": "sensor", "voltage_min": 3.3, "voltage_max": 5.0, "typical_current_mA": 20, "max_current_mA": 40, "logic_voltage": 3.3, "gpio_safe": True, "requires_driver": False, "is_high_current": False, "is_logic_sensitive": False, "is_inductive": False, "notes": "Short-range obstacle detector.", "common_warning": "Output voltage may follow module supply.", "beginner_tip": "Use 3.3V power when connected to ESP32 GPIO."},
    {"id": 15, "name": "MQ-2 Gas Sensor", "category": "sensor", "voltage_min": 5.0, "voltage_max": 5.0, "typical_current_mA": 150, "max_current_mA": 200, "logic_voltage": 5.0, "gpio_safe": True, "requires_driver": False, "is_high_current": True, "is_logic_sensitive": True, "is_inductive": False, "notes": "Gas sensor with heater.", "common_warning": "Heater draws significant current.", "beginner_tip": "Budget current for the heater and level shift analog output for ESP32 if needed."},
    {"id": 16, "name": "BMP280 Pressure Sensor", "category": "sensor", "voltage_min": 3.3, "voltage_max": 3.3, "typical_current_mA": 1, "max_current_mA": 5, "logic_voltage": 3.3, "gpio_safe": True, "requires_driver": False, "is_high_current": False, "is_logic_sensitive": True, "is_inductive": False, "notes": "3.3V pressure sensor.", "common_warning": "Some modules include regulators, some do not.", "beginner_tip": "Check breakout board labeling before using 5V."},
    {"id": 17, "name": "DS18B20 Temperature Sensor", "category": "sensor", "voltage_min": 3.3, "voltage_max": 5.0, "typical_current_mA": 1, "max_current_mA": 5, "logic_voltage": 3.3, "gpio_safe": True, "requires_driver": False, "is_high_current": False, "is_logic_sensitive": False, "is_inductive": False, "notes": "1-wire digital temperature sensor.", "common_warning": "Needs a pull-up resistor.", "beginner_tip": "Very low-current sensor."},
    {"id": 18, "name": "TCS34725 Color Sensor", "category": "sensor", "voltage_min": 3.3, "voltage_max": 5.0, "typical_current_mA": 5, "max_current_mA": 20, "logic_voltage": 3.3, "gpio_safe": True, "requires_driver": False, "is_high_current": False, "is_logic_sensitive": False, "is_inductive": False, "notes": "Color sensor module.", "common_warning": "Onboard LED increases current slightly.", "beginner_tip": "Most breakout boards are easy to use with I2C."},
    {"id": 19, "name": "GPS Module NEO-6M", "category": "sensor", "voltage_min": 3.3, "voltage_max": 5.0, "typical_current_mA": 45, "max_current_mA": 70, "logic_voltage": 3.3, "gpio_safe": True, "requires_driver": False, "is_high_current": False, "is_logic_sensitive": True, "is_inductive": False, "notes": "GPS receiver module.", "common_warning": "Serial logic may be 3.3V.", "beginner_tip": "Give it a clear sky view and stable supply."},
    {"id": 20, "name": "RFID RC522 Module", "category": "sensor", "voltage_min": 3.3, "voltage_max": 3.3, "typical_current_mA": 13, "max_current_mA": 30, "logic_voltage": 3.3, "gpio_safe": True, "requires_driver": False, "is_high_current": False, "is_logic_sensitive": True, "is_inductive": False, "notes": "3.3V RFID reader.", "common_warning": "3.3V logic; be careful with 5V boards.", "beginner_tip": "Use level shifting when connecting to 5V Arduino boards."},
    {"id": 21, "name": "0.96 inch OLED Display", "category": "display", "voltage_min": 3.3, "voltage_max": 5.0, "typical_current_mA": 20, "max_current_mA": 40, "logic_voltage": 3.3, "gpio_safe": True, "requires_driver": False, "is_high_current": False, "is_logic_sensitive": False, "is_inductive": False, "notes": "Small I2C OLED display.", "common_warning": "Bright screens draw more current.", "beginner_tip": "A good display choice for battery projects."},
    {"id": 22, "name": "16x2 LCD Display", "category": "display", "voltage_min": 5.0, "voltage_max": 5.0, "typical_current_mA": 2, "max_current_mA": 120, "logic_voltage": 5.0, "gpio_safe": True, "requires_driver": False, "is_high_current": False, "is_logic_sensitive": True, "is_inductive": False, "notes": "Classic character LCD.", "common_warning": "Backlight can dominate current draw.", "beginner_tip": "Include backlight current in your power budget."},
    {"id": 23, "name": "I2C LCD Backpack", "category": "display", "voltage_min": 5.0, "voltage_max": 5.0, "typical_current_mA": 20, "max_current_mA": 50, "logic_voltage": 5.0, "gpio_safe": True, "requires_driver": False, "is_high_current": False, "is_logic_sensitive": True, "is_inductive": False, "notes": "I2C adapter for LCDs.", "common_warning": "I2C pull-ups may be tied to 5V.", "beginner_tip": "Watch I2C voltage when using ESP32."},
    {"id": 24, "name": "7-Segment Display", "category": "display", "voltage_min": 5.0, "voltage_max": 5.0, "typical_current_mA": 40, "max_current_mA": 160, "logic_voltage": 5.0, "gpio_safe": False, "requires_driver": False, "is_high_current": True, "is_logic_sensitive": False, "is_inductive": False, "notes": "LED numeric display.", "common_warning": "Multiplexed LED displays can draw more current than expected.", "beginner_tip": "Use resistors or a driver module."},
    {"id": 25, "name": "Small TFT Display", "category": "display", "voltage_min": 3.3, "voltage_max": 5.0, "typical_current_mA": 80, "max_current_mA": 150, "logic_voltage": 3.3, "gpio_safe": True, "requires_driver": False, "is_high_current": False, "is_logic_sensitive": True, "is_inductive": False, "notes": "Small color display.", "common_warning": "Backlight current can be significant.", "beginner_tip": "Confirm whether the module accepts 5V logic."},
    {"id": 26, "name": "LED Matrix 8x8", "category": "display", "voltage_min": 5.0, "voltage_max": 5.0, "typical_current_mA": 100, "max_current_mA": 500, "logic_voltage": 5.0, "gpio_safe": False, "requires_driver": False, "is_high_current": True, "is_logic_sensitive": False, "is_inductive": False, "notes": "Matrix LED module.", "common_warning": "Current can be high when many LEDs are on.", "beginner_tip": "Use external 5V power for multiple modules."},
    {"id": 27, "name": "Standard LED", "category": "led", "voltage_min": 2.0, "voltage_max": 5.0, "typical_current_mA": 10, "max_current_mA": 20, "logic_voltage": None, "gpio_safe": True, "requires_driver": False, "is_high_current": False, "is_logic_sensitive": False, "is_inductive": False, "notes": "Use a current-limiting resistor.", "common_warning": "An LED without a resistor can damage a GPIO pin.", "beginner_tip": "Start with 220 ohm or 330 ohm resistors for 5V Arduino projects."},
    {"id": 28, "name": "RGB LED", "category": "led", "voltage_min": 2.0, "voltage_max": 3.3, "typical_current_mA": 20, "max_current_mA": 60, "logic_voltage": None, "gpio_safe": False, "requires_driver": False, "is_high_current": True, "is_logic_sensitive": False, "is_inductive": False, "notes": "Use resistors for each color channel.", "common_warning": "All three colors on can exceed a single GPIO current limit.", "beginner_tip": "Drive each color through its own resistor."},
    {"id": 29, "name": "NeoPixel WS2812B Single LED", "category": "led", "voltage_min": 5.0, "voltage_max": 5.0, "typical_current_mA": 20, "max_current_mA": 60, "logic_voltage": 5.0, "gpio_safe": False, "requires_driver": False, "is_high_current": False, "is_logic_sensitive": True, "is_inductive": False, "notes": "Addressable RGB LED.", "common_warning": "Power should not come from GPIO.", "beginner_tip": "Use a data resistor and common ground."},
    {"id": 30, "name": "NeoPixel Strip", "category": "led", "voltage_min": 5.0, "voltage_max": 5.0, "typical_current_mA": 20, "max_current_mA": 60, "logic_voltage": 5.0, "gpio_safe": False, "requires_driver": False, "is_high_current": True, "is_logic_sensitive": True, "is_inductive": False, "notes": "Current values are per LED.", "common_warning": "High current draw; use external 5V supply for larger strips.", "beginner_tip": "Use a large capacitor near the strip and connect grounds together."},
    {"id": 31, "name": "Buzzer", "category": "load", "voltage_min": 3.3, "voltage_max": 5.0, "typical_current_mA": 20, "max_current_mA": 40, "logic_voltage": None, "gpio_safe": False, "requires_driver": False, "is_high_current": True, "is_logic_sensitive": False, "is_inductive": False, "notes": "Small sound output.", "common_warning": "Some buzzers exceed GPIO current limits.", "beginner_tip": "Use a transistor driver for louder buzzers."},
    {"id": 32, "name": "Active Buzzer Module", "category": "load", "voltage_min": 3.3, "voltage_max": 5.0, "typical_current_mA": 30, "max_current_mA": 50, "logic_voltage": 3.3, "gpio_safe": False, "requires_driver": False, "is_high_current": True, "is_logic_sensitive": False, "is_inductive": False, "notes": "Buzzer module with drive electronics.", "common_warning": "Can draw more than a GPIO pin should source.", "beginner_tip": "Power from VCC and drive the signal pin only."},
    {"id": 33, "name": "Relay Module", "category": "load", "voltage_min": 5.0, "voltage_max": 5.0, "typical_current_mA": 70, "max_current_mA": 90, "logic_voltage": 5.0, "gpio_safe": False, "requires_driver": True, "is_high_current": True, "is_logic_sensitive": False, "is_inductive": True, "notes": "Relay coils should not be powered directly from GPIO.", "common_warning": "Relay coils need driver protection.", "beginner_tip": "Use relay modules with built-in drivers and separate coil power when needed."},
    {"id": 34, "name": "SG90 Micro Servo", "category": "servo", "voltage_min": 5.0, "voltage_max": 5.0, "typical_current_mA": 250, "max_current_mA": 500, "stall_current_mA": 700, "logic_voltage": 5.0, "gpio_safe": False, "requires_driver": False, "is_high_current": True, "is_logic_sensitive": False, "is_inductive": True, "notes": "Small hobby servo.", "common_warning": "Servos can cause voltage dips.", "beginner_tip": "Power servos from a separate 5V supply and connect grounds together."},
    {"id": 35, "name": "MG996R High Torque Servo", "category": "servo", "voltage_min": 5.0, "voltage_max": 6.0, "typical_current_mA": 500, "max_current_mA": 1500, "stall_current_mA": 2500, "logic_voltage": 5.0, "gpio_safe": False, "requires_driver": False, "is_high_current": True, "is_logic_sensitive": False, "is_inductive": True, "notes": "High-current servo; use external supply.", "common_warning": "Stall current can be several amps.", "beginner_tip": "Never power this from a microcontroller board."},
    {"id": 36, "name": "Small DC Motor", "category": "motor", "voltage_min": 3.0, "voltage_max": 6.0, "typical_current_mA": 200, "max_current_mA": 600, "stall_current_mA": 1000, "startup_current_mA": 800, "logic_voltage": None, "gpio_safe": False, "requires_driver": True, "is_high_current": True, "is_logic_sensitive": False, "is_inductive": True, "notes": "Small brushed DC motor.", "common_warning": "Requires a motor driver and flyback protection.", "beginner_tip": "Use a motor driver; GPIO pins should only send control signals."},
    {"id": 37, "name": "N20 Gear Motor", "category": "motor", "voltage_min": 6.0, "voltage_max": 6.0, "typical_current_mA": 150, "max_current_mA": 700, "stall_current_mA": 1600, "startup_current_mA": 1000, "logic_voltage": None, "gpio_safe": False, "requires_driver": True, "is_high_current": True, "is_logic_sensitive": False, "is_inductive": True, "notes": "Small geared motor.", "common_warning": "Stall current can be much higher than running current.", "beginner_tip": "Size your driver and supply for stall current."},
    {"id": 38, "name": "28BYJ-48 Stepper Motor", "category": "motor", "voltage_min": 5.0, "voltage_max": 5.0, "typical_current_mA": 240, "max_current_mA": 500, "startup_current_mA": 500, "logic_voltage": None, "gpio_safe": False, "requires_driver": True, "is_high_current": True, "is_logic_sensitive": False, "is_inductive": True, "notes": "Small stepper often paired with ULN2003.", "common_warning": "Requires a driver board.", "beginner_tip": "Use a ULN2003 driver module."},
    {"id": 39, "name": "Solenoid Lock", "category": "load", "voltage_min": 12.0, "voltage_max": 12.0, "typical_current_mA": 500, "max_current_mA": 1000, "startup_current_mA": 1000, "logic_voltage": None, "gpio_safe": False, "requires_driver": True, "is_high_current": True, "is_logic_sensitive": False, "is_inductive": True, "notes": "12V locking solenoid.", "common_warning": "Needs a driver and flyback diode.", "beginner_tip": "Use a MOSFET module and a 12V supply."},
    {"id": 40, "name": "Mini Water Pump", "category": "motor", "voltage_min": 5.0, "voltage_max": 5.0, "typical_current_mA": 300, "max_current_mA": 800, "startup_current_mA": 800, "logic_voltage": None, "gpio_safe": False, "requires_driver": True, "is_high_current": True, "is_logic_sensitive": False, "is_inductive": True, "notes": "Small 5V pump motor.", "common_warning": "Pump startup can cause voltage dips.", "beginner_tip": "Switch it with a MOSFET module and use common ground."},
    {"id": 41, "name": "Fan 5V", "category": "motor", "voltage_min": 5.0, "voltage_max": 5.0, "typical_current_mA": 150, "max_current_mA": 300, "startup_current_mA": 300, "logic_voltage": None, "gpio_safe": False, "requires_driver": True, "is_high_current": True, "is_logic_sensitive": False, "is_inductive": True, "notes": "Small brushless fan.", "common_warning": "Do not power directly from GPIO.", "beginner_tip": "Use a transistor or MOSFET switch."},
    {"id": 42, "name": "L298N Motor Driver", "category": "driver", "voltage_min": 5.0, "voltage_max": 12.0, "typical_current_mA": 30, "max_current_mA": 50, "logic_voltage": 5.0, "gpio_safe": True, "requires_driver": False, "is_high_current": False, "is_logic_sensitive": False, "is_inductive": False, "notes": "Common but inefficient motor driver.", "common_warning": "May heat up and drop motor voltage.", "beginner_tip": "TB6612FNG is usually better for small robots."},
    {"id": 43, "name": "TB6612FNG Motor Driver", "category": "driver", "voltage_min": 3.3, "voltage_max": 5.0, "typical_current_mA": 10, "max_current_mA": 20, "logic_voltage": 3.3, "gpio_safe": True, "requires_driver": False, "is_high_current": False, "is_logic_sensitive": False, "is_inductive": False, "notes": "Efficient small motor driver.", "common_warning": "Motor power still needs enough current.", "beginner_tip": "Good choice for small DC motor robots."},
    {"id": 44, "name": "ULN2003 Stepper Driver", "category": "driver", "voltage_min": 5.0, "voltage_max": 5.0, "typical_current_mA": 20, "max_current_mA": 30, "logic_voltage": 5.0, "gpio_safe": True, "requires_driver": False, "is_high_current": False, "is_logic_sensitive": False, "is_inductive": False, "notes": "Common driver for 28BYJ-48 stepper.", "common_warning": "Stepper power should come from the supply, not GPIO.", "beginner_tip": "Connect the driver ground to the microcontroller ground."},
    {"id": 45, "name": "MOSFET Module", "category": "driver", "voltage_min": 3.3, "voltage_max": 5.0, "typical_current_mA": 5, "max_current_mA": 10, "logic_voltage": 3.3, "gpio_safe": True, "requires_driver": False, "is_high_current": False, "is_logic_sensitive": False, "is_inductive": False, "notes": "Useful for switching high-current loads.", "common_warning": "Check whether the MOSFET is logic-level at 3.3V.", "beginner_tip": "Add flyback protection for motors, pumps, and solenoids."},
    {"id": 46, "name": "Logic Level Shifter", "category": "driver", "voltage_min": 3.3, "voltage_max": 5.0, "typical_current_mA": 1, "max_current_mA": 5, "logic_voltage": 3.3, "gpio_safe": True, "requires_driver": False, "is_high_current": False, "is_logic_sensitive": False, "is_inductive": False, "notes": "Converts between 3.3V and 5V logic.", "common_warning": "Not meant to power loads.", "beginner_tip": "Use it when connecting 5V signals to ESP32 GPIO."},
    {"id": 47, "name": "PCA9685 Servo Driver", "category": "driver", "voltage_min": 3.3, "voltage_max": 5.0, "typical_current_mA": 10, "max_current_mA": 20, "logic_voltage": 3.3, "gpio_safe": True, "requires_driver": False, "is_high_current": False, "is_logic_sensitive": False, "is_inductive": False, "notes": "Controls many servos, but servo power should still be external.", "common_warning": "The board does not magically provide servo current.", "beginner_tip": "Use a separate 5V servo supply."},
    {"id": 48, "name": "Breadboard Power Supply Module", "category": "power_module", "voltage_min": 3.3, "voltage_max": 5.0, "typical_current_mA": 20, "max_current_mA": 700, "logic_voltage": 5.0, "gpio_safe": False, "requires_driver": False, "is_high_current": False, "is_logic_sensitive": False, "is_inductive": False, "notes": "3.3V/5V breadboard supply module.", "common_warning": "Not suitable for large motors, servos, or LED strips.", "beginner_tip": "Treat 700mA as optimistic unless cooling is good."},
    {"id": 49, "name": "Bluetooth HC-05 Module", "category": "module", "voltage_min": 3.3, "voltage_max": 5.0, "typical_current_mA": 30, "max_current_mA": 50, "logic_voltage": 3.3, "gpio_safe": True, "requires_driver": False, "is_high_current": False, "is_logic_sensitive": True, "is_inductive": False, "notes": "Bluetooth serial module.", "common_warning": "RX pin may be 3.3V logic.", "beginner_tip": "Use a divider on Arduino TX into HC-05 RX."},
    {"id": 50, "name": "WiFi ESP8266 Module", "category": "module", "voltage_min": 3.3, "voltage_max": 3.3, "typical_current_mA": 80, "max_current_mA": 300, "startup_current_mA": 300, "logic_voltage": 3.3, "gpio_safe": True, "requires_driver": False, "is_high_current": True, "is_logic_sensitive": True, "is_inductive": False, "notes": "3.3V WiFi module.", "common_warning": "WiFi current spikes can cause resets.", "beginner_tip": "Use a regulator that can handle at least 300mA spikes."},
]


POWER_SOURCES = [
    {"id": 51, "name": "USB 5V 500mA", "voltage": 5.0, "max_current_mA": 500, "capacity_mAh": None, "internal_resistance_ohm": 0.25, "source_type": "usb", "notes": "Often too weak for motors, servos, or LED strips.", "beginner_tip": "Fine for small sensor projects."},
    {"id": 52, "name": "USB-C 5V 3A", "voltage": 5.0, "max_current_mA": 3000, "capacity_mAh": None, "internal_resistance_ohm": 0.08, "source_type": "usb", "notes": "Good for many small projects.", "beginner_tip": "Still use separate motor drivers for motors."},
    {"id": 53, "name": "9V Rectangular Battery", "voltage": 9.0, "max_current_mA": 300, "capacity_mAh": 500, "internal_resistance_ohm": 2.0, "source_type": "battery", "notes": "Poor choice for motors, servos, and LED strips.", "beginner_tip": "Use AA, LiPo, or an adapter for high-current loads."},
    {"id": 54, "name": "4xAA Battery Pack", "voltage": 6.0, "max_current_mA": 2000, "capacity_mAh": 2000, "internal_resistance_ohm": 0.35, "source_type": "battery", "notes": "Better than 9V battery for moderate loads.", "beginner_tip": "Useful for small robots with a regulator."},
    {"id": 55, "name": "3xAA Battery Pack", "voltage": 4.5, "max_current_mA": 1500, "capacity_mAh": 2000, "internal_resistance_ohm": 0.3, "source_type": "battery", "notes": "Simple battery pack for lower-voltage projects.", "beginner_tip": "May be low for 5V-only loads as cells drain."},
    {"id": 56, "name": "1S LiPo Battery", "voltage": 3.7, "max_current_mA": 5000, "capacity_mAh": 1200, "internal_resistance_ohm": 0.08, "source_type": "battery", "notes": "Needs boost converter for 5V components.", "beginner_tip": "Use proper LiPo charging and protection."},
    {"id": 57, "name": "2S LiPo Battery", "voltage": 7.4, "max_current_mA": 8000, "capacity_mAh": 2200, "internal_resistance_ohm": 0.06, "source_type": "battery", "notes": "Use buck converter for 5V electronics.", "beginner_tip": "Good for robot projects when regulated safely."},
    {"id": 58, "name": "5V Wall Adapter 1A", "voltage": 5.0, "max_current_mA": 1000, "capacity_mAh": None, "internal_resistance_ohm": 0.12, "source_type": "adapter", "notes": "Basic wall power for small projects.", "beginner_tip": "Borderline for several servos or large LED strips."},
    {"id": 59, "name": "5V Wall Adapter 2A", "voltage": 5.0, "max_current_mA": 2000, "capacity_mAh": None, "internal_resistance_ohm": 0.08, "source_type": "adapter", "notes": "Good for moderate 5V projects.", "beginner_tip": "Often enough for small robot demos."},
    {"id": 60, "name": "5V Wall Adapter 5A", "voltage": 5.0, "max_current_mA": 5000, "capacity_mAh": None, "internal_resistance_ohm": 0.04, "source_type": "adapter", "notes": "Good for LED strips and servo banks.", "beginner_tip": "Size wires and connectors for the current too."},
    {"id": 61, "name": "12V Wall Adapter 2A", "voltage": 12.0, "max_current_mA": 2000, "capacity_mAh": None, "internal_resistance_ohm": 0.08, "source_type": "adapter", "notes": "Needs regulator or buck converter for Arduino/ESP32 logic.", "beginner_tip": "Do not feed 12V directly into 5V loads."},
]


REGULATORS = [
    {"id": 62, "name": "AMS1117 Linear Regulator", "regulator_type": "linear", "input_voltage_min": 4.5, "input_voltage_max": 12.0, "output_voltage_options": [3.3, 5.0], "max_current_mA": 800, "efficiency": None, "notes": "Can overheat with high current or large voltage drops.", "beginner_tip": "Do not assume 800mA is safe without cooling."},
    {"id": 63, "name": "LM7805 Linear Regulator", "regulator_type": "linear", "input_voltage_min": 7.0, "input_voltage_max": 20.0, "output_voltage_options": [5.0], "max_current_mA": 1000, "efficiency": None, "notes": "Heat is approximately (Vin - Vout) * current.", "beginner_tip": "Use a buck converter when dropping from 9V or 12V at high current."},
    {"id": 64, "name": "Adjustable Buck Converter", "regulator_type": "buck", "input_voltage_min": 5.0, "input_voltage_max": 24.0, "output_voltage_options": [3.3, 5.0, 6.0, 9.0], "max_current_mA": 3000, "efficiency": 0.90, "notes": "Better for high current or large voltage drops.", "beginner_tip": "Set output voltage before connecting electronics."},
    {"id": 65, "name": "Boost Converter", "regulator_type": "boost", "input_voltage_min": 2.5, "input_voltage_max": 6.0, "output_voltage_options": [5.0, 9.0, 12.0], "max_current_mA": 2000, "efficiency": 0.85, "notes": "Stepping voltage up increases input current demand.", "beginner_tip": "Check battery current, not only output current."},
]


EXAMPLE_PROJECTS = [
    {"id": 1, "name": "Bluetooth RC Car", "description": "A phone-controlled Arduino vehicle that drives DC motors through a motor driver. It teaches motor control, PWM speed control, wireless communication, and power-system basics.", "components": [{"component_id": 1, "quantity": 1}, {"component_id": 42, "quantity": 1}, {"component_id": 36, "quantity": 2}, {"component_id": 49, "quantity": 1}], "power_source": "4xAA Battery Pack", "expected_notes": ["motor driver required", "Bluetooth module current", "battery pack sizing", "common ground"]},
    {"id": 2, "name": "Smart Plant Watering System", "description": "An automated irrigation build that reads soil moisture and powers a small pump when the plant is dry. It introduces analog sensors, switching circuits, and real-world automation.", "components": [{"component_id": 1, "quantity": 1}, {"component_id": 13, "quantity": 1}, {"component_id": 40, "quantity": 1}, {"component_id": 45, "quantity": 1}, {"component_id": 23, "quantity": 1}], "power_source": "5V Wall Adapter 2A", "expected_notes": ["pump needs driver", "moisture sensor load", "external pump power", "battery/runtime check"]},
    {"id": 3, "name": "Home Weather Station", "description": "A desktop monitor that measures weather data and displays it on a small screen. It combines sensor integration, display wiring, and optional IoT connectivity.", "components": [{"component_id": 4, "quantity": 1}, {"component_id": 9, "quantity": 1}, {"component_id": 16, "quantity": 1}, {"component_id": 21, "quantity": 1}], "power_source": "USB-C 5V 3A", "expected_notes": ["mostly safe", "WiFi current spikes", "3.3V sensors", "display current"]},
    {"id": 4, "name": "Ultrasonic Obstacle Avoiding Robot", "description": "An autonomous robot that uses distance sensing to avoid walls and objects. It teaches basic navigation logic, motor control, and startup current planning.", "components": [{"component_id": 1, "quantity": 1}, {"component_id": 7, "quantity": 1}, {"component_id": 42, "quantity": 1}, {"component_id": 36, "quantity": 2}, {"component_id": 34, "quantity": 1}], "power_source": "4xAA Battery Pack", "expected_notes": ["motor stall current", "ultrasonic sensor wiring", "driver required", "servo spike risk"]},
    {"id": 5, "name": "RFID Door Lock System", "description": "An access-control project where RFID cards unlock a servo or solenoid latch. It teaches serial communication, embedded security logic, and actuator power safety.", "components": [{"component_id": 1, "quantity": 1}, {"component_id": 20, "quantity": 1}, {"component_id": 34, "quantity": 1}, {"component_id": 32, "quantity": 1}, {"component_id": 27, "quantity": 2}], "power_source": "5V Wall Adapter 2A", "expected_notes": ["RFID logic voltage", "servo current spikes", "GPIO safety", "access-control wiring"]},
    {"id": 6, "name": "LED Music Visualizer", "description": "A sound-reactive LED project that changes patterns based on microphone input. It is a fun way to learn real-time signals, LED power demand, and visual feedback.", "components": [{"component_id": 2, "quantity": 1}, {"component_id": 30, "quantity": 60}, {"component_id": 27, "quantity": 1}], "power_source": "5V Wall Adapter 5A", "expected_notes": ["LED current draw", "external 5V supply", "capacitor recommended", "brightness affects current"]},
    {"id": 7, "name": "Wi-Fi Smart Home Controller", "description": "An ESP32 or ESP8266 automation controller for lights, fans, or appliances through relays. It introduces Wi-Fi control, switching loads, and GPIO protection.", "components": [{"component_id": 4, "quantity": 1}, {"component_id": 33, "quantity": 2}], "power_source": "USB-C 5V 3A", "expected_notes": ["relay coil current", "WiFi spikes", "GPIO should signal only", "isolate AC loads"]},
    {"id": 8, "name": "Digital Alarm Clock with OLED Display", "description": "A programmable clock that shows time, alarms, and optional temperature data on an OLED. It teaches display wiring, buttons, buzzers, and low-current embedded design.", "components": [{"component_id": 2, "quantity": 1}, {"component_id": 21, "quantity": 1}, {"component_id": 31, "quantity": 1}, {"component_id": 17, "quantity": 1}], "power_source": "USB 5V 500mA", "expected_notes": ["mostly safe", "OLED current", "buzzer current", "battery backup concept"]},
    {"id": 9, "name": "Line Following Robot", "description": "A robot that follows a dark line using infrared sensors and motor feedback. It is a classic robotics project for sensor-driven control and motor power planning.", "components": [{"component_id": 1, "quantity": 1}, {"component_id": 14, "quantity": 3}, {"component_id": 43, "quantity": 1}, {"component_id": 36, "quantity": 2}], "power_source": "4xAA Battery Pack", "expected_notes": ["motor driver required", "sensor feedback", "stall current", "battery pack sizing"]},
    {"id": 10, "name": "ESP32 Security Camera System", "description": "A Wi-Fi camera project that streams video or captures images remotely with an ESP32-CAM. It can be expanded with motion detection, SD storage, and alerts.", "components": [{"component_id": 5, "quantity": 1}, {"component_id": 11, "quantity": 1}], "power_source": "5V Wall Adapter 1A", "expected_notes": ["camera current spikes", "WiFi brownout risk", "5V supply quality", "PIR sensor current"]},
]


def seed_database(db: Session) -> None:
    """Replace lookup data with the Phase 1 starter catalog."""

    db.query(ExampleProject).delete()
    db.query(Regulator).delete()
    db.query(PowerSource).delete()
    db.query(Component).delete()

    db.add_all(Component(**item) for item in COMPONENTS)
    db.add_all(PowerSource(**item) for item in POWER_SOURCES)
    db.add_all(Regulator(**item) for item in REGULATORS)
    db.add_all(ExampleProject(**item) for item in EXAMPLE_PROJECTS)
    db.commit()


def by_name(items: list[dict], name: str) -> dict:
    return next(item for item in items if item["name"] == name)


if __name__ == "__main__":
    from app.database import SessionLocal, init_db

    init_db()
    with SessionLocal() as session:
        seed_database(session)
    print(
        f"Seeded {len(COMPONENTS)} components, "
        f"{len(POWER_SOURCES)} power sources, "
        f"{len(REGULATORS)} regulators, and "
        f"{len(EXAMPLE_PROJECTS)} example projects."
    )
