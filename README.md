# Connect Four

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
  - [Using Docker](#using-docker)
- [⚙️ Environment Variables](#%EF%B8%8F-environment-variables)
- [🛠️ Commands](#%EF%B8%8F-commands)
  - [Run Message Consumer](#run-message-consumer)
  - [Run Task Scheduler](#run-task-scheduler)
  - [Run Task Executor](#run-task-executor)
  - [Create a New Game](#create-a-new-game)
  - [End a Game](#end-a-game)

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
   pip install build
   python3 -m build --wheel
   pip install ./dist/connect_four*.whl
   ```

### Using uv

1. Create and activate a virtual environment:
   ```bash
   uv venv --python 3.12
   source ./.venv/bin/activate
   ```

2. Install dependencies:

   **For development**
   ```bash
   uv sync --all-extras --frozen
   ```

   **For production**
   ```bash
   uv build --wheel
   uv pip install ./dist/connect_four*.whl
   ```

### Using Docker

1. Build Docker image:

   ```bash
   docker build -t connect_four:latest .
   ```

---

## ⚙️ Environment Variables

Configure the following environment variables before running the application:

<div align="center">

| Variable                     | Required            | Description                              |
|------------------------------|---------------------|------------------------------------------|
| `LOGGING_LEVEL`              | Yes                 | Level for [GLogger](https://github.com/gaems12/g-logger)                      |
| `REDIS_URL`                  | Yes                 | URL for the Redis instance.              |
| `NATS_URL`                   | Yes                 | URL for the NATS server.                 |
| `CENTRIFUGO_URL`             | Yes                 | URL for the Centrifugo server.           |
| `CENTRIFUGO_API_KEY`         | Yes                 | API key for Centrifugo.                  |
| `GAME_MAPPER_GAME_EXPIRES_IN`| Yes                 | Game expiration time in seconds.         |
| `LOCK_EXPIRES_IN`            | Yes                 | Lock expiration time in seconds.         |
| `TEST_REDIS_URL`             | Yes(for tests)      | URL for the test Redis instance.         |

</div>

---

## 🛠️ Commands

### Run Message Consumer

Run the message consumer to process game-related events from NATS:
```bash
connect-four run-message-consumer
```

### Run Task Scheduler

Run the task scheduler:
```bash
connect-four run-task-scheduler
```

### Run Task Executor

Run the task executor for scheduled tasks:
```bash
connect-four run-task-executor
```

### Create a New Game

```bash
connect-four create-game --id <UUID> --lobby-id <UUID> --first-player-id <UUID> --second-player-id <UUID> --time-for-each-player <number_of_seconds>
```

### End a Game

```bash
connect-four end-game --id <UUID>
```

---
