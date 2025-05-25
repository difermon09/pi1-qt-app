# Sensor Monitoring Application

PyQt6 desktop application to visualize and manage ESP32 sensor data. Provides an intuitive graphical interface for:
- Real-time sensor readings visualization
- Sensor management and configuration
- Data analysis visualization using Llama 3.2
- Data and graph export

## Project Structure

```
qt_app/
├── main.py          # Application entry point
├── views/           # User interface components
│   ├── main_window.py
│   ├── sensor_view.py
│   └── analysis_view.py
├── resources/       # Resources (images, icons)
└── requirements.txt # Dependencies
```

## Installation

### Option 1: Use the executable (Recommended)

1. Go to the [Releases](https://github.com/difermon09/pi1-qt-app/releases) section of this repository
2. Download the latest version of `PI1_app_windows.exe`
3. Run the downloaded file

### Option 2: Installation from source code

1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run the application:
```bash
python main.py
```

## Compilation

To create an executable:

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Create the executable:
```bash
pyinstaller --onefile --windowed --icon=logotip.ico --add-data "Fons_app.png;." main.py
```

The executable will be created in the `dist/` folder.

## Features

- Real-time dashboard
- Interactive graphs
- Sensor management
- Analysis visualization
- Data export
- Interface customization

## Configuration

The application automatically connects to the API at `http://localhost:8000`. If you need to change the API URL:

1. Open `config.py`
2. Modify the `API_URL` variable

## Troubleshooting

1. **If the application doesn't start**
   - Verify Python 3.12+ is installed
   - Check all dependencies are installed
   - Verify the API is running

2. **If data is not visible**
   - Verify API connection
   - Check if sensors are registered
   - Verify if readings are available

## Contact

For support or questions, contact:
- GitHub: [difermon09](https://github.com/difermon09) 