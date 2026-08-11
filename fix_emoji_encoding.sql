-- Fix Emoji Support: Convert tables to utf8mb4 (WITH FOREIGN KEYS DISABLED)
-- This fixes "Incorrect string value" errors for emojis like 👋

USE bot_management_db;

-- 1. Disable Foreign Key Checks to allow modification
SET FOREIGN_KEY_CHECKS = 0;

-- 2. Convert Database Defaults
ALTER DATABASE bot_management_db CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci;

-- 3. Convert Tables individually

-- Bot Settings (Welcome message, fallback message, etc.)
ALTER TABLE bot_settings CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- FAQs (Questions and Answers often have emojis)
ALTER TABLE bot_faq CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE bot_faq_category CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Bot Pages and Groups
ALTER TABLE bot_page CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE bot_page_group CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Ecom Tables (Medicine names/descriptions)
ALTER TABLE ecom_category CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE ecom_medicine CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Workspace and User Tables (Names can have emojis)
ALTER TABLE workspace CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
ALTER TABLE telegram_user CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- Django Auth Tables (Usernames)
ALTER TABLE auth_user CONVERT TO CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;

-- 4. Re-enable Foreign Key Checks
SET FOREIGN_KEY_CHECKS = 1;

SELECT '✅ All tables converted to utf8mb4! Emojis are now supported.' AS Status;
