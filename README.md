# Backend (FastAPI) - Setup & Usage

This backend provides API and WebSocket endpoints for the Stream UI admin panel. It uses FastAPI, SQLAlchemy, and PostgreSQL.

---

## Prerequisites
- Python 3.10+
- pip
- PostgreSQL (running and accessible)

---

## 1. Installation

1. **Clone the repository and navigate to the backend folder:**
   ```bash
   cd backend
   ```
2. **Create and activate a virtual environment:**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```
3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

---

## 2. Database Setup

1. **Start PostgreSQL** and create a database (e.g., `streamdb`).
2. **Set the database URL** as an environment variable:
   ```bash
   export DATABASE_URL=postgresql://user:password@localhost:5432/streamdb
   ```
   Or create a `.env` file in the backend directory with:
   ```env
   DATABASE_URL=postgresql://user:password@localhost:5432/streamdb
   ```

---

## 3. Running the Server

Start the FastAPI server with Uvicorn:
```bash
uvicorn app.main:app --reload
```
- The API will be available at: http://localhost:8000
- WebSocket endpoint: ws://localhost:8000/ws/chat

---

## 4. Useful Commands
- **Run tests:**
  ```bash
  pytest
  ```
- **Format code (optional):**
  ```bash
  black app/
  ```

---

## 5. Project Structure
- `app/` - Main FastAPI app, services, models, and utilities
- `schemas/` - Pydantic schemas (if used)
- `tests/` - Backend tests
- `venv/` - Virtual environment (not tracked by git)

---

## 6. Notes
- Ensure the backend is running before using the frontend UI.
- Update the `DATABASE_URL` as needed for your environment. 