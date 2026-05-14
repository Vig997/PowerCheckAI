# PowerCheck AI

PowerCheck AI is a full-stack web app that helps students check the power safety of Arduino, ESP32, robotics, IoT, and beginner electronics projects before they build them.

<img width="941" height="472" alt="powercheck ai frnt page" src="https://github.com/user-attachments/assets/bd04c5c2-5729-446e-ae45-1cc4008b0f1a" />

The idea is simple: a lot of maker projects fail because the power supply is too weak, a motor pulls too much current, a GPIO pin is used incorrectly, or a regulator gets too hot. PowerCheck AI helps catch those problems early in a way that is understandable for high school and college students.

PowerCheck AI is not a professional certification tool. It gives educational estimates and warnings. Always double-check important designs with datasheets, measurements, and safe wiring practices.

## Why I Built This

Beginner electronics projects often focus on code first, but the hardware power system is just as important. An Arduino or ESP32 project can reset, flicker, overheat, or behave randomly if the power design is not strong enough.

PowerCheck AI is meant to answer questions like:

- Can my power supply handle this project?
- Will my ESP32 reset when motors start?
- Is it safe to connect this part to a GPIO pin?
- How long will my battery last?
- Will my regulator overheat?
- Do I need a motor driver, MOSFET, buck converter, or separate power rail?

## Main Features

<img width="940" height="465" alt="image" src="https://github.com/user-attachments/assets/dae9f09d-4e3b-477d-8047-aa1ec51c6c2c" />

- Local project saving with no login required
- Starter projects for common Arduino and ESP32 builds
- Builder page where users describe their project and parts list
- Natural language component extraction
- Component matching against a beginner-friendly electronics database
- Electrical checks for current, voltage, battery life, GPIO safety, and heat
- 8 PowerCheck module cards with scores and explanations
- Expanded module views with deeper student-friendly analysis
- Final recommendation explaining what to keep, add, replace, or verify
- Dark mode and responsive UI

## PowerCheck Modules

<img width="935" height="458" alt="image" src="https://github.com/user-attachments/assets/45caf22f-f661-44dd-93f1-fcbe42662a7a" />

The Builder analyzes projects using 8 focused modules:

1. Real-Time Current Profiling
2. Brownout Prediction Engine
3. GPIO Protection Analysis
4. Battery Discharge Modeling
5. Thermal Regulator Analysis
6. Component Compatibility Engine
7. Power Tree Visualization
8. Startup Surge Analysis

Each module explains:

- what parts were detected
- what the issue means
- what could go wrong
- what fixes are recommended
- what information is missing

## Example Projects

The app includes starter projects such as:

- Bluetooth RC Car
- Smart Plant Watering System
- Home Weather Station
- Ultrasonic Obstacle Avoiding Robot
- RFID Door Lock System
- LED Music Visualizer
- Wi-Fi Smart Home Controller
- Digital Alarm Clock with OLED Display
- Line Following Robot
- ESP32 Security Camera System

Users can move starter projects into My Projects, edit them, and analyze them in the Builder.

## Engineering Concepts Used

PowerCheck AI uses simplified but practical electrical engineering ideas:

- current draw
- peak current
- motor startup current
- servo stall current
- voltage sag
- brownout risk
- GPIO current limits
- 3.3V and 5V logic safety
- battery runtime
- regulator heat
- buck and boost converters
- common ground
- separate power rails
- inductive load protection

The app keeps the explanations beginner-friendly, but the checks are based on real concepts that matter in embedded systems.

## Software Concepts Used

This project also demonstrates full-stack software engineering:

- React frontend
- TypeScript data models
- Tailwind CSS styling
- FastAPI backend
- SQLite database
- SQLAlchemy models
- Pydantic schemas
- REST API endpoints
- localStorage project persistence
- pytest backend tests
- Vite build workflow
- Windows-friendly setup scripts

## AI / ML / NLP System

The analysis system is local and explainable:

- rule-based text parsing
- alias matching for common part names
- fuzzy component matching
- deterministic electrical calculations
- scikit-learn RandomForest risk support
- rule-based fallback if ML is unavailable
- template-based student-friendly explanations

The ML model supports risk scoring, but it does not invent component specs or replace the engineering rules.

## Tech Stack

Frontend:

- React
- TypeScript
- Tailwind CSS
- Vite
- Recharts
- localStorage

Backend:

- Python
- FastAPI
- SQLite
- SQLAlchemy
- Pydantic
- scikit-learn
- pytest

## How To Run The Project

This project includes Windows batch scripts so it is easy to run from VS Code or Command Prompt.

### 1. Install Backend

```bat
install_backend.bat
```

This creates `backend\.venv` and installs the Python dependencies.

### 2. Install Frontend

```bat
install_frontend.bat
```

This installs the React/Vite dependencies.

### 3. Start Everything

```bat
runfs
```

Then open:

```text
http://127.0.0.1:5173
```

The backend runs at:

```text
http://127.0.0.1:8000
```

FastAPI docs are available at:

```text
http://127.0.0.1:8000/docs
```

## Other Useful Commands

Run only the backend:

```bat
run_backend.bat
```

Run only the frontend:

```bat
run_frontend.bat
```

Run tests and build checks:

```bat
run_tests.bat
```

## VS Code Workflow

Open the project folder in VS Code, then use:

```text
Terminal > Run Task...
```

Available tasks include:

- Install Backend
- Install Frontend
- Run Backend
- Run Frontend
- Run Full Stack
- Run Tests

## Testing

The backend tests check:

- current calculations
- regulator heat calculations
- API endpoints
- seed data
- `/docs`
- helper endpoints
- AI project description analysis

The frontend check verifies:

- TypeScript compilation
- production build
- Vite configuration
  
