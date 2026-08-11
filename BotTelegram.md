---
### 🧠 **Project Name:** Django Pharmacy Bot System

### 💬 **Brief Description:**

A smart **Telegram-based pharmacy assistant** built with **Django** and **Python Telegram Bot API** that connects customers, pharmacies, and administrators through a unified automated system.
The bot allows users to browse medicines, view categories, place orders, manage prescriptions, and communicate directly with the pharmacy — all inside Telegram.
---

### ⚙️ **Key Features:**

- **Interactive Telegram Interface:** Dynamic keyboards, category lists, and inline buttons for easy navigation.
- **Order Management:** Customers can order medicines or upload prescriptions directly.
- **Smart Search & Filtering:** Find medicines by name, type, or category.
- **Admin Dashboard (Django):** Manage products, track orders, and send broadcast messages.
- **Customer Support Automation:** Provides automated responses and redirects complex queries to human support.
- **Notification System:** Real-time Telegram updates for new orders, confirmations, and delivery status.
- **Free Trial System:** Automatic 7-day free trial for new users with full feature access.
- **Modular Architecture:** Organized structure separating handlers, keyboards, and utilities for scalable maintenance.

---

### 🧩 **Tech Stack:**

- **Backend:** Django Framework (Python)
- **Bot Framework:** python-telegram-bot
- **Database:** PostgreSQL / SQLite
- **Integration:** Telegram Webhook (with token verification)
- **Optional Frontend:** Django Admin or custom dashboard for pharmacies

---

### 🎯 **Vision:**

To create a **fully automated and accessible pharmacy experience** where users can interact, order, and receive real-time pharmacy services **directly from Telegram**, with zero need for additional apps or websites.

# 🧩 BotTelegram Project — Full Documentation

---

## 1. Project Overview

**BotTelegram** is a Django-based Telegram bot system designed for managing pharmacy-related content and FAQs. It is built to be modular, scalable, and extendable for future features like AI integration, mini-apps inside Telegram, and WhatsApp bot extensions.

The project consists of **two main Django apps**:

1. **pharmacy_app** – Manages medicines, pharmacies, and administrative data.
2. **bot_app** – Manages Telegram bot logic, FAQs, categories, bot settings, and interactive workflows.

**Primary Goals:**

- Provide a fully interactive Telegram bot with dynamic keyboards.
- Enable an admin dashboard for managing categories, subcategories, FAQs, and bot settings.
- Maintain modular architecture to support future AI-powered features, mini-apps, and other expansions.

---

## 2. Full Project Tree

```
project_root/
├── activating_virtual_env.txt
├── bot_app/
│   ├── __init__.py
│   ├── __pycache__/
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── telegram_utils.py
│   ├── views.py
│   ├── urls.py
│   ├── tests.py
│   ├── migrations/
│   │   ├── 0001_initial.py
│   │   ├── 0002_botsettings.py
│   │   ├── 0003_botsettings_is_connected.py
│   │   ├── 0004_botsettings_owner.py
│   │   ├── 0005_faqquestion.py
│   │   ├── 0006_delete_faqquestion.py
│   │   ├── 0007_botsettings_active_users_count_and_more.py
│   ├── static/
│   │   ├── css/
│   │   │   ├── categories.css
│   │   │   ├── faq_tree.css
│   ├── telegram/
│   │   ├── __init__.py
│   │   ├── constants.py
│   │   ├── state.py
│   │   ├── views.py
│   │   ├── handlers/
│   │   │   ├── __init__.py
│   │   │   ├── callback_handler.py
│   │   │   ├── category_handler.py
│   │   │   ├── faq_handler.py
│   │   │   ├── message_handler.py
│   │   ├── utils/
│   │   │   ├── __init__.py
│   │   │   ├── api.py
│   │   │   ├── keyboards.py
│   │   │   ├── loader.py
│   ├── templates/
│   │   ├── bot_app/
│   │   │   ├── base.html
│   │   │   ├── bot_settings.html
│   │   │   ├── management.html
│   │   │   ├── nav_bot.html
│   │   │   ├── partials/
│   │   │   │   ├── _category_item.html
│   │   │   │   ├── faq_list_by_category.html
│   │   │   │   ├── faq_modal.html
├── pharmacy_app/
│   ├── __init__.py
│   ├── admin.py
│   ├── apps.py
│   ├── forms.py
│   ├── models.py
│   ├── views.py
│   ├── urls.py
│   ├── tests.py
│   ├── management/
│   │   ├── commands/
│   │   │   ├── create_django_users.py
│   ├── migrations/
│   │   ├── 0001_initial.py
│   │   ├── 0002_telegramuser_user.py
│   │   ├── 0003_remove_medicine_image_url_medicine_image.py
│   │   ├── 0004_faqcategory_remove_faq_idx_faq_pharmacy_active_and_more.py
│   │   ├── 0005_remove_faqcategory_parent_and_more.py
│   │   ├── 0006_pharmacy_owner.py
│   ├── templates/
│   │   ├── owner/
│   │   │   ├── _medicine_row.html
│   │   │   ├── base.html
│   │   │   ├── dashboard.html
│   │   │   ├── login.html
│   │   │   ├── medicine_confirm_delete.html
│   │   │   ├── medicine_form.html
│   │   │   ├── medicines_list.html
├── db.sqlite3
├── media/
│   ├── medicines/
│   ├── temp/
├── manage.py
├── pharmacy_system_bot/
│   ├── __init__.py
│   ├── settings.py
│   ├── urls.py
│   ├── wsgi.py
├── project_structure.txt
├── tree_structure_extractor.py
```

---

## 3. Database Models

### 3.1 bot_app Models

**BotSettings**

- Stores bot configuration and analytics.
- Fields:

  - `bot_token` – Telegram API token
  - `owner` – ForeignKey to User
  - `is_connected` – Boolean
  - `interactions_count` – Integer
  - `active_users_count` – Integer
  - `questions_count` – Integer

**FAQCategory**

- Hierarchical categories for FAQs.
- Fields:

  - `title` – CharField
  - `parent` – Self-referencing FK (nullable)
  - `order` – Integer for sorting

**FAQ**

- Questions & answers linked to categories.
- Fields:

  - `question` – TextField
  - `answer` – TextField
  - `category` – FK → FAQCategory

---

### 3.2 pharmacy_app Models

**Pharmacy**

- Stores pharmacy data.
- Fields: name, address, phone, image, active, owner (FK → User)

**Medicine**

- Stores medicine data.
- Fields: name, description, price, image, pharmacy (FK → Pharmacy)

**TelegramUser**

- Links Telegram users to Django users.
- Fields: telegram_user_id, user (FK → User)

---

## 4. Telegram Bot Architecture

**Location:** `bot_app/telegram/`

```
handlers/      → Event-specific handlers
utils/         → Helper functions (keyboards, API, loader)
state.py       → User state management
views.py       → Webhook / entry points
constants.py   → Bot commands, texts
```

**Flow:**

1. User sends message → `message_handler`
2. Inline buttons → `callback_handler`
3. Category navigation → `category_handler`
4. Question selection → `faq_handler`
5. Dynamic keyboards via `keyboards.py`
6. DB queries abstracted in `api.py`
7. User state tracked in `state.py`

---

## 5. Bot Workflow

```
/start → Default Keyboard → Categories → Subcategories → FAQ → Answer
      → Back button → Return to default keyboard
```

**Features:**

- Dynamic inline keyboards
- Hierarchical category navigation
- Back & home buttons
- Analytics counters updated via `BotSettings`

---

## 6. Admin Dashboard

**Templates:** `bot_app/templates/bot_app/`

**Features:**

- Bot settings management
- Category/Subcategory CRUD
- FAQ CRUD via modals
- Analytics & counters

**Future Improvements:**

- Replace tree-view with **View button + modal**
- Add medicine mini-app grid layout for Telegram

---

## 7. Utilities & Helper Files

- `telegram_utils.py` → External bot helpers
- `keyboards.py` → Generates dynamic keyboards
- `loader.py` → Initializes bot
- `api.py` → Clean DB API for handlers

**Purpose:** Keep logic modular and scalable.

---

## 8. Completed Work

- Bot models (`BotSettings`, `FAQCategory`, `FAQ`)
- Telegram handlers implemented
- Inline & reply keyboards
- Admin dashboard with full CRUD
- Bot state management
- Webhook setup
- Analytics counters
- Analytics counters
- Media management (medicine images)
- Custom Start Keywords (per-bot configuration)
- Free Trial Implementation (7-day automatic trial)

---

## 9. Remaining Work / Roadmap

- Telegram mini-app for medicine grid view
- AI integration for auto-answering questions
- Optional React frontend for admin dashboard
- WhatsApp bot integration
- Dashboard improvements (modals + view buttons)
- Advanced reporting and analytics

---

## 10. Design Principles

- Modular architecture: `handlers`, `utils`, `views` separated
- Scalable DB: hierarchical categories & analytics counters
- Maintainable templates & media structure
- Extendable for AI and mini-apps
- Separation of concerns between Django logic & Telegram logic

---

## 11. Final Notes

The project has reached a **stable core stage**:

- Fully operational Telegram bot with categories, subcategories, FAQs
