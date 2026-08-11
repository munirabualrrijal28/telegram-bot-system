-- Complete Django Database Setup for bot_management_db
-- Run this entire script in MySQL Workbench to create all missing tables

USE bot_management_db;

-- ============================================
-- PART 1: Django Core Tables (auth, contenttypes, sessions, admin)
-- ============================================

-- Django content types
CREATE TABLE IF NOT EXISTS django_content_type (
    id INT AUTO_INCREMENT PRIMARY KEY,
    app_label VARCHAR(100) NOT NULL,
    model VARCHAR(100) NOT NULL,
    UNIQUE KEY django_content_type_app_label_model (app_label, model)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Django migrations tracking
CREATE TABLE IF NOT EXISTS django_migrations (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    app VARCHAR(255) NOT NULL,
    name VARCHAR(255) NOT NULL,
    applied DATETIME(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Auth: Permissions
CREATE TABLE IF NOT EXISTS auth_permission (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    content_type_id INT NOT NULL,
    codename VARCHAR(100) NOT NULL,
    UNIQUE KEY auth_permission_content_type_id_codename (content_type_id, codename),
    CONSTRAINT auth_permission_content_type_id FOREIGN KEY (content_type_id) REFERENCES django_content_type (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Auth: Groups
CREATE TABLE IF NOT EXISTS auth_group (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(150) NOT NULL UNIQUE
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Auth: Group Permissions
CREATE TABLE IF NOT EXISTS auth_group_permissions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    group_id INT NOT NULL,
    permission_id INT NOT NULL,
    UNIQUE KEY auth_group_permissions_group_id_permission_id (group_id, permission_id),
    CONSTRAINT auth_group_permissions_group_id FOREIGN KEY (group_id) REFERENCES auth_group (id),
    CONSTRAINT auth_group_permissions_permission_id FOREIGN KEY (permission_id) REFERENCES auth_permission (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Auth: Users (THE MOST IMPORTANT TABLE!)
CREATE TABLE IF NOT EXISTS auth_user (
    id INT AUTO_INCREMENT PRIMARY KEY,
    password VARCHAR(128) NOT NULL,
    last_login DATETIME(6) NULL,
    is_superuser TINYINT(1) NOT NULL,
    username VARCHAR(150) NOT NULL UNIQUE,
    first_name VARCHAR(150) NOT NULL,
    last_name VARCHAR(150) NOT NULL,
    email VARCHAR(254) NOT NULL,
    is_staff TINYINT(1) NOT NULL,
    is_active TINYINT(1) NOT NULL,
    date_joined DATETIME(6) NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Auth: User Groups
CREATE TABLE IF NOT EXISTS auth_user_groups (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    group_id INT NOT NULL,
    UNIQUE KEY auth_user_groups_user_id_group_id (user_id, group_id),
    CONSTRAINT auth_user_groups_user_id FOREIGN KEY (user_id) REFERENCES auth_user (id),
    CONSTRAINT auth_user_groups_group_id FOREIGN KEY (group_id) REFERENCES auth_group (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Auth: User Permissions
CREATE TABLE IF NOT EXISTS auth_user_user_permissions (
    id BIGINT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    permission_id INT NOT NULL,
    UNIQUE KEY auth_user_user_permissions_user_id_permission_id (user_id, permission_id),
    CONSTRAINT auth_user_user_permissions_user_id FOREIGN KEY (user_id) REFERENCES auth_user (id),
    CONSTRAINT auth_user_user_permissions_permission_id FOREIGN KEY (permission_id) REFERENCES auth_permission (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Django Admin Log
CREATE TABLE IF NOT EXISTS django_admin_log (
    id INT AUTO_INCREMENT PRIMARY KEY,
    action_time DATETIME(6) NOT NULL,
    object_id LONGTEXT NULL,
    object_repr VARCHAR(200) NOT NULL,
    action_flag SMALLINT UNSIGNED NOT NULL,
    change_message LONGTEXT NOT NULL,
    content_type_id INT NULL,
    user_id INT NOT NULL,
    CONSTRAINT django_admin_log_content_type_id FOREIGN KEY (content_type_id) REFERENCES django_content_type (id),
    CONSTRAINT django_admin_log_user_id FOREIGN KEY (user_id) REFERENCES auth_user (id),
    INDEX django_admin_log_content_type_id (content_type_id),
    INDEX django_admin_log_user_id (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Django Sessions
CREATE TABLE IF NOT EXISTS django_session (
    session_key VARCHAR(40) PRIMARY KEY,
    session_data LONGTEXT NOT NULL,
    expire_date DATETIME(6) NOT NULL,
    INDEX django_session_expire_date (expire_date)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- PART 2: Django Allauth Tables
-- ============================================

-- Account: Email Addresses
CREATE TABLE IF NOT EXISTS account_emailaddress (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    email VARCHAR(254) NOT NULL,
    verified TINYINT(1) NOT NULL,
    `primary` TINYINT(1) NOT NULL,
    UNIQUE KEY account_emailaddress_email (email),
    CONSTRAINT account_emailaddress_user_id FOREIGN KEY (user_id) REFERENCES auth_user (id),
    INDEX account_emailaddress_user_id_idx (user_id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Account: Email Confirmations
CREATE TABLE IF NOT EXISTS account_emailconfirmation (
    id INT AUTO_INCREMENT PRIMARY KEY,
    created DATETIME(6) NOT NULL,
    sent DATETIME(6) NULL,
    `key` VARCHAR(64) NOT NULL UNIQUE,
    email_address_id INT NOT NULL,
    CONSTRAINT account_emailconfirmation_email_address_id FOREIGN KEY (email_address_id) REFERENCES account_emailaddress (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Social Account: Social Apps (Google, Facebook, etc.)
CREATE TABLE IF NOT EXISTS socialaccount_socialapp (
    id INT AUTO_INCREMENT PRIMARY KEY,
    provider VARCHAR(30) NOT NULL,
    name VARCHAR(40) NOT NULL,
    client_id VARCHAR(191) NOT NULL,
    secret VARCHAR(191) NOT NULL,
    `key` VARCHAR(191) NOT NULL DEFAULT '',
    provider_id VARCHAR(200) NOT NULL DEFAULT '',
    settings JSON NOT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Social Account: Social App Sites (many-to-many)
CREATE TABLE IF NOT EXISTS socialaccount_socialapp_sites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    socialapp_id INT NOT NULL,
    site_id INT NOT NULL,
    UNIQUE KEY socialaccount_socialapp_sites_uniq (socialapp_id, site_id),
    CONSTRAINT socialaccount_socialapp_sites_socialapp_id FOREIGN KEY (socialapp_id) REFERENCES socialaccount_socialapp (id),
    CONSTRAINT socialaccount_socialapp_sites_site_id FOREIGN KEY (site_id) REFERENCES django_site (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Social Account: Social Accounts (user's connected social accounts)
CREATE TABLE IF NOT EXISTS socialaccount_socialaccount (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    provider VARCHAR(200) NOT NULL,
    uid VARCHAR(255) NOT NULL,
    last_login DATETIME(6) NOT NULL,
    date_joined DATETIME(6) NOT NULL,
    extra_data JSON NOT NULL,
    UNIQUE KEY socialaccount_socialaccount_provider_uid (provider, uid),
    CONSTRAINT socialaccount_socialaccount_user_id FOREIGN KEY (user_id) REFERENCES auth_user (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Social Account: Social Tokens (OAuth tokens)
CREATE TABLE IF NOT EXISTS socialaccount_socialtoken (
    id INT AUTO_INCREMENT PRIMARY KEY,
    token LONGTEXT NOT NULL,
    token_secret LONGTEXT NOT NULL,
    expires_at DATETIME(6) NULL,
    account_id INT NOT NULL,
    app_id INT NULL,
    UNIQUE KEY socialaccount_socialtoken_app_account (app_id, account_id),
    CONSTRAINT socialaccount_socialtoken_account_id FOREIGN KEY (account_id) REFERENCES socialaccount_socialaccount (id),
    CONSTRAINT socialaccount_socialtoken_app_id FOREIGN KEY (app_id) REFERENCES socialaccount_socialapp (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- ============================================
-- PART 3: Configure Google OAuth
-- ============================================

-- Insert Google OAuth app (placeholder credentials - UPDATE THESE!)
INSERT INTO socialaccount_socialapp (id, provider, name, client_id, secret, `key`, provider_id, settings)
VALUES (1, 'google', 'Google OAuth', 'YOUR_GOOGLE_CLIENT_ID_HERE', 'YOUR_GOOGLE_CLIENT_SECRET_HERE', '', '', '{}')
ON DUPLICATE KEY UPDATE 
    provider = 'google',
    name = 'Google OAuth';

-- Link Google app to your site
INSERT INTO socialaccount_socialapp_sites (socialapp_id, site_id)
VALUES (1, 1)
ON DUPLICATE KEY UPDATE socialapp_id = 1;

-- ============================================
-- PART 4: Verification
-- ============================================

SELECT '✅ All tables created successfully!' AS Status;
SELECT COUNT(*) AS 'Total Tables' FROM information_schema.tables WHERE table_schema = 'bot_management_db';
SHOW TABLES;
