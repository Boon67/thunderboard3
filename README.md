# thunderboard3

A Python-based IoT sensor reader for the Silicon Labs Thunderboard Sense (Thunder Sense) BLE devices. Reads environmental sensor data via Bluetooth Low Energy and stores it in a MariaDB database.

## Overview

This application discovers nearby Thunderboard Sense devices via BLE, reads their environmental sensors (temperature, humidity, CO2, VOC, UV, pressure, sound, and ambient light), and logs the data to a MariaDB database.

## Sensors Supported

- Temperature
- Humidity
- CO2 (Carbon Dioxide)
- TVOC (Total Volatile Organic Compounds)
- UV Index
- Ambient Light / Luminosity
- Barometric Pressure
- Sound Level

## Prerequisites

- Raspberry Pi or Linux system with Bluetooth
- Python 3.7+
- BlueZ (Linux Bluetooth stack)
- MariaDB/MySQL server
- Silicon Labs Thunderboard Sense device

## Dependencies

```
bluepy
bleak
requests
mariadb
```

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Boon67/thunderboard3.git
   cd thunderboard3
   ```

2. Install Python dependencies:
   ```bash
   pip install bluepy bleak requests mariadb
   ```

3. Set up the MariaDB database:
   - Create database `env`
   - Create user `environment_logger` with password
   - Create the `records` table (see schema in `env.py`)

4. Configure the device address in `tb.py`:
   ```python
   DEVICE_ADDR = 'XX:XX:XX:XX:XX:XX'  # Your Thunderboard MAC address
   ```

5. Run the sensor reader:
   ```bash
   python tb.py
   ```

## Project Structure

```
├── tb.py               # Main BLE sensor reader (bluepy-based)
├── tbProperites.py     # Thunderboard property definitions
├── ioDemo/             # I/O demonstration scripts
└── README.md
```

## Configuration

Edit the constants at the top of `tb.py` (or `env.py` for the async version):

```python
DB_USER = "environment_logger"
DB_PASSWORD = "password"
DB_HOST = "localhost"
DB_PORT = 3306
DB_DATABASE = "env"
INTERVAL_SECONDS = 5
```

## License

MIT - see [LICENSE](LICENSE)
