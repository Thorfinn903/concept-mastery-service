# Concept Mastery Service 🧠

A FastAPI microservice that acts as the "Intelligence Layer" for an educational platform. It consumes raw student data from the Learning Events Service and calculates real-time "Mastery Scores" for different subjects.

## 🚀 Features
* **Microservice Architecture:** Designed to run alongside a separate Logging Service.
* **Mastery Calculation:** Automates the grading logic (Mastery = Successes / Total Attempts).
* **Sync & Recompute:** Includes a "Recompute" endpoint to process historical data from the logger.
* **SQLite Database:** Stores mastery scores efficiently.

## 🛠️ Tech Stack
* **Framework:** FastAPI
* **Database:** SQLite + SQLAlchemy
* **Validation:** Pydantic
* **Communication:** Python `requests` (to talk to Service 1)

## ⚡ How to Run

### Prerequisites
1. Ensure the **Learning Events Service** is running on Port 8000.
2. Python 3.10+ installed.

### Installation
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the FastAPI server:
   ```bash
   uvicorn main:app --reload --port 8001
   ```
   
### Endpoints
* `GET /mastery/{student_id}/{subject}` - Get the mastery score for a student in a subject.
* `POST /recompute` - Recompute mastery scores from historical data.
