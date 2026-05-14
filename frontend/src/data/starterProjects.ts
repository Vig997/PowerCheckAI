import type { ExampleProject } from "../types";

export const starterProjects: ExampleProject[] = [
  {
    id: 1,
    name: "Bluetooth RC Car",
    description: "A phone-controlled Arduino vehicle that drives DC motors through a motor driver. It teaches motor control, PWM speed control, wireless communication, and power-system basics.",
    full_description:
      "Bluetooth RC Car (Arduino + Motor Driver)\n\nA small robotic vehicle controlled from a phone over Bluetooth. The Arduino reads commands from a Bluetooth module and drives DC motors through a motor driver, allowing forward/reverse movement and steering. This project teaches motor control, PWM speed control, power systems, and wireless communication, and is extremely common in beginner robotics and embedded systems.\n\nParts needed: Arduino Nano Every, L298N Dual H-Bridge Motor Driver, TT 6V Geared DC Motors (x4), HC-05 Bluetooth Module, 18650 Battery Holder + 2x Samsung 30Q 18650 Cells, LM2596 Buck Converter, Acrylic Smart Car Chassis Kit, MG90S Metal Gear Servo (optional steering/camera), Mini rocker switch, Dupont jumper wires.",
    components: [{ component_id: 1, quantity: 1 }, { component_id: 42, quantity: 1 }, { component_id: 36, quantity: 2 }, { component_id: 49, quantity: 1 }],
    power_source: "4xAA Battery Pack",
    expected_notes: ["motor driver required", "Bluetooth module current", "battery pack sizing", "common ground"],
  },
  {
    id: 2,
    name: "Smart Plant Watering System",
    description: "An automated irrigation build that reads soil moisture and powers a small pump when the plant is dry. It introduces analog sensors, switching circuits, and real-world automation.",
    full_description:
      "Smart Plant Watering System\n\nAn automated irrigation system that monitors soil moisture and turns on a small water pump when the soil becomes too dry. The Arduino continuously reads analog moisture sensor data and can optionally display readings on an LCD or send alerts over Wi-Fi. This project introduces sensors, relays/transistors, and real-world automation concepts.\n\nParts needed: Arduino Nano, Capacitive Soil Moisture Sensor v1.2, Mini 5V Peristaltic Water Pump, IRLZ44N MOSFET, 1N4007 Flyback Diode, 12V DC Power Adapter, Silicone water tubing, SSD1306 OLED Display (128x64 I2C), Breadboard + jumper wires.",
    components: [{ component_id: 1, quantity: 1 }, { component_id: 13, quantity: 1 }, { component_id: 40, quantity: 1 }, { component_id: 45, quantity: 1 }, { component_id: 23, quantity: 1 }],
    power_source: "5V Wall Adapter 2A",
    expected_notes: ["pump needs driver", "moisture sensor load", "external pump power", "battery/runtime check"],
  },
  {
    id: 3,
    name: "Home Weather Station",
    description: "A desktop monitor that measures weather data and displays it on a small screen. It combines sensor integration, display wiring, and optional IoT connectivity.",
    full_description:
      "Home Weather Station\n\nA desktop weather monitor that measures temperature, humidity, pressure, and sometimes altitude. The Arduino gathers data from environmental sensors and displays it on an OLED/LCD screen or uploads it online using Wi-Fi. This project is popular because it combines sensor integration, data visualization, and IoT connectivity.\n\nParts needed: ESP32 DevKit V1, BME280 Temperature/Humidity/Pressure Sensor, SSD1306 OLED Display, DS3231 RTC Module, 5V USB-C Power Supply, Mini breadboard, Female-to-female jumper wires.",
    components: [{ component_id: 4, quantity: 1 }, { component_id: 9, quantity: 1 }, { component_id: 16, quantity: 1 }, { component_id: 21, quantity: 1 }],
    power_source: "USB-C 5V 3A",
    expected_notes: ["mostly safe", "WiFi current spikes", "3.3V sensors", "display current"],
  },
  {
    id: 4,
    name: "Ultrasonic Obstacle Avoiding Robot",
    description: "An autonomous robot that uses distance sensing to avoid walls and objects. It teaches basic navigation logic, motor control, and startup current planning.",
    full_description:
      "Ultrasonic Obstacle Avoiding Robot\n\nA small autonomous robot that uses an ultrasonic distance sensor to detect walls or objects and automatically change direction to avoid collisions. The Arduino processes sensor data and controls motors accordingly, introducing autonomous navigation and basic robotics logic.\n\nParts needed: Arduino Uno R3, HC-SR04 Ultrasonic Sensor, SG90 Servo Motor, L298N Motor Driver, TT Gear Motors (x2), 2WD Robot Chassis Kit, 7.4V Li-ion Battery Pack, XL4015 Voltage Regulator, ON/OFF Toggle Switch.",
    components: [{ component_id: 1, quantity: 1 }, { component_id: 7, quantity: 1 }, { component_id: 42, quantity: 1 }, { component_id: 36, quantity: 2 }, { component_id: 34, quantity: 1 }],
    power_source: "4xAA Battery Pack",
    expected_notes: ["motor stall current", "ultrasonic sensor wiring", "driver required", "servo spike risk"],
  },
  {
    id: 5,
    name: "RFID Door Lock System",
    description: "An access-control project where RFID cards unlock a servo or solenoid latch. It teaches serial communication, embedded security logic, and actuator power safety.",
    full_description:
      "RFID Door Lock System\n\nAn electronic access-control system where RFID cards or tags unlock a servo-driven latch. The Arduino reads the RFID UID, compares it to authorized IDs, and unlocks the mechanism if valid. This project is commonly used to learn embedded security systems and serial communication.\n\nParts needed: Arduino Nano, MFRC522 RFID Reader Module, MIFARE Classic RFID Cards, MG996R High Torque Servo, Active Buzzer Module, Green/Red 5mm LEDs, 220 ohm Resistors, 12V DC Adapter, Breadboard + Dupont wires.",
    components: [{ component_id: 1, quantity: 1 }, { component_id: 20, quantity: 1 }, { component_id: 34, quantity: 1 }, { component_id: 32, quantity: 1 }, { component_id: 27, quantity: 2 }],
    power_source: "5V Wall Adapter 2A",
    expected_notes: ["RFID logic voltage", "servo current spikes", "GPIO safety", "access-control wiring"],
  },
  {
    id: 6,
    name: "LED Music Visualizer",
    description: "A sound-reactive LED project that changes patterns based on microphone input. It is a fun way to learn real-time signals, LED power demand, and visual feedback.",
    full_description:
      "LED Music Visualizer\n\nA reactive LED lighting system that changes brightness or patterns based on sound input from a microphone module. The Arduino analyzes audio amplitude and drives LED strips or matrices in sync with music, making it a fun introduction to signal processing and real-time visualization.\n\nParts needed: Arduino Nano, MAX9814 Microphone Amplifier Module, WS2812B Addressable LED Strip (60 LEDs/m), 1000 uF Capacitor, 330 ohm Data Line Resistor, 5V 10A Power Supply, Acrylic diffuser case, JST connectors.",
    components: [{ component_id: 2, quantity: 1 }, { component_id: 30, quantity: 60 }, { component_id: 27, quantity: 1 }],
    power_source: "5V Wall Adapter 5A",
    expected_notes: ["LED current draw", "external 5V supply", "capacitor recommended", "brightness affects current"],
  },
  {
    id: 7,
    name: "Wi-Fi Smart Home Controller",
    description: "An ESP32 or ESP8266 automation controller for lights, fans, or appliances through relays. It introduces Wi-Fi control, switching loads, and GPIO protection.",
    full_description:
      "Wi-Fi Smart Home Controller\n\nAn IoT-based automation system that lets users control lights, fans, or appliances from a phone or browser using Wi-Fi. The ESP32 or ESP8266 hosts a web server or communicates with platforms like Blynk or MQTT to toggle relays remotely. This project is very common in home automation and IoT learning.\n\nParts needed: ESP32-WROOM-32 Dev Board, 4-Channel Opto-Isolated Relay Module, DHT22 Temperature Sensor, PIR Motion Sensor HC-SR501, Mean Well 5V Power Supply, Screw terminal blocks, Breadboard + jumper wires.",
    components: [{ component_id: 4, quantity: 1 }, { component_id: 33, quantity: 2 }],
    power_source: "USB-C 5V 3A",
    expected_notes: ["relay coil current", "WiFi spikes", "GPIO should signal only", "isolate AC loads"],
  },
  {
    id: 8,
    name: "Digital Alarm Clock with OLED Display",
    description: "A programmable clock that shows time, alarms, and optional temperature data on an OLED. It teaches display wiring, buttons, buzzers, and low-current embedded design.",
    full_description:
      "Digital Alarm Clock with OLED Display\n\nA programmable alarm clock that displays time, alarms, and temperature on a small OLED screen. The Arduino uses a real-time clock module to maintain accurate time even when powered off, and buttons allow the user to set alarms and settings.\n\nParts needed: Arduino Nano Every, DS3231 Precision RTC Module, SSD1306 OLED Display, KY-006 Passive Buzzer, Tactile Push Buttons (x3), 10k ohm Resistors, USB-C Power Module, Acrylic enclosure.",
    components: [{ component_id: 2, quantity: 1 }, { component_id: 21, quantity: 1 }, { component_id: 31, quantity: 1 }, { component_id: 17, quantity: 1 }],
    power_source: "USB 5V 500mA",
    expected_notes: ["mostly safe", "OLED current", "buzzer current", "battery backup concept"],
  },
  {
    id: 9,
    name: "Line Following Robot",
    description: "A robot that follows a dark line using infrared sensors and motor feedback. It is a classic robotics project for sensor-driven control and motor power planning.",
    full_description:
      "Line Following Robot\n\nA robot that uses infrared sensors to detect and follow a black line on the floor autonomously. The Arduino continuously adjusts motor speeds based on sensor feedback, teaching closed-loop control and sensor-driven robotics. This is one of the most common robotics competition projects.\n\nParts needed: Arduino Nano, QTR-8A Reflectance Sensor Array, DRV8833 Motor Driver, N20 Metal Gear Motors, Pololu Zumo Chassis, 7.4V LiPo Battery, Slide power switch, JST battery connector.",
    components: [{ component_id: 1, quantity: 1 }, { component_id: 14, quantity: 3 }, { component_id: 43, quantity: 1 }, { component_id: 36, quantity: 2 }],
    power_source: "4xAA Battery Pack",
    expected_notes: ["motor driver required", "sensor feedback", "stall current", "battery pack sizing"],
  },
  {
    id: 10,
    name: "ESP32 Security Camera System",
    description: "A Wi-Fi camera project that streams video or captures images remotely with an ESP32-CAM. It can be expanded with motion detection, SD storage, and alerts.",
    full_description:
      "ESP32 Security Camera System\n\nA Wi-Fi-enabled camera project using the ESP32-CAM module to stream video to a browser or capture images remotely. It can be extended with motion detection, cloud uploads, or mobile notifications, making it a strong beginner IoT/computer vision project.\n\nParts needed: ESP32-CAM AI Thinker Module, FT232RL FTDI Programmer, OV2640 Camera Module, HC-SR501 PIR Motion Sensor, 32GB SanDisk MicroSD Card, AMS1117 5V to 3.3V Regulator, 5V 2A Wall Adapter, Dupont jumper wires.",
    components: [{ component_id: 5, quantity: 1 }, { component_id: 11, quantity: 1 }],
    power_source: "5V Wall Adapter 1A",
    expected_notes: ["camera current spikes", "WiFi brownout risk", "5V supply quality", "PIR sensor current"],
  },
];
