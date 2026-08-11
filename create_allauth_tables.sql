-- Create all django-allauth tables for bot_management_db
USE bot_management_db;

-- Table: account_emailaddress
CREATE TABLE IF NOT EXISTS account_emailaddress (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    email VARCHAR(254) NOT NULL UNIQUE,
    verified TINYINT(1) NOT NULL,
    `primary` TINYINT(1) NOT NULL,
    CONSTRAINT account_emailaddress_user_id FOREIGN KEY (user_id) REFERENCES auth_user (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: account_emailconfirmation
CREATE TABLE IF NOT EXISTS account_emailconfirmation (
    id INT AUTO_INCREMENT PRIMARY KEY,
    created DATETIME(6) NOT NULL,
    sent DATETIME(6) NULL,
    `key` VARCHAR(64) NOT NULL UNIQUE,
    email_address_id INT NOT NULL,
    CONSTRAINT account_emailconfirmation_email_address_id FOREIGN KEY (email_address_id) REFERENCES account_emailaddress (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: socialaccount_socialapp
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

-- Table: socialaccount_socialapp_sites
CREATE TABLE IF NOT EXISTS socialaccount_socialapp_sites (
    id INT AUTO_INCREMENT PRIMARY KEY,
    socialapp_id INT NOT NULL,
    site_id INT NOT NULL,
    UNIQUE KEY socialaccount_socialapp_sites_uniq (socialapp_id, site_id),
    CONSTRAINT socialaccount_socialapp_sites_socialapp_id FOREIGN KEY (socialapp_id) REFERENCES socialaccount_socialapp (id),
    CONSTRAINT socialaccount_socialapp_sites_site_id FOREIGN KEY (site_id) REFERENCES django_site (id)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- Table: socialaccount_socialaccount
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

-- Table: socialaccount_socialtoken
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

-- Insert placeholder Google OAuth app (you'll need to update with real credentials)
INSERT INTO socialaccount_socialapp (id, provider, name, client_id, secret, `key`, provider_id, settings)
VALUES (1, 'google', 'Google OAuth', 'PLACEHOLDER_CLIENT_ID', 'PLACEHOLDER_SECRET', '', '', '{}')
ON DUPLICATE KEY UPDATE provider = 'google';

-- Link Google app to site
INSERT INTO socialaccount_socialapp_sites (socialapp_id, site_id)
VALUES (1, 1)
ON DUPLICATE KEY UPDATE socialapp_id = 1;

-- Verify tables were created
SELECT 'Tables created successfully!' AS Status;
SHOW TABLES LIKE '%account%';
SHOW TABLES LIKE '%social%';
