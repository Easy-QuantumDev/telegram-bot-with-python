# 🤖 Telegram Bots Collection

A collection of **Telegram Bot projects built with Python** using the **TeleBot (pyTelegramBotAPI)** library.

This repository contains practical projects created to improve my skills in Telegram Bot development, Python, APIs, databases, and bot architecture.

---

## 🚀 Projects

### 🎙️ 1. Text-to-Speech Bot

A Telegram bot that converts user text into speech and sends the generated audio back to the user.

**Features:**

* `/start` command
* `/voice` command
* Text-to-Speech conversion
* English voice generation
* Sending generated audio to Telegram

**Technologies:**

* Python
* TeleBot
* gTTS

---

### 👥 2. Group Management Bot

A Telegram bot designed to help manage Telegram groups.

**Planned Features:**

* Admin commands
* User management
* Message moderation
* Welcome messages
* Custom commands
* Inline keyboards

**Technologies:**

* Python
* TeleBot

---

### 💰 3. Currency & Price Bot

A Telegram bot that retrieves financial information from APIs and displays updated prices.

**Planned Features:**

* Currency prices
* Gold prices
* Cryptocurrency prices
* REST API integration
* Inline keyboards
* Automatic updates

**Technologies:**

* Python
* TeleBot
* Requests
* REST API
* JSON

---

### 🛒 4. Telegram Store Bot

A Telegram-based shopping bot for displaying products and managing orders.

**Planned Features:**

* Product categories
* Product details
* Inline keyboards
* Shopping cart
* User registration
* Order management
* Database integration

**Technologies:**

* Python
* TeleBot
* SQLite
* SQL

---

### 📊 5. Telegram Statistics Bot

A bot for collecting and displaying user or group statistics.

**Planned Features:**

* User statistics
* Message statistics
* Admin reports
* Database storage
* Data analysis

**Technologies:**

* Python
* TeleBot
* SQLite

---

## 🧠 Topics Covered

Throughout these projects, I will practice:

* Telegram Bot API
* TeleBot
* Message Handlers
* Command Handlers
* Callback Queries
* Inline Keyboards
* Reply Keyboards
* `register_next_step_handler`
* User input handling
* File handling
* Sending images and files
* Sending voice messages
* Text-to-Speech
* REST APIs
* JSON
* Database integration
* SQLite
* CRUD operations
* Error handling
* Logging
* Environment Variables
* `.env`
* Bot security
* Polling
* Webhooks
* Docker
* Deployment

---

## 🛠️ Technologies

| Technology       | Usage                     |
| ---------------- | ------------------------- |
| 🐍 Python        | Main programming language |
| 🤖 TeleBot       | Telegram Bot development  |
| 🔊 gTTS          | Text-to-Speech            |
| 🌐 Requests      | API requests              |
| 🗄️ SQLite       | Database                  |
| 🐳 Docker        | Containerization          |
| 🔐 python-dotenv | Environment variables     |
| 📦 Git           | Version control           |
| 🐙 GitHub        | Project hosting           |

---

## 📁 Repository Structure

```text
telegram-bots/
│
├── text-to-speech-bot/
│   ├── main.py
│   ├── requirements.txt
│   └── README.md
│
├── group-management-bot/
│   ├── main.py
│   ├── requirements.txt
│   └── README.md
│
├── currency-price-bot/
│   ├── main.py
│   ├── requirements.txt
│   └── README.md
│
├── telegram-store-bot/
│   ├── main.py
│   ├── database.py
│   ├── requirements.txt
│   └── README.md
│
└── statistics-bot/
    ├── main.py
    ├── database.py
    ├── requirements.txt
    └── README.md
```

---

## ⚙️ Installation

Clone the repository:

```bash
git clone https://github.com/YOUR_USERNAME/telegram-bots.git
```

Go to the project directory:

```bash
cd telegram-bots
```

Create a virtual environment:

```bash
python -m venv venv
```

Activate the virtual environment on Windows:

```bash
venv\Scripts\activate
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

For security reasons, bot tokens and API keys should never be stored directly in the source code.

Create a `.env` file:

```env
BOT_TOKEN=your_bot_token
API_KEY=your_api_key
```

Load the variables in Python:

```python
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")
```

> ⚠️ Never upload your Telegram Bot Token or API keys to GitHub.

---

## ▶️ Running a Bot

After installing the dependencies and configuring the environment variables:

```bash
python main.py
```

The bot will start using Telegram polling.

---

## 📚 Learning Path

The projects in this repository follow a progressive learning path:

```text
Python
   ↓
TeleBot Basics
   ↓
Handlers
   ↓
Keyboards & Callbacks
   ↓
User State Management
   ↓
APIs
   ↓
Databases
   ↓
Authentication & Security
   ↓
Advanced Bot Architecture
   ↓
Docker
   ↓
Deployment
```

---

## 📈 Roadmap

* [x] Learn Telegram Bot basics
* [x] Learn TeleBot
* [x] Create Text-to-Speech Bot
* [ ] Build Group Management Bot
* [ ] Build Currency & Price Bot
* [ ] Build Telegram Store Bot
* [ ] Build Statistics Bot
* [ ] Learn Database Integration
* [ ] Learn REST APIs
* [ ] Learn Webhooks
* [ ] Improve Bot Security
* [ ] Dockerize Telegram Bots
* [ ] Deploy Bots on a Server

---

## 🎯 Goal

The main goal of this repository is to build practical Telegram Bot projects, strengthen Python programming skills, and create a collection of real-world projects for my **GitHub portfolio**.

New projects, features, and advanced concepts will be added over time.

---

## 👨‍💻 Author

**YOUR NAME**

⭐ If you find this repository useful, consider giving it a star!
