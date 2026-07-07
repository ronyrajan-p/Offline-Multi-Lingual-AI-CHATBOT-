# Offline Raspberry Pi OLED Multilingual AI Chatbot

This project is a fully offline multilingual AI chatbot designed for a Raspberry Pi 4 or Raspberry Pi 5 board with an OLED display. It runs without internet access by using local processing, offline translation, local storage, and a lightweight device UI.

## Purpose

The goal is to build a compact offline chatbot device for environments where internet access is unavailable, unreliable, expensive, or not allowed. Because the target display is an OLED, the application should avoid heavy browser-based UI architecture and instead use a small device-oriented interface.

## Target Hardware

- Raspberry Pi 4 or Raspberry Pi 5
- OLED display using I2C or SPI
- MicroSD card or SSD storage
- Optional buttons, rotary encoder, USB keyboard, microphone, or speaker
- Optional cooling, especially for Raspberry Pi 5 or long-running inference

## Optimal Architecture

```text
User Input
 Buttons / Keyboard / Voice
        |
        v
Device Controller
 Python main loop
        |
        +-------------------+
        |                   |
        v                   v
OLED Display Driver    Chatbot Core
Status + short text    Prompt + session logic
                            |
       +--------------------+--------------------+
       |                    |                    |
       v                    v                    v
Local AI Engine     Offline Translation      SQLite
llama.cpp / small   English, Tamil, Hindi    chat history
local model         translation service      settings
       |                    |
       +---------+----------+
                 |
                 v
          Formatted Response
                 |
                 v
          OLED Display Output
```

## Architecture Decision

For a Raspberry Pi 4 or 5 with an OLED display, the recommended architecture is a local Python application instead of a React web application.

Use this approach:

- Python application as the main runtime.
- OLED display driver for device output.
- Lightweight input handler for buttons, keyboard, rotary encoder, or voice input.
- Local chatbot core for prompt and conversation management.
- Local AI service for model inference.
- Offline translation service for English, Tamil, and Hindi.
- SQLite for chat history and settings.

Avoid this for the OLED version:

- React frontend as the primary UI.
- Browser-based kiosk mode as the main interface.
- Heavy FastAPI-only architecture when no network UI is needed.
- Long responses that cannot fit on a small display.

FastAPI can still be added later as an optional local admin or debugging interface, but it should not be the core runtime for the OLED device.

## Recommended Folder Structure

```text
raspberry/
|
+-- app/
|   +-- main.py
|   +-- controller.py
|   +-- config.py
|
+-- core/
|   +-- chatbot.py
|   +-- language_detector.py
|   +-- prompt_builder.py
|   +-- response_formatter.py
|   +-- conversation_manager.py
|   +-- utils.py
|
+-- display/
|   +-- oled_driver.py
|   +-- screen_manager.py
|   +-- text_layout.py
|   +-- screens.py
|
+-- input/
|   +-- buttons.py
|   +-- keyboard.py
|   +-- voice_input.py
|
+-- services/
|   +-- local_ai.py
|   +-- offline_translation.py
|   +-- speech.py
|
+-- models/
|   +-- local-llm-files/
|
+-- translations/
|   +-- argos-packages/
|
+-- database/
|   +-- chatbot.sqlite
|   +-- schema.sql
|
+-- scripts/
|   +-- install.sh
|   +-- run.sh
|   +-- setup_service.sh
|
+-- readme.md
```

## Core Modules

The `core/` package contains reusable chatbot logic that should stay independent from Raspberry Pi hardware.

```text
core/
|
+-- chatbot.py                # Main chatbot orchestration
+-- language_detector.py      # English, Tamil, Hindi detection or selection
+-- prompt_builder.py         # Builds prompts for the local model
+-- response_formatter.py     # Formats short OLED-friendly responses
+-- conversation_manager.py   # Tracks sessions and message history
+-- utils.py                  # Shared helper functions
```

The core should not directly control the OLED, buttons, microphone, `llama.cpp`, Argos Translate, or SQLite implementation details. Those should be handled through service and device layers.

## OLED Display Layer

The OLED display should show short, readable device states instead of full chat pages.

### Recommended Screens

- Boot screen
- Ready screen
- Listening or input screen
- Processing screen
- Response screen
- Language selection screen
- Error screen
- Settings screen

### Display Rules

- Keep messages short.
- Wrap text based on OLED width.
- Use pagination for longer responses.
- Show clear status labels such as `Ready`, `Thinking`, `Tamil`, or `Offline`.
- Use high-contrast monochrome UI for small OLED displays.
- Avoid dense paragraphs.

## Input Options

Choose one input method first, then add others later.

### Recommended First Input

Use a USB keyboard during development because it is simple and reliable.

### Device Input Options

- USB keyboard for typed messages.
- Buttons for menu navigation.
- Rotary encoder for scrolling and selection.
- Microphone for voice input.
- Speaker for spoken responses.

For the first working version, use keyboard input and OLED output. Add buttons, voice input, and audio output after the chatbot flow is stable.

## Local AI Strategy

Raspberry Pi 4 and Raspberry Pi 5 can run local models, but performance depends heavily on model size, quantization, cooling, and memory.

### Recommended Approach

- Use `llama.cpp` for local inference.
- Use a small quantized model.
- Prefer short prompts and short answers.
- Limit maximum response length.
- Stream tokens if possible.
- Keep conversation history compact.
- Store only the most useful recent messages in the prompt.

### Model Guidance

- Raspberry Pi 4: use the smallest practical quantized model.
- Raspberry Pi 5: can handle slightly larger models, especially with cooling.
- Prefer GGUF quantized models.
- Test response time before finalizing the model.

## Offline Translation

The chatbot should support English, Tamil, and Hindi without internet access.

### Recommended Approach

- Use Argos Translate if suitable language packages are available.
- Store translation packages under `raspberry/translations/`.
- Translate user input into the model's working language if needed.
- Translate the model response back to the selected user language.
- Cache repeated translations where possible.

If translation quality or performance is not acceptable on Raspberry Pi, start with manual language selection and predefined multilingual responses for common device states.

## Database

Use SQLite for local storage.

Store:

- Chat sessions
- Messages
- Selected language
- Device settings
- Error logs
- Model configuration

Keep the database in:

```text
raspberry/database/chatbot.sqlite
```

## Technologies

- Python 3
- Raspberry Pi OS
- OLED display library such as `luma.oled` or `Adafruit_CircuitPython_SSD1306`
- `llama.cpp`
- Argos Translate
- SQLite
- Optional: Vosk or another offline speech-to-text engine
- Optional: eSpeak NG or another offline text-to-speech engine
- Optional: FastAPI for local admin/debug interface only

## Current Program

The current implementation is a runnable offline simulator of the Raspberry Pi OLED chatbot architecture.

It includes:

- Console-backed OLED display simulation.
- USB keyboard-style console input.
- Chatbot core with language detection and prompt building.
- Offline translation service wrapper with an Argos Translate extension point.
- Local AI service wrapper with a deterministic fallback response.
- SQLite chat history, settings, and error logging.
- Placeholder adapters for buttons, voice input, speech output, and hardware OLED rendering.

Run from the project root:

```powershell
python -m raspberry.app.main
```

Useful commands inside the chatbot:

```text
/lang en
/lang ta
/lang hi
/exit
```

The fallback AI keeps the application usable before a local GGUF model and `llama.cpp` are connected.

### Qwen Tamil And Hindi Responses

The chatbot uses Qwen-style ChatML prompts for Qwen2.5 Instruct models. For Tamil output, select Tamil with:

```text
/lang ta
```

For Hindi output, select Hindi with:

```text
/lang hi
```

Then ask your question normally. The prompt tells Qwen to generate a fresh Tamil or Hindi response in the correct script instead of using fixed demo-style replies.

Language commands are handled by the Python chatbot before they reach Qwen. Use `/lang ta`, `/lang hi`, or `/language hi`. If `/lang ta` gets a model-generated answer, you are probably inside raw `llama-cli` instead of this app.

Start the chatbot with `python3 -m raspberry.app.main`. Starting `llama-cli` directly bypasses the command parser and OLED update logic.

When the app calls Qwen internally, `llama-cli` is run as a one-shot worker process. You should not see the large `llama.cpp` banner or `available commands` list after a normal message.

### OLED Chatbot Responses

Use OLED mode when running the real device:

```bash
export CHATBOT_DISPLAY_DRIVER=ssd1306_i2c
export CHATBOT_I2C_PORT=1
export CHATBOT_I2C_ADDRESS=0x3C
export CHATBOT_DISPLAY_PAGE_SECONDS=2.5
export CHATBOT_FONT_PATH=
export CHATBOT_FONT_SIZE=10
python3 -m raspberry.app.main
```

Chatbot responses use the same OLED display path as boot, status, and language screens. Longer responses are wrapped and shown page by page.

If the OLED shows random patterns, test the display without the LLM:

```bash
python3 -m raspberry.scripts.oled_test
```

If patterns continue, try `CHATBOT_DISPLAY_DRIVER=sh1106_i2c`; many 1.3 inch OLED modules use SH1106 instead of SSD1306.

Install Noto fonts on the Pi for Tamil and Hindi OLED rendering:

```bash
sudo apt install -y fonts-noto-core fonts-noto-extra
```

## Implementation Steps

1. Prepare the Raspberry Pi
   - Install Raspberry Pi OS.
   - Enable I2C or SPI based on the OLED module.
   - Install Python 3 and required system packages.
   - Confirm the OLED display works with a basic test script.

2. Build the OLED display layer
   - Create `display/oled_driver.py`.
   - Create `display/screen_manager.py`.
   - Add basic screens for boot, ready, processing, response, and error states.
   - Add text wrapping and pagination.

3. Add the input layer
   - Start with USB keyboard input.
   - Add button or rotary encoder navigation after the basic flow works.
   - Keep input handling separate from chatbot logic.

4. Build the chatbot core
   - Create the `core/` modules.
   - Implement conversation management.
   - Implement prompt building.
   - Implement response formatting for short OLED output.
   - Add language selection for English, Tamil, and Hindi.

5. Add local AI support
   - Install and configure `llama.cpp`.
   - Add a small quantized local model.
   - Create `services/local_ai.py`.
   - Limit response length and keep prompts compact.

6. Add offline translation
   - Install Argos Translate.
   - Add available English, Tamil, and Hindi translation packages.
   - Create `services/offline_translation.py`.
   - Cache translations if repeated phrases are common.

7. Add SQLite storage
   - Create `database/schema.sql`.
   - Store chat history and settings locally.
   - Keep database access outside the chatbot core.

8. Create the main controller
   - Create `app/main.py`.
   - Create `app/controller.py`.
   - Connect input, display, chatbot core, local AI, translation, and database services.
   - Add graceful error handling and startup checks.

9. Optimize for Raspberry Pi 4/5
   - Use a small quantized model.
   - Reduce prompt size.
   - Limit output tokens.
   - Use response streaming if possible.
   - Monitor CPU, memory, and temperature.
   - Add cooling if inference causes throttling.

10. Run as a device service
   - Create a startup script.
   - Add a `systemd` service.
   - Start the chatbot automatically after boot.
   - Log errors to a local file.

11. Test offline behavior
   - Disconnect internet.
   - Reboot the Raspberry Pi.
   - Confirm the OLED shows the boot and ready screens.
   - Test English, Tamil, and Hindi conversations.
   - Test long responses, errors, and database persistence.

## Device User Flow

```text
Power On
   |
   v
OLED Boot Screen
   |
   v
Load Model + Translation + Database
   |
   v
Ready Screen
   |
   v
User Enters Message
   |
   v
Translate if Needed
   |
   v
Local AI Generates Response
   |
   v
Format Short OLED Response
   |
   v
Display Response Page
```

## Development Roadmap

1. Test OLED display output.
2. Build the device controller loop.
3. Add keyboard input.
4. Build the chatbot core.
5. Add SQLite settings and chat history.
6. Add local AI inference.
7. Add offline translation.
8. Add buttons or rotary encoder.
9. Add optional voice input and speech output.
10. Configure auto-start on boot.
11. Test fully offline on Raspberry Pi 4 and Raspberry Pi 5.

## Implementation Principles

- Design for the OLED first.
- Keep the UI short, readable, and state-based.
- Keep hardware code separate from chatbot logic.
- Keep local AI and translation behind service wrappers.
- Avoid external API dependencies.
- Keep prompts and responses short.
- Optimize for reliability before model size.
- Store all data locally.
- Make the device usable immediately after boot.
