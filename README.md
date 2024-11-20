# TODO
- [x] Deploy on render.com
  - [x] PostgreSQL
  - [x] API
- [ ] Improve logging and exception handling
- [ ] Implement simple AUTH
- [ ] Add more tests
- [ ] Implement tox
- [ ] Implement alembic

# Applifting API

![License](https://img.shields.io/github/license/StrawIII/applifting-api)
![Python](https://img.shields.io/badge/python-3.10%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-✔-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-✔-blue)

### 👷 **Deployed demo**: [https://applifting-api.onrender.com](https://applifting-api.onrender.com) 
🚨ATTENTION: first request might take up to a minute due to server spin up🚨

## Overview

**Applifting API** is a microservice API built using **FastAPI** and **PostgreSQL**. Designed with modern development practices, it integrates seamless containerization using Docker and adheres to clean code principles. It supports dynamic configurations with `.env` files and provides powerful database management using SQLAlchemy.

## Features

- **FastAPI** for high-performance RESTful APIs.
- **PostgreSQL** as the database backend.
- **Pydantic** for robust settings and data validation.
- Supports local development and containerized deployments.

## Prerequisites

Before running the project, ensure you have the following installed:

- [Python 3.10+](https://www.python.org/downloads/)
- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)
- [uv (native running, testing)](https://docs.astral.sh/uv/getting-started/installation/)

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/StrawIII/applifting-api.git
cd applifting-api
```

### 2. Setup Environment Variables

```bash
cp .env.example .env
```
### 3. Start the Application

#### Locally:

```bash
uv run uvicorn api.main:app --reload
```
#### With Docker Compose:

```bash
docker-compose up --build
```
#### With Docker Compose (PostgreSQL):

```bash
docker compose -f compose.dev.yaml up --build
```

## Development

### Run tests

```bash
uv run pytest
```
