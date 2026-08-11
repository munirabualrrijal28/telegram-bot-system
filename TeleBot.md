# 🤖 TeleBot - Business Bot Management System

## 📋 Project Overview

**TeleBot** is a comprehensive **Django-based Telegram Bot Management System** designed for businesses of all types. It provides a complete multi-tenant SaaS platform where business owners (retailers, service providers, generic stores) can create, configure, and manage intelligent Telegram bots to serve their customers.

### 🎯 Core Mission

To create a **fully automated and accessible business experience** where users can interact, order products/services, receive real-time support, and access information **directly from Telegram**, with zero need for additional apps or websites.

---

## 🏗️ System Architecture

### Multi-Tenant SaaS Platform

The system is built as a **multi-tenant application** with three distinct user roles:

1. **System Administrators** - Manage the entire platform, activation codes, and subscriptions
2. **Business/Workspace Owners** - Create and manage their bots, products (service catalog), categories, and FAQs
3. **End Users (Telegram Users)** - Interact with business bots via Telegram

### Technology Stack

- **Backend Framework**: Django 5.2.6 (Python)
- **Bot Framework**: python-telegram-bot
- **Database**: MySQL (Primary) / SQLite (Development)
- **Frontend**: HTML, CSS, JavaScript (Vanilla + AJAX)
- **Authentication**: Django Auth + Django Allauth (Google OAuth)
- **API Integration**: Telegram Bot API
- **Deployment**: Webhook-based (Cloudflare Tunnel)

---

## 📦 Application Structure

The project is organized into **7 Django apps** following a modular, domain-driven architecture:

### 1. **core** (Foundation Models)

Contains the foundational models used across the entire system:

- `UUIDModel` - Abstract base class with UUID primary keys
- `Workspace` - Main tenant model (Business Entity / formerly Pharmacy)
- `SystemAdmin` - System-level administrator accounts
- `TelegramUser` - Application user profile (links Django User with Telegram)
- `AuditLog` - System-wide action logging
- `Subscription` - Business subscription tracking
- `Attachment` - File attachments
- `PlanActivationCode` - Unified activation code system for all plans

### 2. **ecom** (E-commerce)

Product catalog, inventory, and order management.
_Note: Due to the project's evolution, some internal model names (e.g., `Medicine`) may still reflect the initial pharmacy focus but serve as generic Product models._

- `Category` - Product/Service categories
- `Medicine` - **Product Catalog** (Generic Item/Product/Service with pricing & stock)
- `PriceHistory` - Price change tracking
- `InventoryTransaction` - Stock movement tracking
- `Order` - Customer orders
- `OrderItem` - Order line items

### 3. **ai_service** (AI/ML Service)

AI configuration, knowledge base, and logging:

- `AIModel` - AI model configuration (OpenAI, Qwen, Ollama)
- `AIPromptTemplate` - Reusable prompt templates
- `AIDocument` - Document knowledge base
- `AIEmbedding` - Vector embeddings storage
- `AIRequest` - AI request logging
- `AIResponse` - AI response storage
- `AIModeration` - AI content moderation logging

### 4. **bot_app** (Telegram Bot Core)

The main bot management application:

- `BotSettings` - Bot configuration and analytics
- `FAQCategory` - Hierarchical categories for FAQs
- `FAQ` - Questions & answers linked to categories
- `BotPage` - Pages within categories
- `PageGroup` - Groups within pages containing attachments

**Telegram Bot Logic** (`bot_app/telegram/`):

- `handlers/` - Event-specific handlers
  - `message_handler.py` - Processes text messages
  - `callback_handler.py` - Handles inline button clicks
  - `category_handler.py` - Category navigation logic
  - `faq_handler.py` - FAQ display and interaction
- `utils/` - Helper functions
  - `keyboards.py` - Dynamic keyboard generation
  - `api.py` - Database API abstractions
  - `loader.py` - Bot initialization

### 5. **admin_app** (Admin Dashboard)

System-wide administration for platform owners:

- `SystemNotification` - Platform-wide notification system

**Features**:

- System admin authentication
- Dashboard with analytics (total bots, users, subscriptions)
- Subscription management (activate/deactivate user plans)
- Activation code CRUD operations (via `PlanActivationCode`)
- User management
- Broadcast notifications to all users

### 6. **pharmacy_app** (Owner Dashboard)

_Legacy naming preserved._ Currently handles owner authentication and basic views for the Business/Workspace components.

### 7. **home_app** (Landing Page)

Public-facing landing page for the platform.

---

## 🗄️ Database Schema

### Key Relationships

```
User (Django Auth)
└── Workspace (one-to-one)
    ├── BotSettings (multiple bots per workspace)
    │   ├── FAQCategory (hierarchical)
    │   │   ├── FAQ (questions/answers)
    │   │   └── BotPage
    │   │       └── PageGroup
    │   │           ├── Attachments (general)
    │   │           └── Products (Medicines)
    │   └── Products (Medicines)
    ├── Products (Medicines)
    ├── Categories
    ├── Orders
    └── Subscriptions

TelegramUser (Telegram Users)
├── telegram_user_id (unique)
└── Orders
```

### Database Configuration

- **Production**: MySQL on port 3307
  - Database: `pharmacy_db` (Legacy Name)
  - User: `pharmacy_user`
- **Development**: SQLite (`db.sqlite3`)

---

## 🔑 Key Features

### 1. Multi-Bot Management

- Business owners can create multiple bots under a single account (e.g., Sales Bot, Support Bot)
- Each bot has independent configuration:
  - Bot token
  - Business name
  - Welcome/support messages
  - Default keyboard type (Inline/Reply)
  - Analytics (interactions, active users, questions)

### 2. Hierarchical Category System

- **Categories** → **Subcategories** → **FAQs/Products**
- Dynamic nested structure with unlimited depth
- Suitable for various business types (e.g., Menus, Service Catalogs, Help Centers)

### 3. Intelligent FAQ System

- Rich question/answer format
- Linked to categories
- Active/inactive status
- AJAX-based CRUD operations

### 4. Pages & Groups

- **Pages** organize content within categories
- **Groups** contain collections of attachments
- Groups support:
  - Title and description
  - Contact button (links to bot or custom bot)
  - Mixed attachments (general files + products)
  - Custom ordering

### 5. Attachment & Product Management

- **Attachments**: General files, images, documents.
- **Products**: (Technically `Medicine` model) Supports images, descriptions, pricing, stock.
- Linked to specific bots.

### 6. Subscription System

- **Four tiers**: Free, Free Trial (7 Days), Pro, Max
- **Unified Activation Codes**:
  - Managed via `PlanActivationCode` model in `core`
  - Secure, random code generation
- **Free Trial**:
  - One-time use per user
  - 7-day duration with Pro features

### 7. Telegram Bot Workflow

```
User starts bot → /start
    ↓
Welcome message + Main keyboard
    ↓
Categories list (Inline/Reply Configurable)
    ↓
Select category → View subcategories/FAQs/Pages
    ↓
Select Content → Display info/product/answer
    ↓
Back button → Return to previous level
    ↓
Home button → Return to main menu
```

### 8. Admin Features

- **Dashboard Analytics**:
  - Total bots, users, subscriptions
  - Subscription breakdown
- **User Management**:
  - View all registered users
  - Manage user subscriptions
- **Broadcast System**:
  - Send notifications to all users or specific targets

### 9. Owner Features (Bot Dashboard)

- **Bot Settings**:
  - Create/edit/delete bots
  - Configure token, webhook, active status
- **Category Management**:
  - Tree view visualization
  - Drag-and-drop ordering
- **Product/Service Management**:
  - Add/edit/delete items (Medicines)
  - Image upload, Price tracking, Stock management
- **Subscription**:
  - View plan, Activate codes

---

## 🎨 Frontend Architecture

### Technology

- **Vanilla JavaScript** (no frameworks)
- **AJAX** for dynamic content loading
- **Bootstrap-inspired custom CSS**
- **Responsive design**

### UI Components

- Sidebar navigation
- Data tables with search/pagination
- Form modals
- Toast notifications (success/error/info/update)
- Tree view for categories
- Selection modals for attachments

---

## 🔐 Authentication & Authorization

### Three Authentication Systems

1. **System Admin Authentication** (`admin_app`)
   - Custom auth, Admin-only routes
2. **Business Owner Authentication** (`pharmacy_app`)
   - Django Auth + Google OAuth
   - User → Workspace relationship
3. **Telegram User Tracking** (`bot_app`)
   - Automatic user creation on interaction via `TelegramUser` model

---

## 🔄 System Workflow Logic

### Hierarchy & Relationships

The system follows a clear hierarchical structure designed for multi-tenancy and scalability:

1.  **User (The Account Owner)** 👤
    - **Role**: The business owner or administrator.
    - **Entity**: Django `User` model.
    - **Relationship**: Owns exactly **ONE** Workspace (Account).

2.  **Workspace (The Business Entity)** 🏢
    - **Role**: Represents the business organization (Store, Clinic, Agency, etc.).
    - **Entity**: `Workspace` model.
    - **Relationship**: Contains Bots, Products, and Subscribers.
    - **Function**: Central container for all business data.

3.  **Bots (The Interfaces)** 🤖
    - **Role**: The interfaces customers interact with.
    - **Entity**: `BotSettings` model.
    - **Function**: Serve as the touchpoints for customers.

4.  **TelegramUsers (The Customers)** 👥
    - **Role**: End-users chatting with the bots.
    - **Entity**: `TelegramUser` model.
    - **Relationship**: Interaction happens within the scope of a Workspace.

---

## 💡 Usage Scenarios

### Scenario 1: Retail Store Owner

1. Registers account.
2. Creates a "Sales Bot".
3. Uploads product catalog (using the Product/Medicine interface).
4. Configures categories for "Men's Wear", "Electronics".
5. Bot serves customers looking to browse and check prices.

### Scenario 2: Service Provider (e.g., Consultant)

1. Registers account.
2. Creates a "Booking Info Bot".
3. Sets up FAQs for "Pricing", "Hours", "Location".
4. Uses Groups to attach "Portfolio.pdf".
5. Bot answers common client questions automatically.

### Scenario 3: Aggregator

1. Creates multiple bots for different branches/departments under one Workspace.
2. Manages all orders/interactions from a central dashboard.

---

## 🛠️ Development Notes

### Commands

- Run server: `python manage.py runserver`
- Migrations: `python manage.py makemigrations && python manage.py migrate`

### Database

- **Important**: Models use UUID primary keys.

### Legacy Terminology

- `Medicine` model is used for all "Products" or "Items".
- `pharmacy_app` handles the owner dashboard logic.
- `pharmacy_db` is the default database name.

---

## 📜 License
