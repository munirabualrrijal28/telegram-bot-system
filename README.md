# 🤖 TeleBot: Comprehensive Bot Management System

<div align="center">
  <h3>A multi-tenant SaaS platform for businesses to create, configure, and manage intelligent Telegram bots.</h3>
</div>

---

## 📖 About the Project

**TeleBot** is a fully-featured, multi-tenant Software-as-a-Service (SaaS) platform built to empower businesses. It bridges the gap between complex backend management systems and the simplicity of instant messaging apps.

Through TeleBot, business owners (such as retailers, service providers, or clinics) can register for an account (a **Workspace**) and instantly deploy a customized Telegram Bot. The platform handles user interactions, FAQs, file sharing, customer support, and even fully functioning e-commerce checkout flows directly inside the Telegram chat UI.

### What Problems Does It Solve?

1. **No External Apps Needed:** Customers don't need to download a new app or visit a web store; they just message the Telegram bot.
2. **Centralized Bot Management:** Business owners can configure welcome messages, deep hierarchical FAQ systems (to answer customer queries 24/7), and showcase a live product catalog without writing a single line of code.
3. **Automated AI Intelligence:** Instead of static auto-replies, business owners can attach PDF documents or textual knowledge bases to the system. TeleBot uses LLMs to provide intelligent support directly to customers based on the provided business data.

---

## 🛠️ Frameworks & Technology Stack

The project relies on a carefully curated, modern tech stack optimized for speed, scalability, and ease of deployment:

### Backend

- **Django (5.1.4):** The core foundation. Provides the ORM, administration interface, and secure routing.
- **Python-Telegram-Bot:** Operates the Telegram API interaction via Webhooks (instead of long-polling), enabling scalable response handling.
- **Django Allauth:** Powers the authentication system, integrating Google OAuth alongside traditional Email/Password logins.
- **MySQL / SQLite:** MySQL is used for production (via AWS RDS), while SQLite is supported for fast local development.

### Frontend

- **HTMX:** Used extensively in the Business Owner Dashboard (`pharmacy_app/`) to provide Single Page Application (SPA)-like speed without writing complex React/Vue frontend code. It swaps HTML fragments dynamically over the standard Django views.
- **Vanilla JavaScript & AJAX:** Used for complex DOM manipulations (like dragging and dropping categories or handling dynamic file uploads).
- **Bootstrap-Inspired Custom CSS:** Provides a clean, responsive, and mobile-friendly UI layout for the owner dashboards.

### Infrastructure & Operations

- **AWS Elastic Beanstalk (EB):** Hosts the computational web application.
- **AWS RDS:** Hosts the managed relational MySQL database.
- **AWS S3:** Serves all static and media files securely (via `django-storages` and `boto3`).
- **Gunicorn & Whitenoise:** Gunicorn runs the WSGI server; Whitenoise serves statics effectively before reaching S3 in caching pipelines.

---

## 🏗️ Core Architecture (Django Apps)

The system uses a domain-driven micro-app structure:

- **`core`**: Base architecture (`Workspace`, `TelegramUser`, `PlanActivationCode`).
- **`ecom`**: The E-commerce engine for products (`Medicine`), orders, and inventory.
- **`bot_app`**: Webhook receivers and Telegram bot handlers for responding to messages.
- **`ai_service`**: AI configuration for LLM connections, embeddings, and response moderation.
- **`admin_app`**: Global System Admin dashboard to track overall platform analytics.
- **`pharmacy_app`**: The primary UI interface (Dashboard) for business owners.
- **`home_app`**: The public-facing landing and marketing page.
- **`management/commands`**: Contains custom commands for migrations, superuser creation (`createsu`), and fixing database syncs.

---

## � Full Project Directory Structure

Below is the comprehensive architectural outline of the project repository, detailing the key files, modules, and `.md` lifecycle resources:

```text
/
├── .ebextensions/               # AWS Elastic Beanstalk configuration files
│   ├── 01_django.config         # Main Django EB config
│   ├── 01_django_minimal.config # Alternative minimal config for debugging
│   └── 02_python.config         # Additional python tweaks mapping WSGI & statics
├── .elasticbeanstalk/           # Auto-generated EB deployment logs and metadata
├── admin_app/                   # System Administrator Dashboard
│   ├── templates/admin_app/     # HTML templates for admin ui (dashboard, user manage, broadcasts)
│   ├── management/commands/     # Custom seed commands for bootstrapping system admins
│   ├── models.py                # Admin models (Global SystemNotification)
│   ├── views.py                 # Views handling system-level functions and overviews
│   └── urls.py                  # Admin route definitions
├── ai_service/                  # LLM integrations and Vector Knowledge Base
│   ├── models.py                # AIModels, AIPromptTemplates, AIDocuments, and Embeddings
│   └── views.py                 # Request handlers mapping directly to OpenAI/Ollama APIs
├── bot_app/                     # Core Telegram logic and webhook ingestion
│   ├── telegram/
│   │   ├── handlers/            # Event-specific logic (message, callback, category, faq)
│   │   ├── utils/               # Keyboard parsers, DB API abstractions
│   │   ├── constants.py         # Static bot configurations
│   │   └── views.py             # Primary Telegram webhook entrypoint
│   ├── templates/bot_app/       # Components and UI partials for the mini-app and dashboard
│   ├── middleware.py            # Middleware for parsing Telegram context
│   └── models.py                # BotSettings, FAQCategory, FAQ, BotPage, GroupItem
├── bot_management_system/       # Django Project Root (Configuration)
│   ├── settings.py              # Contains AWS S3 config, DB conditionals, Whitenoise config
│   ├── urls.py                  # Main routing dispatcher across all apps
│   └── wsgi.py                  # WSGI config for Gunicorn deployment
├── core/                        # Foundational Auth & Tenant Models
│   ├── management/commands/     # Contains createsu.py for superuser bootstrapping
│   └── models.py                # UUIDModel, Workspace, TelegramUser, AuditLog, PlanActivationCode
├── ecom/                        # Built-in E-commerce engine
│   └── models.py                # Category, Medicines (Products), Order, OrderItem, InventoryTransaction
├── home_app/                    # Landing page app
│   ├── templates/home_app/      # Landing page HTML (SaaS marketing)
│   └── urls.py                  # Public routes
├── pharmacy_app/                # Business Owner Dashboard UI/UX
│   ├── templates/owner/         # Rich owner UI templates (auth, dashboard, products/medicines lists)
│   ├── models.py                # UI related owner models
│   ├── forms.py                 # Form validation for bot settings and product entries
│   ├── signals.py               # Post-save/delete signal handlers for automated data integrity
│   └── views.py                 # Dashboard views utilizing dynamic HTMX & AJAX calls
├── manage.py                    # Standard Django project management script
├── Procfile                     # Deployment process definitions (often used for VPS/Cloud)
├── requirements.txt             # Production python packages (verified versions)
├── requirements-minimal.txt     # Fallback minimal dependencies for AWS bootstrap debugging
├── .env.example                 # Environment variables blueprint
└── Root System Documents (*.md) # Lifecycle guides, scaling protocols, and issue logs
    ├── AWS_explain.md           # Deep-dive architectural explanation of the AWS stack
    ├── Bot_models.md / TeleBot.md # Internal model schemas and entity relationship guides
    ├── CHECK_ENVIRONMENT.md     # Debugging protocols for AWS EB container health checks
    ├── DEPLOYMENT.md            # Master deployment instruction workflow
    ├── SSH_SETUP_CONFIRM.md     # Walkthroughs for fixing migration sync bugs on AWS RDS
    └── TROUBLESHOOTING.md       # Master troubleshooting log for deployment/migration errors
```

---

## �🚀 How to Run the Project

### Phase 1: Local Development Setup

**1. Clone and Prepare the Virtual Environment**

```bash
# Clone the repository and enter the directory
git clone <your-repo-url>
cd bot_management_system

# Create and activate a Python virtual environment
python -m venv env

# On Windows:
env\Scripts\activate
# On Mac/Linux:
source env/bin/activate
```

**2. Install Dependencies**

```bash
pip install -r requirements.txt
```

_(Note: The main `requirements.txt` contains dependencies for production. In local development on Windows, SQLite will be the default database, bypassing the need for native MySQL compilation if issues arise)._

**3. Configure Environment Variables**
Create a `.env` file in the root directory. Minimally, for local development using SQLite, you will need:

```ini
DEBUG=True
SECRET_KEY="your-local-secret-key-change-this"

# (Optional for general dev) You must supply a valid Telegram Bot Token generated from @BotFather to test bot connectivity
TELEGRAM_BOT_TOKEN="123456789:YOUR_TELEGRAM_TOKEN"
```

**4. Run Database Migrations**
TeleBot uses complex schemas spanning 7 apps. Migrate the local SQLite database:

```bash
python manage.py makemigrations
python manage.py migrate
```

**5. Create a Superuser and Start the App**

```bash
# Create an admin account to configure the system
python manage.py createsu
# (Alternatively, run: python manage.py createsuperuser)

# Start the Django development server
python manage.py runserver
```

**6. Local Webhook Testing (Optional but Recommended)**
Since the bot operates on webhooks instead of local long-polling, Telegram needs a public HTTPS URL to send messages to.

1. Download and run `ngrok http 8000`.
2. Grab the `https` link generated by ngrok.
3. Update your bot's webhook URL dynamically with the provided token integration.

---

### Phase 2: Production / Deployment Setup (AWS Elastic Beanstalk)

The project is natively configured for **AWS Elastic Beanstalk (EB)** with an **RDS MySQL Database**.

**1. EB CLI Setup**
Initialize the AWS EB CLI in the root directory:

```bash
eb init
```

_Select your region, Python environment (Python 3.12 is recommended), and confirm your EC2 keypairs._

**2. Configure Production Database & Environment Variables**
In the AWS Console for Elastic Beanstalk (or via `eb setenv`), you must establish the production variables to connect to AWS RDS and S3:

```bash
eb setenv DEBUG=False \
          SECRET_KEY="PRODUCTION_SECRET" \
          DB_ENGINE="django.db.backends.mysql" \
          DB_HOST="your-rds-endpoint" \
          DB_NAME="bot_management_db" \
          DB_USER="admin" \
          DB_PASSWORD="your-strong-password" \
          DB_PORT="3306" \
          USE_S3=True \
          AWS_ACCESS_KEY_ID="xxx" \
          AWS_SECRET_ACCESS_KEY="xxx" \
          AWS_STORAGE_BUCKET_NAME="bucket-name"
```

**3. Deploy the Code**
We rely on `.ebextensions/` config files to handle Linux dependencies, Python package execution, and automatic Django `collectstatic` routing.

```bash
eb deploy
```

**4. Migrating & Troubleshooting**
If automatic migrations fail, you can SSH into your EC2 instance (or use the built-in AWS Console tools) to manually migrate:

```bash
python manage.py migrate
```

_(The repository also includes several `.md` guides like `CHECK_ENVIRONMENT.md` and `TROUBLESHOOTING.md` tailored for diagnosing AWS issues)._

---

## 📜 License

_Proprietary - Do not distribute without permission._


-----------------------------------------------------------
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
