-- Create Core Application Tables for bot_management_db
-- Run this in MySQL Workbench to create workspace, telegram_user, and related tables

USE bot_management_db;

-- ============================================
-- Table: workspace (Main tenant model)
-- ============================================
CREATE TABLE IF NOT EXISTS workspace (
    id CHAR(36) PRIMARY KEY,  -- UUID
    owner_id INT NULL,
    name VARCHAR(255) NOT NULL,
    address TEXT NULL,
    contact_phone VARCHAR(32) NULL,
    contact_email VARCHAR(254) NULL,
    logo_url VARCHAR(500) NULL,
    hours JSON NULL,
    settings JSON NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    UNIQUE KEY workspace_owner_id (owner_id),
    CONSTRAINT workspace_owner_id_fk FOREIGN KEY (owner_id) REFERENCES auth_user (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- Table: telegram_user (Application user profile)
-- ============================================
CREATE TABLE IF NOT EXISTS telegram_user (
    id CHAR(36) PRIMARY KEY,  -- UUID
    user_id INT NULL,
    telegram_user_id BIGINT NULL,
    name VARCHAR(200) NULL,
    email VARCHAR(254) NULL,
    phone VARCHAR(32) NULL,
    password_hash VARCHAR(255) NULL,
    role VARCHAR(32) NOT NULL DEFAULT 'customer',
    workspace_id CHAR(36) NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    has_used_free_trial TINYINT(1) NOT NULL DEFAULT 0,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    UNIQUE KEY telegram_user_user_id (user_id),
    INDEX idx_tg_user_telegram (telegram_user_id),
    INDEX idx_tg_user_email (email),
    INDEX idx_tg_user_phone (phone),
    INDEX idx_tg_user_role (role),
    CONSTRAINT telegram_user_user_id_fk FOREIGN KEY (user_id) REFERENCES auth_user (id) ON DELETE SET NULL,
    CONSTRAINT telegram_user_workspace_id_fk FOREIGN KEY (workspace_id) REFERENCES workspace (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- Table: system_admin (System administrators)
-- ============================================
CREATE TABLE IF NOT EXISTS system_admin (
    id CHAR(36) PRIMARY KEY,  -- UUID
    username VARCHAR(150) NOT NULL UNIQUE,
    email VARCHAR(254) NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role VARCHAR(32) NOT NULL DEFAULT 'moderator',
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    last_login DATETIME(6) NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- Table: subscription (Workspace subscriptions)
-- ============================================
CREATE TABLE IF NOT EXISTS subscription (
    id CHAR(36) PRIMARY KEY,  -- UUID
    workspace_id CHAR(36) NOT NULL,
    plan_name VARCHAR(100) NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'active',
    start_date DATE NOT NULL,
    end_date DATE NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    updated_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6) ON UPDATE CURRENT_TIMESTAMP(6),
    INDEX idx_subscription_workspace (workspace_id),
    INDEX idx_subscription_status (status),
    INDEX idx_subscription_end (end_date),
    CONSTRAINT subscription_workspace_id_fk FOREIGN KEY (workspace_id) REFERENCES workspace (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- Table: plan_activation_code (Activation codes)
-- ============================================
CREATE TABLE IF NOT EXISTS plan_activation_code (
    id CHAR(36) PRIMARY KEY,  -- UUID
    code VARCHAR(50) NOT NULL UNIQUE,
    plan_name VARCHAR(20) NOT NULL,
    code_type VARCHAR(20) NOT NULL DEFAULT 'general',
    target_user_id CHAR(36) NULL,
    is_used TINYINT(1) NOT NULL DEFAULT 0,
    used_by_id CHAR(36) NULL,
    used_at DATETIME(6) NULL,
    created_by_id CHAR(36) NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    expires_at DATETIME(6) NULL,
    INDEX idx_plan_code (code),
    INDEX idx_plan_is_used (is_used),
    INDEX idx_plan_expires (expires_at),
    CONSTRAINT plan_activation_code_target_user_id_fk FOREIGN KEY (target_user_id) REFERENCES telegram_user (id) ON DELETE CASCADE,
    CONSTRAINT plan_activation_code_used_by_id_fk FOREIGN KEY (used_by_id) REFERENCES telegram_user (id) ON DELETE SET NULL,
    CONSTRAINT plan_activation_code_created_by_id_fk FOREIGN KEY (created_by_id) REFERENCES system_admin (id) ON DELETE SET NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- Table: attachment (File attachments)
-- ============================================
CREATE TABLE IF NOT EXISTS attachment (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    image VARCHAR(100) NOT NULL,
    type VARCHAR(20) NOT NULL DEFAULT 'GENERAL',
    owner_id INT NOT NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    INDEX idx_attachment_owner (owner_id),
    INDEX idx_attachment_type (type),
    CONSTRAINT attachment_owner_id_fk FOREIGN KEY (owner_id) REFERENCES auth_user (id) ON DELETE CASCADE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- Table: audit_log (System audit logs)
-- ============================================
CREATE TABLE IF NOT EXISTS audit_log (
    id CHAR(36) PRIMARY KEY,  -- UUID
    actor_type VARCHAR(32) NOT NULL,
    actor_id VARCHAR(36) NULL,
    action VARCHAR(200) NOT NULL,
    resource_type VARCHAR(100) NOT NULL,
    resource_id VARCHAR(36) NULL,
    details JSON NULL,
    ip_address VARCHAR(45) NULL,
    created_at DATETIME(6) NOT NULL DEFAULT CURRENT_TIMESTAMP(6),
    INDEX idx_audit_actor (actor_type, actor_id),
    INDEX idx_audit_resource (resource_type, resource_id),
    INDEX idx_audit_created_at (created_at)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- Verification
-- ============================================
SELECT '✅ Core application tables created successfully!' AS Status;
SELECT COUNT(*) AS 'Total Tables' FROM information_schema.tables WHERE table_schema = 'bot_management_db';
SHOW TABLES;
