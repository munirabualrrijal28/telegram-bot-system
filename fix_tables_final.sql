-- FINAL FIX: Correct Table Names and Create Missing Tables
-- This aligns the database with Django models exactly.
-- Run this to fix "Table medicine doesn't exist" and emoji errors.

USE bot_management_db;

SET FOREIGN_KEY_CHECKS = 0;

-- 1. DROP Incorrectly Named Tables (if they exist)
DROP TABLE IF EXISTS bot_page_group_medicines;
DROP TABLE IF EXISTS bot_page_group_attachments;
DROP TABLE IF EXISTS ecom_medicine;
DROP TABLE IF EXISTS ecom_category;

-- 2. CREATE Tables with Correct Names (matching models.py db_table)

-- Table: category (was ecom_category)
CREATE TABLE IF NOT EXISTS category (
    id CHAR(36) PRIMARY KEY,
    workspace_id CHAR(36) NULL, -- Can be null? Check model: null=True, blank=True
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200) NULL,
    description TEXT NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    CONSTRAINT category_workspace_id_fk FOREIGN KEY (workspace_id) REFERENCES workspace (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: medicine (was ecom_medicine)
CREATE TABLE IF NOT EXISTS medicine (
    id CHAR(36) PRIMARY KEY,
    bot_id CHAR(36) NULL,
    workspace_id CHAR(36) NOT NULL,
    category_id CHAR(36) NULL,
    sku VARCHAR(100) NULL UNIQUE,
    name VARCHAR(255) NOT NULL,
    brand VARCHAR(200) NULL,
    generic_name VARCHAR(200) NULL,
    description TEXT NULL,
    dosage_form VARCHAR(100) NULL,
    strength VARCHAR(100) NULL,
    price DECIMAL(12, 2) NULL,
    currency VARCHAR(3) NOT NULL DEFAULT 'USD',
    visible TINYINT(1) NOT NULL DEFAULT 1,
    stock_quantity INT NOT NULL DEFAULT 0,
    low_stock_threshold INT NOT NULL DEFAULT 0,
    image VARCHAR(100) NULL,
    metadata JSON NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    CONSTRAINT medicine_bot_id_fk FOREIGN KEY (bot_id) REFERENCES bot_settings (id) ON DELETE CASCADE,
    CONSTRAINT medicine_workspace_id_fk FOREIGN KEY (workspace_id) REFERENCES workspace (id) ON DELETE CASCADE,
    CONSTRAINT medicine_category_id_fk FOREIGN KEY (category_id) REFERENCES category (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: bot_app_pagegroup_medicines (M2M table for PageGroup.medicines)
-- Django default naming: app_model_field -> bot_app_pagegroup_medicines
CREATE TABLE IF NOT EXISTS bot_app_pagegroup_medicines (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    pagegroup_id CHAR(36) NOT NULL,
    medicine_id CHAR(36) NOT NULL,
    UNIQUE KEY bot_app_pagegroup_medicines_uniq (pagegroup_id, medicine_id),
    CONSTRAINT bot_app_pg_med_group_fk FOREIGN KEY (pagegroup_id) REFERENCES bot_page_group (id) ON DELETE CASCADE,
    CONSTRAINT bot_app_pg_med_medicine_fk FOREIGN KEY (medicine_id) REFERENCES medicine (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: bot_app_pagegroup_attachments (M2M table for PageGroup.attachments)
-- Django default naming: bot_app_pagegroup_attachments
CREATE TABLE IF NOT EXISTS bot_app_pagegroup_attachments (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    pagegroup_id CHAR(36) NOT NULL,
    attachment_id INT NOT NULL, -- Attachment uses auto-increment ID
    UNIQUE KEY bot_app_pagegroup_atts_uniq (pagegroup_id, attachment_id),
    CONSTRAINT bot_app_pg_att_group_fk FOREIGN KEY (pagegroup_id) REFERENCES bot_page_group (id) ON DELETE CASCADE,
    CONSTRAINT bot_app_pg_att_attachment_fk FOREIGN KEY (attachment_id) REFERENCES attachment (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;


-- 3. CREATE Missing Ecom Tables

-- Table: price_history
CREATE TABLE IF NOT EXISTS price_history (
    id CHAR(36) PRIMARY KEY,
    medicine_id CHAR(36) NOT NULL,
    old_price DECIMAL(12, 2) NULL,
    new_price DECIMAL(12, 2) NULL,
    changed_by_user_id CHAR(36) NULL,
    changed_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    CONSTRAINT price_history_medicine_fk FOREIGN KEY (medicine_id) REFERENCES medicine (id) ON DELETE CASCADE,
    CONSTRAINT price_history_user_fk FOREIGN KEY (changed_by_user_id) REFERENCES telegram_user (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: inventory_transaction
CREATE TABLE IF NOT EXISTS inventory_transaction (
    id CHAR(36) PRIMARY KEY,
    medicine_id CHAR(36) NOT NULL,
    workspace_id CHAR(36) NOT NULL,
    delta INT NOT NULL,
    reason VARCHAR(50) NOT NULL,
    reference_id VARCHAR(36) NULL,
    performed_by_id CHAR(36) NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    CONSTRAINT inv_trans_medicine_fk FOREIGN KEY (medicine_id) REFERENCES medicine (id) ON DELETE CASCADE,
    CONSTRAINT inv_trans_workspace_fk FOREIGN KEY (workspace_id) REFERENCES workspace (id) ON DELETE CASCADE,
    CONSTRAINT inv_trans_user_fk FOREIGN KEY (performed_by_id) REFERENCES telegram_user (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: order
CREATE TABLE IF NOT EXISTS `order` (
    id CHAR(36) PRIMARY KEY,
    workspace_id CHAR(36) NOT NULL,
    user_id CHAR(36) NULL,
    medicine_id CHAR(36) NULL,
    quantity INT UNSIGNED NOT NULL DEFAULT 1,
    total_price DECIMAL(12, 2) NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    metadata JSON NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    CONSTRAINT order_workspace_fk FOREIGN KEY (workspace_id) REFERENCES workspace (id) ON DELETE CASCADE,
    CONSTRAINT order_user_fk FOREIGN KEY (user_id) REFERENCES telegram_user (id) ON DELETE SET NULL,
    CONSTRAINT order_medicine_fk FOREIGN KEY (medicine_id) REFERENCES medicine (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- Table: order_item
CREATE TABLE IF NOT EXISTS order_item (
    id CHAR(36) PRIMARY KEY,
    order_id CHAR(36) NOT NULL,
    medicine_id CHAR(36) NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(12, 2) NOT NULL,
    total_price DECIMAL(12, 2) NOT NULL,
    CONSTRAINT order_item_order_fk FOREIGN KEY (order_id) REFERENCES `order` (id) ON DELETE CASCADE,
    CONSTRAINT order_item_medicine_fk FOREIGN KEY (medicine_id) REFERENCES medicine (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci;

-- 4. Re-run Welcome Message Fix (Just in case)
ALTER TABLE bot_settings 
MODIFY COLUMN welcome_message LONGTEXT 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci 
NOT NULL;

SET FOREIGN_KEY_CHECKS = 1;

SELECT '✅ All tables fixed and correctly named!' AS Status;
SHOW TABLES;
