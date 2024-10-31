# Mission Control

**Mission Control** is a real-time aircraft tracking application that fetches Automatic Dependent Surveillance Broadcasting (ADS-B) data from the OpenSky API. This data is relayed to a Next.js dashboard that features an interactive map, enabling users to track commercial aircraft in near real-time.

# Demo
<img src="demo.gif" alt="Demo" style="width:60%;">
<p>Demo of the Mission Control application</p>

<a href="docs/mission-control-sequence.png" target="_blank">
    <img src="docs/mission-control-sequence.png" alt="Sequence Diagram" style="width:60%;">
</a>
<p><a href="docs/mission-control-sequence.png" target="_blank">Sequence Diagram</a></p>

## Features

- **Real-time Tracking:** Visualize aircraft movements on a dynamic map using ADS-B data.
- **Data Relay:** Utilizes RabbitMQ to efficiently pass data from the OpenSky integration to a FastAPI backend.
- **Next.js Dashboard:** A user-friendly interface for displaying tracking data.

## System Requirements

- Node.js (v18 or higher)
- Python (v3.9 or higher)
- RabbitMQ Server
- SQLite (for local database)
- Docker (optional, for containerized deployment)

## Project Structure

```
mission-control/
│
├── dashboard/         # Next.js web application
├── api/              # FastAPI backend service
│   └── main.py
├── dbupdater/        # Database updater service
│   └── main.py
├── integrations/     # External integrations
│   └── opensky/      # OpenSky API integration
│       └── opensky.py
├── lib/              # Shared Python library code
├── env.dev           # Development environment variables
└── requirements.txt  # Root level Python dependencies
```

## Installation & Setup

### 1. RabbitMQ Server
Ensure RabbitMQ is installed and running on your system. You can either:
- Install it locally: Follow instructions at [RabbitMQ Downloads](https://www.rabbitmq.com/download.html)
- Use Docker: `docker run -d --name rabbitmq -p 5672:5672 -p 15672:15672 rabbitmq:management`

### 2. Environment Setup
The project includes an `env.dev` file with default configuration values. Copy this file to create your local environment file:

```bash
cp env.dev .env
```

Default configuration values:
```env
# Database Configuration
DATABASE_NAME="mission-control.db"

# RabbitMQ Configuration
RABBIT_HOST="localhost"
ADSB_QUEUE="adsb"
REGIONS_QUEUE="regions"

# OpenSky API Configuration
OPENSKY_API_URL='https://opensky-network.org/api'

# API Configuration
API_VERSION=1.0.0
ORIGINS=["*"]
```

These default values are suitable for local development. Modify them in your `.env` file if you need to customize any settings.

### 3. Dashboard (Next.js)
```bash
cd dashboard
npm install
```

### 4. Python Environment Setup
Create and activate a Python virtual environment from the root directory:
```bash
# From the root directory
python -m venv venv
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
pip install -r requirements.txt
```

This will install all required Python dependencies for all components, including the shared library code.

## Running the Application

All Python scripts must be run from the root directory to ensure proper access to the shared library code.

Start all components in the following order:

### 1. Start RabbitMQ
Ensure RabbitMQ is running and accessible on port 5672

### 2. Start the API
From the root directory:
```bash
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
python -m api.main
```
The API will be available at `http://localhost:8000`

### 3. Start the Dashboard
```bash
cd dashboard
npm run dev
```
Access the dashboard at `http://localhost:3000`

### 4. Start the Database Updater
From the root directory:
```bash
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
python -m dbupdater.main
```

### 5. Start the OpenSky Integration
From the root directory:
```bash
source venv/bin/activate  # On Windows: .\venv\Scripts\activate
python -m integrations.opensky.opensky
```

## Project Structure Details

### Shared Library
The `lib/` directory contains shared Python code used across multiple components. This is why all Python scripts must be run from the root directory using the module syntax (`python -m`). This ensures that Python can properly import shared libraries and maintain consistent behavior across all components.

### Python Module Structure
- All Python components are structured as modules
- Scripts should be run using the `-m` flag from the root directory
- This enables proper importing of shared code from the `lib/` directory
- Maintains consistent path resolution across all components

## Troubleshooting

Common issues and solutions:

1. **Module Import Errors**
   - Ensure you're running Python scripts from the root directory
   - Verify that your Python virtual environment is activated
   - Check that all dependencies are installed via `requirements.txt`

2. **Database Issues**
   - Ensure the SQLite database file is created in the expected location
   - Check file permissions for the database file
   - Verify the DATABASE_NAME in your .env file

3. **RabbitMQ Connection Issues**
   - Ensure RabbitMQ server is running
   - Verify RABBIT_HOST setting in .env file
   - Check RabbitMQ management interface at `http://localhost:15672`

4. **OpenSky API Issues**
   - Verify OPENSKY_API_URL is accessible
   - Check for rate limiting if making frequent requests
   - Consider using authenticated access for higher rate limits

5. **Data Not Appearing on Dashboard**
   - Verify all components are running
   - Check browser console for frontend errors
   - Verify message queues are properly configured (ADSB_QUEUE and REGIONS_QUEUE)

## Work in Progress

This project is currently under development, and future updates will include integration of additional data sources beyond ADS-B. Check back for updates!

## License

This project is licensed under the MIT License.
