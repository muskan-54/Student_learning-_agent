# 🎓 Student Learning Agent – AI-Powered Multi-Agent Study Assistant

A smart, multi-agent learning assistant built using **Google ADK**, **Gemini 2.5 Flash**, **FastAPI**, and a custom **frontend UI**.
Designed to help students study smarter with **daily plans, coding help, and motivation** — all in one place.

---

## 🌟 Features

### 🧠 **Task Planner Agent**

Creates simple and personalized **daily or weekly study plans** based on goals and time availability.

### 💻 **Code Helper Agent**

Explains code, fixes errors, and generates clean examples for beginner programmers.

### 💬 **Motivation Tool**

Fetches fresh motivational quotes from an external API to keep students focused and energized.

### 🎯 **Root Agent (Controller)**

Decides which sub-agent should answer based on the user prompt.

### 🖥️ **Interactive Frontend (index.html)**

A smooth, modern chat UI with:

* Chat bubbles
* Timestamps
* Loading animation
* Fully responsive design
* FastAPI backend integration

---

## 🧩 Architecture Overview

```
Frontend (index.html)
        ↓
FastAPI Backend (chat endpoint)
        ↓
Root Agent – Google ADK
 ├── Task Planner Agent
 ├── Code Helper Agent
 └── Motivation Tool (API)
```

Modular, extensible, and easy to maintain.

---

## 📁 Project Structure

```
student_learning_agent/
│── my_agent/
│   │── agent.py
│   │── __init__.py
│── index.html
│── constitution.json
│── requirements.txt
│── README.md
```

---

## 🚀 Getting Started

### 1️⃣ Create a virtual environment

```bash
python -m venv .venv
```

### 2️⃣ Activate it

**Windows:**

```bash
.venv\Scripts\activate
```

### 3️⃣ Install dependencies

```bash
pip install -r requirements.txt
```

### 4️⃣ Run the ADK Agent

```bash
adk run my_agent
```

### 5️⃣ Start FastAPI Backend

```bash
uvicorn api_server:app --reload
```

### 6️⃣ Open Frontend

Just open:

```
index.html
```

---

## 🔌 Motivation Tool (API)

The Motivation Agent fetches quotes using:

```
https://motivational-api.vercel.app/motivational
```

Used for quick mood boost during study sessions.

## 🌱 Future Improvements

If more time was available, I’d extend the system with:

* Voice interaction (speech-to-text + TTS)
* Flashcards + spaced repetition
* Progress dashboard
* PDF summarization agent
* Mobile app version
* Study streak tracking
* Notebook-style markdown support

---

## 👩‍💻 Author

**Muskan Fatima**
Frontend Developer | AI & Web Enthusiast


