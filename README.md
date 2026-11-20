# IoT Sentinel

**IoT Network Security and Unauthorized Actuator Access Detection System**  
ITCN · Unit 3 · Software-based implementation

IoT Sentinel is a beginner-friendly, local software prototype of an IoT gateway security monitor. It creates virtual smart-home devices, generates normal and suspicious command traffic, checks each command against a set of understandable security rules, and records every decision in a local SQLite audit log.

No Arduino, ESP32, sensor, actuator, or physical network is required.

## What is included

- **Virtual devices:** temperature sensor, humidity sensor, smart light, front-door lock, fan, and an IoT gateway.
- **Device controls:** send commands through simulated owner, administrator, and guest profiles.
- **Security engine:** client identity checks, demo-token validation, role/actuator permissions, replay checks, per-client rate limiting, and command-value validation.
- **Five controlled attack scenarios:** unauthorised actuator access, unknown-device impersonation, replay, traffic flooding, and invalid credentials.
- **Dashboard:** overview, device state, traffic monitor, attack lab, security events, reports, and an explanation of the system.
- **Audit and export:** decisions are stored in SQLite and can be exported as CSV.
- **Optional MQTT bridge:** mirror generated command events to a local Mosquitto broker. The project works without MQTT.
- **Automated tests:** unit tests for the security rules.

## Quick start on macOS

### Option 1 — easiest

1. Install Python 3.11 or newer if it is not already installed.
2. Unzip the project folder.
3. Open the folder in Finder.
4. Double-click `start_mac.command`.
5. The first run creates a local `.venv`, installs the dependencies, and starts the dashboard. A browser tab opens at the local Streamlit address shown in Terminal.

If macOS blocks the script, right-click `start_mac.command`, choose **Open**, and confirm. You can also use the Terminal instructions below.

### Option 2 — Terminal

Open Terminal and run these commands from inside the unzipped `IoT-Sentinel` folder:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
streamlit run main.py
```

To stop the app, return to Terminal and press `Control + C`.

## First demonstration

1. Open **Overview** and create normal traffic. Observe that authorised requests are accepted.
2. Open **Devices & controls**. Use the Guest profile to try to unlock the front door. The gateway should block the command because guests cannot control the lock.
3. Open **Attack simulation lab** and run the five scenarios one at a time.
4. Open **Security events** to read the explanation for each blocked request.
5. Open **Reports & analytics** and download the audit log as CSV.

The dashboard starts with an empty audit history. Use **Reset lab and clear history** in the sidebar to restore the default virtual device states and clear the local log.

## Optional MQTT setup

The simulator and dashboard work without a broker. To add local MQTT transport, install and start Docker Desktop, then run this command from the project folder:

```bash
docker compose up -d mosquitto
```

In the dashboard, open **Local MQTT bridge** and connect to `127.0.0.1`, port `1883`. Command events will be mirrored to:

```text
iot-sentinel/traffic/events
```

To inspect the messages, install the Mosquitto command-line tools and run:

```bash
mosquitto_sub -h 127.0.0.1 -t 'iot-sentinel/#' -v
```

Stop the broker with:

```bash
docker compose down
```

The compose configuration binds the host port to loopback (`127.0.0.1`) and is intended only for a local classroom demonstration. Anonymous access is enabled inside this isolated demo broker for simplicity. Do not expose it to a LAN or the public internet.

## Run the tests

With the project virtual environment activated:

```bash
python -m unittest discover -s tests -v
```

or, after installing `requirements-dev.txt`:

```bash
pytest -q
```

## Project structure

```text
IoT-Sentinel/
├── main.py                    # Streamlit application entry point
├── config.py                  # Demo device clients and lab settings
├── requirements.txt           # Runtime dependencies
├── start_mac.command          # One-click macOS launcher
├── core/
│   ├── engine.py              # Gateway validation and actuator state
│   ├── store.py               # SQLite audit log
│   └── mqtt_bridge.py         # Optional MQTT publisher
├── simulator/
│   ├── devices.py             # Virtual device definitions
│   └── traffic.py             # Normal traffic and attack scenarios
├── security/
│   └── rules.py               # Threat descriptions and response guidance
├── dashboard/
│   ├── styles.py              # Visual theme
│   └── views.py               # Dashboard pages
├── tests/
│   └── test_security_engine.py
├── docs/
│   ├── PROJECT_OVERVIEW.md
│   └── TEST_PLAN.md
├── mqtt/
│   └── mosquitto.conf
└── data/                      # Local SQLite database is created here
```

## Important scope and security note

This is a **software prototype and controlled simulation**, not a production IoT security gateway. Devices, users, tokens, commands, and attacks are synthetic. The demo tokens in `config.py` are intentionally visible examples, not secrets. The prototype demonstrates selected controls; it does not implement production cryptography, TLS device provisioning, radio packet capture, secure key rotation, or comprehensive intrusion detection.

The flooding rule allows up to five valid requests per client in a ten-second window and blocks requests above that threshold. The replay rule checks repeated request IDs during the running session. A production system should use cryptographically secure message authentication, unique nonces or sequence numbers, timestamps, secure transport, and persistent replay state.

See `docs/PROJECT_OVERVIEW.md` and `docs/TEST_PLAN.md` for material that can be adapted into the project report.
