-- Create Remaining Application Tables for bot_management_db
-- Bot App & Ecom tables

USE bot_management_db;

-- ============================================
-- BOT_APP TABLES
-- ============================================

-- Table: bot_settings
CREATE TABLE IF NOT EXISTS bot_settings (
    id CHAR(36) PRIMARY KEY,
    owner_id INT NOT NULL,
    workspace_name VARCHAR(255) NOT NULL,
    telegram_token VARCHAR(255) NULL,
    bot_username VARCHAR(255) NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 0,
    is_connected TINYINT(1) NOT NULL DEFAULT 0,
    interactions_count INT UNSIGNED NOT NULL DEFAULT 0,
    questions_count INT UNSIGNED NOT NULL DEFAULT 0,
    active_users_count INT UNSIGNED NOT NULL DEFAULT 0,
    welcome_message TEXT NOT NULL,
    fallback_message TEXT NOT NULL,
    start_keywords TEXT NULL,
    working_hours_start TIME NOT NULL DEFAULT '08:00:00',
    working_hours_end TIME NOT NULL DEFAULT '22:00:00',
    language VARCHAR(20) NOT NULL DEFAULT 'en',
    show_contact_info TINYINT(1) NOT NULL DEFAULT 1,
    contact_phone VARCHAR(50) NULL,
    contact_address VARCHAR(255) NULL,
    google_maps_link VARCHAR(200) NULL,
    enable_ai_mode TINYINT(1) NOT NULL DEFAULT 0,
    home_keyboard_type VARCHAR(10) NOT NULL DEFAULT 'INLINE',
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    INDEX idx_botsettings_workspace (workspace_name),
    INDEX idx_botsettings_active (is_active),
    INDEX idx_botsettings_connected (is_connected),
    CONSTRAINT bot_settings_owner_id_fk FOREIGN KEY (owner_id) REFERENCES auth_user (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: bot_faq_category
CREATE TABLE IF NOT EXISTS bot_faq_category (
    id CHAR(36) PRIMARY KEY,
    bot_id CHAR(36) NULL,
    workspace_id CHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    parent_id CHAR(36) NULL,
    keyboard_type VARCHAR(10) NOT NULL DEFAULT 'INLINE',
    INDEX idx_faqcat_bot (bot_id),
    CONSTRAINT bot_faq_category_bot_id_fk FOREIGN KEY (bot_id) REFERENCES bot_settings (id) ON DELETE CASCADE,
    CONSTRAINT bot_faq_category_workspace_id_fk FOREIGN KEY (workspace_id) REFERENCES workspace (id) ON DELETE CASCADE,
    CONSTRAINT bot_faq_category_parent_id_fk FOREIGN KEY (parent_id) REFERENCES bot_faq_category (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: bot_faq
CREATE TABLE IF NOT EXISTS bot_faq (
    id CHAR(36) PRIMARY KEY,
    bot_id CHAR(36) NULL,
    workspace_id CHAR(36) NOT NULL,
    category_id CHAR(36) NULL,
    question TEXT NOT NULL,
    answer TEXT NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    INDEX idx_faq_bot (bot_id),
    CONSTRAINT bot_faq_bot_id_fk FOREIGN KEY (bot_id) REFERENCES bot_settings (id) ON DELETE CASCADE,
    CONSTRAINT bot_faq_workspace_id_fk FOREIGN KEY (workspace_id) REFERENCES workspace (id) ON DELETE CASCADE,
    CONSTRAINT bot_faq_category_id_fk FOREIGN KEY (category_id) REFERENCES bot_faq_category (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: bot_page
CREATE TABLE IF NOT EXISTS bot_page (
    id CHAR(36) PRIMARY KEY,
    category_id CHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    CONSTRAINT bot_page_category_id_fk FOREIGN KEY (category_id) REFERENCES bot_faq_category (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: bot_page_group
CREATE TABLE IF NOT EXISTS bot_page_group (
    id CHAR(36) PRIMARY KEY,
    page_id CHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    image VARCHAR(100) NULL,
    contact_bot_username VARCHAR(255) NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    CONSTRAINT bot_page_group_page_id_fk FOREIGN KEY (page_id) REFERENCES bot_page (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: bot_page_group_attachments (Many-to-Many)
CREATE TABLE IF NOT EXISTS bot_page_group_attachments (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    pagegroup_id CHAR(36) NOT NULL,
    attachment_id INT NOT NULL,
    UNIQUE KEY bot_page_group_attachments_unique (pagegroup_id, attachment_id),
    CONSTRAINT bot_page_group_attachments_group_fk FOREIGN KEY (pagegroup_id) REFERENCES bot_page_group (id) ON DELETE CASCADE,
    CONSTRAINT bot_page_group_attachments_attachment_fk FOREIGN KEY (attachment_id) REFERENCES attachment (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- ECOM TABLES (for Medicine management)
-- ============================================

-- Table: ecom_category
CREATE TABLE IF NOT EXISTS ecom_category (
    id CHAR(36) PRIMARY KEY,
    workspace_id CHAR(36) NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    CONSTRAINT ecom_category_workspace_id_fk FOREIGN KEY (workspace_id) REFERENCES workspace (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: ecom_medicine
CREATE TABLE IF NOT EXISTS ecom_medicine (
    id CHAR(36) PRIMARY KEY,
    workspace_id CHAR(36) NOT NULL,
    category_id CHAR(36) NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT NULL,
    price DECIMAL(10, 2) NOT NULL DEFAULT 0.00,
    stock INT NOT NULL DEFAULT 0,
    image VARCHAR(100) NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    CONSTRAINT ecom_medicine_workspace_id_fk FOREIGN KEY (workspace_id) REFERENCES workspace (id) ON DELETE CASCADE,
    CONSTRAINT ecom_medicine_category_id_fk FOREIGN KEY (category_id) REFERENCES ecom_category (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: bot_page_group_medicines (Many-to-Many)
CREATE TABLE IF NOT EXISTS bot_page_group_medicines (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    pagegroup_id CHAR(36) NOT NULL,
    medicine_id CHAR(36) NOT NULL,
    UNIQUE KEY bot_page_group_medicines_unique (pagegroup_id, medicine_id),
    CONSTRAINT bot_page_group_medicines_group_fk FOREIGN KEY (pagegroup_id) REFERENCES bot_page_group (id) ON DELETE CASCADE,
    CONSTRAINT bot_page_group_medicines_medicine_fk FOREIGN KEY (medicine_id) REFERENCES ecom_medicine (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- Verification
-- ============================================
SELECT '✅ Bot app and ecom tables created successfully!' AS Status;
SELECT COUNT(*) AS 'Total Tables' FROM information_schema.tables WHERE table_schema = 'bot_management_db';
SHOW TABLES;
