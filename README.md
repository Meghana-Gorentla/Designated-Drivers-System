
# Designated Drivers System Backend

A backend system for a designated driver service that allows users to request drivers, track rides, make payments, and manage feedback. Built with **FastAPI**, using **Docker** and **Kubernetes** for containerization and deployment.

---

## Table of Contents

* [Features](#features)
* [Tech Stack](#tech-stack)
* [Architecture](#architecture)
* [Setup & Installation](#setup--installation)
* [Docker & Kubernetes](#docker--kubernetes)
* [API Endpoints](#api-endpoints)
* [Contributing](#contributing)
* [License](#license)

---

## Features

* User authentication and role-based access (Driver / User / Admin)
* Book, track, and manage rides
* Payment processing and earnings calculation
* Submit complaints and feedback
* Emergency services integration
* Dockerized backend services
* Kubernetes deployment (local pod setup)

---

## Tech Stack

* **Backend:** FastAPI
* **Database:** SQLAlchemy (ORM)
* **Containerization:** Docker, Docker Compose
* **Orchestration:** Kubernetes (local pod)
* **Python Version:** 3.13
* **IDE:** PyCharm

---

## Architecture

The application follows a modular FastAPI architecture:

```
designated driver system/
│
├── .venv/ # Virtual environment
├── alembic/ # Alembic migrations
├── app/
│ ├── core/ # Core utilities
│ ├── models/ # Database models
│ ├── routers/ # FastAPI route handlers
│ └── schemas/ # Pydantic schemas
│
├── dependencies/ # Authentication & dependency files
├── k8s/ # Kubernetes configuration files
├── .env
├── alembic.ini
├── docker-compose.yml
├── Dockerfile
├── requirements.txt

```

* **Docker Compose:** Runs 2 containers – one for the backend API and one for the database
* **Kubernetes:** Local single-pod deployment for testing and orchestration

---

## Setup & Installation

1. Clone the repository:

```bash
git clone https://github.com/Meghana-Gorentla/Designated-Drivers-System.git
cd Designated-Drivers-System
```

2. Create a virtual environment:

```bash
python -m venv .venv
source .venv/bin/activate   # Linux/Mac
.venv\Scripts\activate      # Windows
```

3. Install dependencies:

```bash
pip install -r requirements.txt
```

4. Run the backend:

```bash
uvicorn app.main:app --reload
```

---

## Docker & Kubernetes

### Docker

1. Build and run containers using Docker Compose:

```bash
docker-compose up --build
```

2. Services:

* **backend:** FastAPI API
* **db:** PostgreSQL database

### Kubernetes (Local)

1. Apply the deployment YAML:

```bash
kubectl apply -f k8s/deployment.yaml
```

2. Check pod status:

```bash
kubectl get pods
```

3. Access the API via `localhost:<port>`


## API Endpoints (Example)

* `/auth/register` – Register a new user
* `/auth/login` – Login and get access token
* `/ride/request` – Book a ride
* `/ride/status` – Track ride status
* `/driver/{driver_id}/earnings` – Get driver earnings
* `/feedback/submit` – Submit feedback


