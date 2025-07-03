Multi-Agent Asteroid Detection System

This project implements a foundational multi-agent AI pipeline for real-time asteroid detection and orbital analysis. It features a Python FastAPI backend that simulates a continuous stream of astronomical image data, processes it through a series of specialized AI agents, and provides real-time updates to a React-based web frontend via REST API polling.
✨ Key Features

    Multi-Agent Architecture: Modular Python agents for:

        Image Ingestion: Loading FITS astronomical images.

        Calibration: Performing basic image calibration and WCS (World Coordinate System) solutions.

        Detection: Identifying potential asteroid streaks/objects using a placeholder PyTorch CNN.

        Orbit Estimation: Simulating orbital element computation from detections using Skyfield.

    FastAPI Backend: Provides a robust, asynchronous server for pipeline orchestration and data management.

    REST API Polling: Frontend periodically fetches the latest processed results from a dedicated API endpoint (/latest_results).

    Real-time Image Visualization: Displays the simulated astronomical images on the frontend with detected asteroid positions overlaid.

    React Frontend: An interactive web dashboard built with React and Tailwind CSS to visualize pipeline status, image data, detections, and orbital elements.

    Simulated Data Stream: Generates dummy FITS image files periodically to mimic continuous telescope observations, now including image data for visualization.

    Robustness: Includes error handling, logging, type hints, and file clean-up mechanisms.

🏗️ System Architecture

The system is composed of two main parts:

    Python Backend (pipeline.py and agents/):

        A FastAPI application acts as the central orchestrator.

        A background task continuously generates simulated FITS image files.

        Each simulated image is passed through a sequence of Python agents (Ingest, Calibration, Detection, Orbit).

        The latest processed results (including image data) are stored in memory and exposed via a REST API endpoint for the frontend.

    React Frontend (asteroid-ui/):

        A single-page application built with Create React App.

        Polls the backend's /latest_results endpoint at regular intervals to retrieve the most recent pipeline data.

        Presents pipeline status, the processed image with detections, recent detections list, and estimated orbital elements in an intuitive dashboard.

graph TD
    subgraph Backend (Python FastAPI)
        A[Simulated Data Stream] --> B(Image Ingest Agent)
        B --> C(Calibration Agent)
        C --> D(Detection Agent)
        D --> E(Orbit Agent)
        E --> F{Store Latest Results in Memory}
        F -- HTTP GET /latest_results --> G[REST API Endpoint]
    end

    subgraph Frontend (React UI)
        H[Web Browser] --> I(Polling Client)
        I -- Periodically fetch data --> G
        I --> J[Display Real-time Data & Image]
    end

🚀 Setup & Installation
Prerequisites

    Git: For cloning the repository.

    Python 3.8+: For the backend.

    Node.js (v18 LTS Recommended): For the React frontend.

        Highly Recommended for Windows: Use nvm-windows to manage Node.js versions. Install nvm-windows, then run nvm install 18 and nvm use 18 in your terminal. This ensures compatibility with create-react-app.

Clone the Repository

git clone <repository_url>
cd multi-agent-asteroid

1. Backend Setup (Python)

Navigate to the root of the cloned repository:

cd multi-agent-asteroid

Create and activate a Python virtual environment:

python -m venv venv
# On Windows:
.\venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

Install Python dependencies:

pip install -r requirements.txt
# Ensure Pillow is also installed for image processing:
pip install Pillow

2. Frontend Setup (React)

Navigate into the frontend directory:

cd asteroid-ui

Important: Ensure Node.js 18 LTS is active in your terminal (e.g., nvm use 18).

Clean previous Node.js installations (crucial for resolving dependency conflicts):

npm cache clean --force
rm -rf node_modules
rm package-lock.json
# On Windows, if rm fails:
# rmdir /s /q node_modules
# del package-lock.json

Install Node.js dependencies:

npm install

▶️ Running the System

You will need two separate terminal windows.
1. Start the Backend

In your Python project root directory (multi-agent-asteroid), with your virtual environment activated:

uvicorn pipeline:app --host 127.0.0.1 --port 8000 --reload

This will start the FastAPI server on http://127.0.0.1:8000. It will also begin simulating data and creating dummy FITS files in a simulated_fits_data/ directory. Keep this terminal running.
2. Start the Frontend

In your React project directory (multi-agent-asteroid/asteroid-ui):

npm start

This will compile the React application and open it in your web browser, typically at http://localhost:3000. Keep this terminal running.

You should now see the web UI updating in real-time with pipeline status, the processed image with overlaid detections, and lists of detections and orbital elements as the backend processes simulated data.
📁 Project Structure

multi-agent-asteroid/
├── pipeline.py               # FastAPI backend, pipeline orchestration, data simulation, REST API
├── requirements.txt          # Python dependencies
├── .gitignore                # Git ignore rules for generated files and environments
├── agents/                   # Contains individual AI agents
│   ├── __init__.py
│   ├── ingest.py             # Image Ingest Agent
│   ├── calibration.py        # Calibration Agent
│   ├── detection.py          # Detection Agent
│   └── orbit.py              # Orbit Estimation Agent
├── simulated_fits_data/      # Directory for dummy FITS files (generated by pipeline)
└── asteroid-ui/              # React frontend application
    ├── public/
    ├── src/
    │   └── App.js            # Main React component for UI, handles polling & image rendering
    │   └── index.css         # Tailwind CSS imports
    ├── package.json          # Frontend dependencies and scripts
    ├── tailwind.config.js    # Tailwind CSS configuration
    └── ... (other React files)

🔮 Future Enhancements

This project provides a strong foundation. Future work includes:

    Real Data Integration: Adapting the simulate_data_stream to fetch and process actual FITS data from public astronomical archives (e.g., ZTF via astroquery).

    Advanced Agents: Implementing more sophisticated detection models (e.g., DeepStreaks), robust WCS calibration, and precise orbit determination algorithms.

    Governance & Human-in-the-Loop (HITL): Adding a Meta-Agent for system-wide optimization, cost control, and an HITL agent for expert validation of critical detections.

    Synthetic Data Generation: Developing an agent to create diverse synthetic training data for model robustness.

    Ethical & Security Considerations: Implementing agents for compliance checking, audit logging, and misuse detection.

    Cognitive Services: Agents for automated literature synthesis, grant proposal generation, and public communication.

📄 License

MIT License (or choose your preferred license)