# Educational Microservices Platform 🎓

A scalable backend system built with **FastAPI** that tracks student activities and uses intelligent processing to calculate real-time subject mastery.

The system is composed of two decoupled microservices:
1.  **The Logger (Service 1):** Records raw data.
2.  **The Brain (Service 2):** Analyzes data and computes scores.

---

## 🏗️ System Architecture



| Service | Port | Role | Description |
| :--- | :--- | :--- | :--- |
| **Learning Events Service** | `8000` | **The Logger** 📔 | Captures raw events (video views, quiz attempts) and stores them permanently. |
| **Concept Mastery Service** | `8001` | **The Brain** 🧠 | Consumes data from the Logger to calculate 0-100% mastery scores for every topic. |

---

## 🚀 Service 1: Learning Events Service
*Located in: `/learning_events_service`*

A high-performance API designed to ingest student activity data. It acts as the "Source of Truth" for all user actions.

### Key Features
* **Event Logging:** Tracks specific actions like `quiz_attempt`, `video_watched`, or `assignment_submitted`.
* **Data Integrity:** Automatic UUID generation and UTC timestamps for every event.
* **History Retrieval:** Provides a full timeline of events for any user.
* **Interactive Docs:** Swagger UI available at `http://127.0.0.1:8000/docs`.

### 🔌 API Endpoints (Port 8000)
* `POST /events/` - Log a new learning event.
* `GET /events/{user_id}` - Get full history for a student.
* `GET /health` - Service health check.

---

## 🧠 Service 2: Concept Mastery Service
*Located in: `/concept_mastery_service`*

The intelligence layer. It talks to Service 1 to "learn" what the student has done and applies grading algorithms to determine proficiency.

### Key Features
* **Mastery Calculation:** Automates grading logic (e.g., *Mastery = Successful Quizzes / Total Attempts*).
* **Sync & Recompute:** A powerful "Recompute" engine that pulls historical data from Service 1 to fix or update scores.
* **Batch Processing:** Optimized database commits for processing large histories efficiently.
* **Fault Tolerance:** Resilient HTTP connections with retries and timeouts.

### 🔌 API Endpoints (Port 8001)
* `GET /mastery/{user_id}` - Get all subject scores for a student.
* `GET /mastery/{user_id}/{concept_id}` - Get specific score for a topic.
* `POST /mastery/recompute/{user_id}` - Trigger a sync with Service 1.

---

## 🛠️ Tech Stack
* **Language:** Python 3.10+
* **Framework:** FastAPI
* **Server:** Uvicorn
* **Database:** SQLite (Separate DBs for each service)
* **ORM:** SQLAlchemy
* **Validation:** Pydantic V2
* **Inter-Service Communication:** Python `requests` library

---

## ⚡ How to Run

Since these are microservices, they must run in **separate terminal windows** simultaneously.

### Step 1: Start the Logger (Service 1)
Open a new terminal:
```bash
cd learning_events_service
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
