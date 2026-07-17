# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands by Sub-Project

### Imager (Qt6 / C++)
* **Build AppImage (Linux)**: `./create-appimage.sh` or `./create-embedded.sh`
* **Build (Windows with VS Code)**: Set CMake Configure Args:
  `-DQt6_ROOT=C:\Qt\6.9.0\mingw_64 -DMINGW64_ROOT=C:\Qt\Tools\mingw1310_64 -DENABLE_INNO_INSTALLER=ON -DIMAGER_SIGNED_APP=ON`
  Select variant `MinSizeRel`, target `inno_installer`, and build. Output installer is under `%WORKSPACE%\build\installer`.
* **Build macOS**: `./qt/build-qt-macos.sh` then select target `rpi_imager`.
* **Run Tests**: CTest-configured Catch2 tests. Run target `test_customization_generator` or executable `customization_generator_test`. Run target `fat_partition_test` manually.

### Mina Voice Assistant (Python / C Helper)
* **Install Deps**: `make install-deps` then `pip install -r requirements.txt`. For ASR capabilities, install `pip install nemo_toolkit[asr] librosa torch`.
* **Compile Backend**: `make compile` (builds `bin/<arch>/apicomm` and `libs/<arch>/libstt.so` or `libs/<arch>/stt.dll`).
* **Run GUI**: `make run` (or `python main_gui.py`, append `-f` for fullscreen or `-s` for studio mode).
* **Run CLI**: `make cli` (or `python main_cli.py`).
* **Lint & Format**: `make lint` (runs flake8), `make format` (runs black), `make sort-imports` (runs isort).
* **Test**: `make test` runs validation compileall on source Python files. Run unit tests using `pytest tests/`.

### NoNail AI Agent (Python v1 / C++ v2)
* **Install (Python v1)**: `pip install -e ".[dev]"` (compiles native `_fastcore` C++ extension automatically if compiler present).
* **Run Mode CLI**: `nonail chat` or `nonail run "prompt"`.
* **Run Mode MCP Server**: `nonail serve`.
* **Python Tests**: Run `.venv/bin/pytest tests -q`. Run a single test file: `.venv/bin/pytest tests/test_fallback.py -q`. Run a specific test by name: `.venv/bin/pytest tests -q -k "test_rate_limit_error_detection_patterns"`. **Crucial**: Target the `tests/` directory explicitly to avoid picking up the archived `v1/tests` subfolder which collides due to identical module names.
* **Python Lint**: `.venv/bin/ruff check nonail tests`.
* **C++ v2 Build**:
  - Native: `cd v2 && cmake -B build -DCMAKE_BUILD_TYPE=Release && cmake --build build -j$(nproc)`
  - Cross-Compile (OpenWrt/MT7621): `source /path/to/openwrt/sdk/environment-setup-* && cmake -B build-openwrt -DCMAKE_BUILD_TYPE=MinSizeRel -DNONAIL_CROSS_COMPILE=ON -DCMAKE_TOOLCHAIN_FILE=cmake/openwrt-mt7621.cmake && cmake --build build-openwrt -j$(nproc) && cmake --build build-openwrt --target strip-binary`
* **C++ v2 Tests**: Run target `nonail-tests`.

### Scraping (FastAPI / LangChain Stack)
* **Install Deps**: `pip install -r requirements.txt`.
* **Run with Docker Compose**: `docker compose up -d --build`.
* **Run API locally**: `uvicorn api.main:app --reload`.
* **Run Collector locally**: `python -m collector.main`.
* **Run Tests**: `pytest -v --cov=collector --cov=database --cov=api --cov=agent`.

---

## High-Level Architecture

MultiForge is a modular platform designed to repurpose legacy ARM hardware (such as TV Boxes and routers) into digital edge infrastructure.

```
                  ┌───────── Imager (Qt/C++) ─────────┐
                  │ Writes images to SD/eMMC devices  │
                  └─────────────────┬─────────────────┘
                                    ▼
┌───────────────────────── Linux Host (TV Box / Router) ─────────────────────────┐
│                                                                                │
│  ┌───────────────────────┐  ┌───────────────────────┐  ┌────────────────────┐  │
│  │   Mina Voice Agent    │  │     NoNail Client     │  │ Scraping Platform  │  │
│  │ Hybrid Local Classifier│  │ System Tool-Use Agent │  │ Scrapers, API, RAG │  │
│  │  Offline SQLite + GUI │  │ MCP client/server +   │  │ PG/Redis backend   │  │
│  │                       │  │ C++ OpenWrt target v2 │  │                    │  │
│  └───────────────────────┘  └───────────┬───────────┘  └────────────────────┘  │
│                                         │                                      │
└─────────────────────────────────────────┼──────────────────────────────────────┘
                                          ▼
                         ┌────────── Zombie Master ──────────┐
                         │ Communicates via TCP/WebSockets  │
                         │ with optional Telegram/WA bot ops │
                         └───────────────────────────────────┘
```

### Decoupling & Integration Paradigms

1. **Voice Intelligence Pipeline (Mina)**:
   Designed to operate with zero network latency. Standard query routes first hit the `IntentClassifier` (`intent_classifier.py`), which uses regexp patterns to extract intents (e.g., class rooms, professors) and query a local SQLite database (`academic.db`). If no match is found, control flows outward through `chat_bridge.py` to target cloud LLM APIs (Groq/Cerebras).
2. **Abstract Scraper Pipeline (Scraping)**:
   The collector subsystem is decoupled from the storage layer using `AcademicDataSource` (`collector/base.py`). Concrete classes (like `OpenMeteoSource` or potential authenticated portal scrapers) output normalized `CollectedEvent` packets. This ensures the rest of the RAG agent (`agent/`) and REST endpoints (`api/`) remain agnostic of the underlying crawler implementations.
3. **Provider Fallback & Local Optimization (NoNail)**:
   In Python v1, rate-limiting or API context failures seamlessly cascade through a specified fallback chain (`Gemini` -> `Anthropic` -> `OpenAI` -> `Groq`). Cache stores share a single SQLite database to prevent redundant API queries. Performance-critical parts (matching paths) dynamically bind to the C++ native extension `_fastcore` while lazily importing heavy libraries (MCP SDK, WhatsApp/Telegram/Discord) on demand, remaining lightweight for device runtime. In C++ v2, absolute dependency minimization allows the build to run inside a ~3MB footprint suitable for OpenWrt.
