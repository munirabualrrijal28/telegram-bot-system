-- NUCLEAR OPTION: Force modify the specific columns causing issues
-- This ignores table defaults and forces the column itself to be utf8mb4

USE bot_management_db;

SET FOREIGN_KEY_CHECKS = 0;

-- 1. Explicitly modify the welcome_message column
ALTER TABLE bot_settings 
MODIFY COLUMN welcome_message LONGTEXT 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci 
NOT NULL;

-- 2. Explicitly modify other text columns just in case
ALTER TABLE bot_settings 
MODIFY COLUMN fallback_message LONGTEXT 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci 
NOT NULL;

ALTER TABLE bot_settings 
MODIFY COLUMN start_keywords LONGTEXT 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci 
NULL;

-- 3. Verify the change
SELECT TABLE_NAME, COLUMN_NAME, CHARACTER_SET_NAME, COLLATION_NAME 
FROM information_schema.COLUMNS 
WHERE TABLE_SCHEMA = 'bot_management_db' 
  AND TABLE_NAME = 'bot_settings' 
  AND COLUMN_NAME = 'welcome_message';

SET FOREIGN_KEY_CHECKS = 1;

SELECT '✅ Column welcome_message explicitly converted to utf8mb4!' AS Status;
