
## 📖 Deep Description

**TeleBot** is a fully-featured, multi-tenant Software-as-a-Service (SaaS) platform built with Django. Its primary mission is to empower business owners—such as retailers, clinics, specific service providers, or aggregators—to automate their customer interactions through intelligent, highly customizable Telegram bots.

Instead of paying for expensive bespoke app development, businesses can register a **Workspace** on TeleBot and instantly deploy their own custom bot. The system provides an entire ecosystem directly inside Telegram, meaning end-users do not need to download additional apps or visit external websites.

### Core Capabilities:

- **Intelligent Customer Support:** Create infinite-depth hierarchical categories and dynamic FAQs to answer customer questions 24/7.
- **E-Commerce & Inventory Management:** Built-in tools allow businesses to manage product catalogs (with descriptions, prices, and stock limits), track price histories, and handle customer orders directly within the bot.
- **AI-Powered Responses:** Seamless integration with Large Language Models (LLMs) like OpenAI and Ollama. TeleBot uses vector embeddings to ground the AI's knowledge in the business's specific documents, ensuring accurate, highly context-aware automated support.
- **Subscription Engine:** A scalable SaaS billing and access system featuring tiered plans (Free, 7-Day Trial, Pro, Max) governed by secure cryptographic activation codes.

---

## 🏗️ Project Architecture (Django Apps)

The system is built on a domain-driven micro-app architecture:

1. **`core`**: Foundational models (`Workspace`, `TelegramUser`, `PlanActivationCode`, `AuditLog`). This forms the base multi-tenant architecture.
2. **`ecom`**: The E-commerce engine. Manages product/service catalogs (`Medicine`), tracks inventory (`InventoryTransaction`), logs price changes (`PriceHistory`), and stores customer `Order`s.
3. **`bot_app`**: The Telegram brain. Contains webhook handlers, `BotSettings`, `FAQ` hierarchies, and navigation logic that dynamically renders inline and reply keyboards.
4. **`ai_service`**: The AI integration layer. Manages `AIModel` configs, parses `AIDocument`s into `AIEmbedding` vectors, and handles request/response/moderation logging.
5. **`admin_app`**: Global System Administration dashboard to monitor overall platform health, view active bots/users, and dispatch global notifications.
6. **`pharmacy_app`**: The Workspace/Owner Dashboard. Provides the UI for business owners to manage their bot settings, products, FAQs, and subscription plans (uses HTMX + Vanilla JS).
7. **`home_app`**: The public-facing landing and marketing page.

---

## 📂 Root Directory Structure

Below is the high-level outline of the core components in the project repository:

```text
/
├── admin_app/                   # System Administrator dashboard & logic
├── ai_service/                  # AI LLM integrations & Vector Knowledge Base
├── bot_app/                     # Core Telegram logic, Webhooks, FAQ schemas
│   ├── telegram/
│   │   ├── handlers/            # Message, callback, and category event handlers
│   │   └── utils/               # Keyboard generation & bot API loaders
├── bot_management_system/       # Main Django configuration & settings (WSGI/ASGI)
├── core/                        # Foundational models (Tenants, Users, Subscriptions)
├── ecom/                        # E-commerce, Inventory, and Order management
├── home_app/                    # Landing page app
├── pharmacy_app/                # Business Owner Dashboard UI/UX
├── .ebextensions/               # AWS Elastic Beanstalk configurations
├── .elasticbeanstalk/           # AWS EB deployment metadata
└── manage.py                    # Django project management script
```

_(Note: Various root Markdown files include specific deployment, environment, and architecture documentation tailored to different lifecycle steps, such as AWS deployment, S3 setup, and SSH migrations)._

---

## 🛠️ Technology Stack

- **Backend:** Python (Django 5.2.6)
- **Bot Engine:** `python-telegram-bot` (Webhook based)
- **Database:** MySQL on AWS RDS (Production) / SQLite (Local)
- **Frontend:** Vanilla JavaScript, HTMX, AJAX, Custom CSS
- **Authentication:** Django Auth + Django Allauth (Google OAuth)
- **Deployment:** AWS Elastic Beanstalk, AWS S3 (Static & Media files)

---

## 🚀 Setup & Installation

### Local Development

1. **Clone the repository and install dependencies:**

   ```bash
   python -m venv env
   source env/bin/activate  # Or `env\Scripts\activate` on Windows
   pip install -r requirements.txt
   ```

2. **Configure Environment Variables:**
   Create a `.env` file in the root based on `.env.example`. Ensure you set your database details, `SECRET_KEY`, and Telegram Bot Token if testing webhooks locally (we recommend using ngrok).

3. **Run Migrations & Start Server:**
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   python manage.py createsu  # Create a superuser
   python manage.py runserver
   ```

### AWS Elastic Beanstalk Deployment

The project includes `.ebextensions` and PowerShell scripts (`deploy_to_eb.ps1`) for streamlined deployment to AWS EB. Refer to `AWS_explain.md` and `DEPLOYMENT.md` in the root directory for in-depth cloud setup instructions, including tying in RDS and S3.

---

## 📜 License

_Proprietary - Do not distribute without permission._

--------
# telegram-bot-system
A fully automated Telegram bot system backed by a highly optimized relational database, deployed securely on AWS.

# 🤖 Telegram Bot Automation System (Django)

## 📝 Overview
A robust, fully automated Telegram bot system engineered to streamline workflows, handle concurrent user interactions, and manage data efficiently. Built on the **Django** framework, the project is currently deployed in a live production environment on **AWS**, demonstrating practical experience in backend development, cloud deployment, and system maintenance.

## 🚀 Tech Stack
* **Framework:** Django (Python)
* **Database:** Relational Database leveraging Django ORM
* **Cloud Infrastructure:** Amazon Web Services (AWS)
* **Security:** Environment Variables (`.env`) for secure credential management

## ⚙️ Key Features
* **Live Cloud Deployment:** Hosted securely on AWS, ensuring high availability and reliable uptime.
* **Django ORM Integration:** Utilizing Django's powerful Object-Relational Mapping for optimized database queries and secure data handling.
* **Webhook / Polling Architecture:** Designed to efficiently process incoming Telegram API updates.
* **Production-Grade Security:** Strict separation of codebase and server secrets using `.gitignore` and `.env` to protect AWS keys, Database credentials, and Bot Tokens.

## 🛠️ Local Setup & Execution

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/munirabualrrijal28/telegram-bot-system.git](https://github.com/munirabualrrijal28/telegram-bot-system.git)
   
2. **Navigate to the directory:**
   ```bash
   cd telegram-bot-system

``
3. **Environment Setup:**
* Create a .env file in the root directory.
* Add your credentials:
   ```bash
   SECRET_KEY=your_django_secret_key
   DEBUG=True
   BOT_TOKEN=your_telegram_bot_token
   DB_NAME=your_db_name
   DB_USER=your_db_user
   DB_PASS=your_db_password

``
* 4.Install dependencies :
   ```bash
   pip install -r requirements.txt
   

``
* 5.Apply Database Migration:
   ```bash
   python manage.py migrate

* 6.Run the Django Development Server:
  ```bash
   python manage.py runserver
  
 Note: The .env file containing live AWS, Database, and Telegram API credentials is purposefully excluded from this repository for security best practices.
