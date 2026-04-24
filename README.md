# 🎧 Realtime Chat Application

A real-time chat application built with **WebSockets**, designed for fast, reliable, and interactive communication.  
This project supports **text messaging, voice communication**, and advanced chat features like **replying and forwarding messages** — all in real time.

The main goal of this project was to build a clean, scalable backend architecture for realtime communication while keeping the system responsive and easy to extend.

---

## ✨ Features
- 💬 Realtime text messaging using **WebSockets**
- 🎤 Live voice communication
- ↩️ Reply to messages
- 📤 Forward messages
- ⚡ Low-latency, event-driven communication
- 🔐 Secure and structured message handling
- 🧱 Clean and maintainable backend architecture

---

## 🛠 Tech Stack
- **Python**
- **Django / Django REST Framework**
- **WebSockets**
- **Redis** (message broker / pub-sub)
- **JWT Authentication**
- **Docker**
- **PostgreSQL**
- **Linux-based deployment**

---

## 🧠 How It Works (High-Level)
- WebSocket connections are established for each active user
- Messages are broadcasted in real time using an event-driven architecture
- Voice data is streamed live over persistent WebSocket connections
- Reply and forward actions keep references to original messages
- Redis is used for handling realtime events and scalability

---

## 🚀 Why This Project?
This project was built to explore and implement **real-world realtime communication challenges**, such as:
- Handling concurrent WebSocket connections
- Managing message states in realtime
- Designing scalable chat architectures
- Supporting voice data alongside text messages

It reflects how realtime systems are actually built in production environments.

---

## 🧪 Possible Improvements
- Message read receipts
- Typing indicators
- Group voice chat
- Media file support
- Horizontal scaling with multiple workers

---

## 👩‍💻 Author
**Melika Tavakoli**  
Backend Developer  
Focused on realtime systems, clean architecture, and scalable backend solutions.

---

## 📄 License
This project is open for learning and demonstration purposes.
