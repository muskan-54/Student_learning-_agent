# 🎓 Student Learning Agent – Capstone Project

A smart, multi-agent student assistant built using **Google ADK**, **Gemini 2.5 Flash**, and custom tools.
This project helps students learn better with planning, motivation, coding help, and personalized study routines.

---

## 🚀 Features

### 🧠 **1. Task Planner Agent**

Creates a personalized daily or weekly study plan based on your goals and availability.

### 💻 **2. Code Helper Agent**

Explains code, fixes errors, and generates examples to support learning programming.

### 💬 **3. Motivational Quotes Tool**

Uses an online API to deliver fresh motivational messages during study sessions.

### 📚 **4. Root Agent**

The main controller that routes tasks to the correct sub-agent.

---

## 🔧 Tech Stack

* **Google ADK**
* **Gemini 2.5 Flash Model**
* **Python 3.11+**
* **Custom Tools (Motivation API)**
* **Constitution-based multi-agent design**

---

## 📁 Project Structure

```
student_learning_agent/
│── my_agent/
│   │── agent.py
│   │── __init__.py
│── constitution.json
│── requirements.txt
│── README.md
```

---

## ▶️ How to Run

1. Create a virtual environment:

   ```
   python -m venv .venv
   ```

2. Activate it:
   **Windows:**

   ```
   .venv\Scripts\activate
   ```

3. Install packages:

   ```
   pip install -r requirements.txt
   ```

4. Run the agent:

   ```
   adk run my_agent
   ```

---

## 📦 Packaging for Submission

Generate the submission zip:

```
adk package my_agent
```

This creates:

```
my_agent.zip
```

Submit this ZIP file.

---

## 🛠 Tools Overview

### **Motivation Tool**

Fetches motivational quotes using:

```
https://motivational-api.vercel.app/motivational
```

Helps students stay focused through positive reinforcement.

---

## 🎯 Use Cases

* Study planning
* Coding error debugging
* Daily motivation
* Personalized learning companion

---

## 🌟 Author

**Muskan Fatima**
Frontend Developer | AI & Web Enthusiast

