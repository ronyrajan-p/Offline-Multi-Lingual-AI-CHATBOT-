# Offline Multilingual AI Chatbot — Raspberry Pi 5 + I2C OLED

A fully offline, multilingual chatbot device built for the **Raspberry Pi 5**, driven entirely through a **0.96" 128x64 SSD1306 I2C OLED display**. It runs with zero internet dependency: local inference, local translation, local storage, and a compact device UI.

## Hardware Target

| Component | Spec |
|---|---|
| Board | Raspberry Pi 5 (4GB, minimum) |
| Display | SSD1306 128x64 OLED, I2C interface |
| Storage | 32GB+ microSD, A2-rated, NVMe SSD via the M.2 HAT for sustained inference workloads |
| Cooling | Active cooler (required for sustained local inference on Pi 5) |
| Input | USB keyboard for the first working build |
| Power | Official 27W USB-C supply |

## Tech Stack

This project uses one deliberate stack, chosen for efficiency on Pi 5 hardware. No alternatives are listed; each layer has a single implementation.

| Layer | Technology |
|---|---|
| Runtime | Python 3.11, running as a headless systemd service |
| Display driver | `luma.oled` + `Pillow`, talking to the SSD1306 over I2C |
| Local inference | `llama-server`, compiled natively on the Pi 5 with ARM NEON optimizations, kept running as its own persistent service |
| Inference transport | HTTP, from the chatbot process to `llama-server`'s `/health` and `/completion` endpoints, using Python's standard library `urllib` |
| Model | Qwen2.5-1.5B-Instruct, GGUF, Q4_K_M quantization |
| Translation | Argos Translate, with English, Tamil, and Hindi packages installed locally |
| Storage | SQLite, for chat history, sessions, settings, and error logs |
| Process supervision | systemd, for boot-time autostart and crash recovery, two units |

React, FastAPI, and any browser-based kiosk layer are intentionally excluded from the core runtime. The OLED cannot render a web page, so the entire application is a native Python process that writes directly to the framebuffer through `luma.oled`.

Inference is a persistent server, not a per-message subprocess. Earlier designs shelled out to `llama-cli` for every message and depended on `--no-conversation` flags to force one-shot output. Current `llama-cli` builds default into an interactive chat TUI that writes its banner straight to the controlling terminal, bypassing captured output entirely, and reload the full model from disk on every turn. `llama-server` loads the model once at boot; each chat turn becomes a short HTTP request against already-resident weights.

## Architecture

```text
USB Keyboard Input
        |
        v
Device Controller (app/controller.py)
        |
        +-----------------------------+
        |                             |
        v                             v
Chatbot Core                   OLED Display Layer
(core/*.py)                    (display/*.py, I2C)
        |
        +---------------+---------------+
        |               |               |
        v               v               v
llama-server        Argos Translate      SQLite
HTTP client          (services/          (services/
(services/            offline_          storage.py)
 local_ai.py)          translation.py)
        |               |               |
        +---------------+---------------+
                        |
                        v
              Formatted Response
                        |
                        v
                I2C OLED Output
```

## Project Structure

```text
raspberry/
├── app/
│   ├── main.py            # Composes and starts the controller
│   ├── controller.py       # Main device loop
│   └── config.py           # All hardware and runtime settings, env-driven
├── core/
│   ├── chatbot.py           # Orchestration
│   ├── language_detector.py
│   ├── prompt_builder.py
│   ├── response_formatter.py
│   ├── conversation_manager.py
│   └── utils.py
├── display/
│   ├── oled_driver.py       # ConsoleOLEDDriver + HardwareOLEDDriver (I2C)
│   ├── screen_manager.py
│   ├── text_layout.py
│   └── screens.py
├── input/
│   ├── keyboard.py           # Primary input for the first build
│   ├── buttons.py            # Future GPIO menu navigation
│   └── voice_input.py        # Future microphone input
├── services/
│   ├── local_ai.py            # llama.cpp process wrapper
│   ├── offline_translation.py # Argos Translate wrapper
│   └── storage.py             # SQLite access
├── database/
│   ├── chatbot.sqlite
│   └── schema.sql
├── translations/
│   └── argos-packages/
├── models/
│   └── qwen2.5-1.5b-instruct-q4_k_m.gguf
├── scripts/
│   ├── install.sh
│   ├── run.sh
│   ├── oled_test.py
│   └── setup_service.sh
├── .env.example
└── requirements.txt
```

## I2C OLED Setup

### 1. Enable I2C on Raspberry Pi OS

```bash
sudo raspi-config
# Interface Options -> I2C -> Enable
sudo reboot
```

### 2. Wire the display

| OLED Pin | Raspberry Pi 5 Pin |
|---|---|
| VCC | Pin 1, 3.3V |
| GND | Pin 6, GND |
| SDA | Pin 3, GPIO2 |
| SCL | Pin 5, GPIO3 |

### 3. Confirm the address

```bash
sudo apt install -y i2c-tools
i2cdetect -y 1
```

The SSD1306 shows up at `0x3C`. That value is the default in `config.py` and requires no override.

### 4. Install fonts for Tamil and Hindi glyphs

```bash
sudo apt install -y fonts-noto-core fonts-noto-extra
```

Font paths used by the app:

```text
/usr/share/fonts/truetype/noto/NotoSansTamil-Regular.ttf
/usr/share/fonts/truetype/noto/NotoSansDevanagari-Regular.ttf
```

## Installation

```bash
git clone <repo-url>
cd "Multi Language Chatbot"
python3 -m pip install --upgrade pip
python3 -m pip install -r raspberry/requirements.txt
cp raspberry/.env.example raspberry/.env
```

## Configuration

All hardware and runtime behavior is controlled through environment variables, read in `raspberry/app/config.py`.

```bash
export CHATBOT_DISPLAY_DRIVER=ssd1306_i2c
export CHATBOT_I2C_PORT=1
export CHATBOT_I2C_ADDRESS=0x3C
export CHATBOT_OLED_WIDTH=128
export CHATBOT_OLED_HEIGHT=64
export CHATBOT_DISPLAY_PAGE_SECONDS=2.5
export CHATBOT_FONT_PATH=/usr/share/fonts/truetype/noto/NotoSansTamil-Regular.ttf
export CHATBOT_FONT_SIZE=10
export CHATBOT_MODEL=/home/pi/raspberry/models/qwen2.5-1.5b-instruct-q4_k_m.gguf
export CHATBOT_LLAMA_SERVER_HOST=127.0.0.1
export CHATBOT_LLAMA_SERVER_PORT=8080
export CHATBOT_LLAMA_REQUEST_TIMEOUT=60
export CHATBOT_LLAMA_STARTUP_WAIT=60
export CHATBOT_ALLOW_FALLBACK_AI=false
export CHATBOT_REQUIRE_TRANSLATION=true
export CHATBOT_LANGUAGE=en
```

`CHATBOT_MODEL` is read by `scripts/start_llama_server.sh`, not by the chatbot process itself. The chatbot only ever talks to `CHATBOT_LLAMA_SERVER_HOST`/`CHATBOT_LLAMA_SERVER_PORT` over HTTP.

### Verify the OLED before running the full chatbot

```bash
python3 -m raspberry.scripts.oled_test
```

## Build llama.cpp on the Pi 5

```bash
git clone https://github.com/ggerganov/llama.cpp
cd llama.cpp
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build --config Release -j4
sudo cp build/bin/llama-server /usr/local/bin/
```

`llama-cli` is a debugging tool for a human sitting at the keyboard. This project uses `llama-server` in production, which serves a plain HTTP completion API and never touches the terminal.

Download the quantized model into `raspberry/models/`:

```bash
mkdir -p raspberry/models
# Place qwen2.5-1.5b-instruct-q4_k_m.gguf in raspberry/models/
```

Start the server and confirm it is healthy, before starting the chatbot:

```bash
export CHATBOT_MODEL=/home/pi/raspberry/models/qwen2.5-1.5b-instruct-q4_k_m.gguf
raspberry/scripts/start_llama_server.sh &
sleep 5
curl http://127.0.0.1:8080/health
```

A healthy server responds with `{"status":"ok"}`. Loading a 1.5B Q4 model typically takes ten to twenty seconds on a Pi 5; that cost is now paid once at boot, not on every message.

## Install Translation Packages

```bash
python3 -m pip install argostranslate
python3 - <<'PY'
import argostranslate.package
argostranslate.package.update_package_index()
available = argostranslate.package.get_available_packages()
targets = [("en", "ta"), ("ta", "en"), ("en", "hi"), ("hi", "en")]
for from_code, to_code in targets:
    match = next(p for p in available if p.from_code == from_code and p.to_code == to_code)
    argostranslate.package.install_from_path(match.download())
PY
```

## Run

With `llama-server` already running (see above), start the chatbot in a second terminal:

```bash
python3 -m raspberry.app.main
```

If `llama-server` is not yet ready, the OLED shows a **Waiting AI** screen and the app polls `/health` for up to `CHATBOT_LLAMA_STARTUP_WAIT` seconds. With `CHATBOT_ALLOW_FALLBACK_AI=true` it then falls back; with it set to `false` it surfaces a clear error instead.

Language switching commands inside the chatbot:

```text
/lang en
/lang ta
/lang hi
/status
```

`/status` reports the live backend name, `llama-server` when the HTTP server answered the last health check and `fallback` otherwise, so you always know which engine produced a given reply.

## Run as systemd Services

Two services run on the finished device: `llama-server.service` loads the model once, and `chatbot.service` depends on it. Print both unit templates with:

```bash
raspberry/scripts/setup_service.sh
```

Create `/etc/systemd/system/llama-server.service`:

```ini
[Unit]
Description=llama.cpp inference server
After=multi-user.target

[Service]
Type=simple
User=pi
EnvironmentFile=/home/pi/Multi Language Chatbot/raspberry/.env
ExecStart=/home/pi/Multi Language Chatbot/raspberry/scripts/start_llama_server.sh
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Create `/etc/systemd/system/chatbot.service`:

```ini
[Unit]
Description=Offline Multilingual OLED Chatbot
After=llama-server.service
Requires=llama-server.service

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/Multi Language Chatbot
EnvironmentFile=/home/pi/Multi Language Chatbot/raspberry/.env
ExecStart=/usr/bin/python3 -m raspberry.app.main
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

Enable and start both:

```bash
sudo systemctl daemon-reload
sudo systemctl enable llama-server.service chatbot.service
sudo systemctl start llama-server.service
sudo systemctl start chatbot.service
sudo journalctl -u llama-server.service -u chatbot.service -f
```

`Requires=llama-server.service` means a chatbot restart never races a cold model load; systemd starts the server first and only brings the chatbot up once that unit is active.

## OLED Display Rules

- Messages stay short, sized for a 128x64 panel.
- Text wraps to the configured character width per line.
- Long responses paginate automatically at the interval set by `CHATBOT_DISPLAY_PAGE_SECONDS`.
- Status labels stay compact: `Ready`, `Thinking`, `Tamil`, `Offline`.
- The UI stays high-contrast monochrome throughout.

## Performance Notes for Pi 5

- The active cooler is mandatory once inference workloads run continuously; thermal throttling degrades response latency fast.
- The Q4_K_M quantization keeps the 1.5B model responsive on Pi 5's 4-core Cortex-A76 CPU.
- Prompt history stays compact through `ConversationManager`, keeping context windows small and inference fast.
- `CHATBOT_AI_MAX_TOKENS` caps generation length; 80 tokens balances readability against latency on-device.
- `llama-server` loads weights into RAM exactly once at boot. A chat turn costs one inference pass over an already-loaded model instead of a full model reload, which is the dominant cost on SD-card-backed storage.
- `--ctx-size` stays at 2048 for both the server and the compact conversation history, keeping memory pressure predictable across long sessions.

## Troubleshooting

**The OLED shows `AI Offline`, and the terminal prints a `llama-server is not reachable` error.**
`llama-server.service` is not running. It may also still be loading the model. Check its status:

```bash
sudo systemctl status llama-server.service
curl http://127.0.0.1:8080/health
```

**`llama-cli`'s ASCII banner appears directly in the terminal instead of a formatted chatbot reply.**
This happens if `llama-cli` is invoked directly instead of `llama-server`. Current `llama-cli` builds default into an interactive chat session and write their splash screen straight to the controlling terminal, bypassing any output capture. This project never calls `llama-cli` from the chatbot process; confirm `scripts/start_llama_server.sh` is what's actually running, not a stray `llama-cli` invocation.

**Responses feel slow on the first message after boot.**
Expected. `llama-server` finishes loading the model in the background while the OLED shows `Waiting AI`. Subsequent messages are fast because the model stays resident in RAM.

## Data Storage

SQLite persists locally at `raspberry/database/chatbot.sqlite`:

- Chat sessions and messages
- Selected language per session
- Device settings
- Error logs

## Verifying Fully Offline Operation

```bash
sudo systemctl stop NetworkManager
sudo reboot
```

After reboot, confirm the OLED shows the boot screen, then the ready screen, then confirm a full conversation completes in English, Tamil, and Hindi without any network activity.

## Testing

```bash
python3 -m raspberry.tests.run_checks
```
