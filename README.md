# Four In A Row Game

<p align="left">
   <a>
      <img src="https://img.shields.io/badge/python-3.12-blue" alt="Python version">
   </a>
   <a href="https://github.com/astral-sh/ruff">
      <img src="https://img.shields.io/badge/code_style-ruff-%236b00ff" alt="Code style">
   </a>
</p>

## 📚 Table of Contents

- [📦 Dependencies](#-dependencies)
- [🚀 Installation](#-installation)
  - [Using pip](#using-pip)
  - [Using uv](#using-uv)
- [⚙️ Environment Variables](#%EF%B8%8F-environment-variables)
- [🛠️ Commands](#%EF%B8%8F-commands)
  - [Start Web API](#start-web-api)
  - [Run Message Consumer](#run-message-consumer)
  - [Run Task Executor](#run-task-executor)
  - [Create a New Game](#create-a-new-game)

---

## 📦 Dependencies

Ensure the following services are installed and running:

- **Redis**
- **NATS**
- **Centrifugo**

---

## 🚀 Installation

### Using pip

1. Create and activate a virtual environment:
   ```bash
   python3 -m venv .venv
   source ./.venv/bin/activate
   ```

2. Install dependencies:

   **For development:**
   ```bash
   pip install -e ".[dev]"
   ```

   **For production:**
   ```bash
   pip install .
   ```

### Using uv

1. Create a virtual environment with uv:
   ```bash
   uv venv --python 3.12
   ```

2. Sync dependencies:

   **For development**
   ```bash
   uv sync --all-extras
   ```

   **For production**
   ```bash
   uv sync
   ```

---

## ⚙️ Environment Variables

Configure the following environment variables before running the application:

| Variable                     | Required            | Description                              |
|------------------------------|---------------------|------------------------------------------|
| `REDIS_URL`                  | Yes                 | URL for the Redis instance.              |
| `NATS_URL`                   | Yes                 | URL for the NATS server.                 |
| `CENTRIFUGO_URL`             | Yes                 | URL for the Centrifugo server.           |
| `CENTRIFUGO_API_KEY`         | Yes                 | API key for Centrifugo.                  |
| `GAME_MAPPER_GAME_EXPIRES_IN`| Yes                 | Game expiration time in seconds.         |
| `LOCK_EXPIRES_IN`            | Yes                 | Lock expiration time in seconds.         |
| `TEST_REDIS_URL`             | Yes(for tests)      | URL for the test Redis instance.         |

---

## 🛠️ Commands

### Start Web API

Run the web API to handle HTTP requests from Centrifugo:
```bash
four-in-a-row run-web-api
```

### Run Message Consumer

Run the message consumer to process game-related events from NATS:
```bash
four-in-a-row run-message-consumer
```

### Run Task Executor

Run the executor for scheduled tasks:
```bash
four-in-a-row run-task-executor
```

### Create a New Game

```bash
four-in-a-row create-game --id <UUID> --first-player-id <UUID> --second-player-id <UUID> --time-for-each-player <number of seconds>
```

---
