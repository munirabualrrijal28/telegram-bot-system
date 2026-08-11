-- Check specific column collation
USE bot_management_db;

SELECT 
    TABLE_NAME, 
    COLUMN_NAME, 
    CHARACTER_SET_NAME, 
    COLLATION_NAME 
FROM information_schema.COLUMNS 
WHERE TABLE_SCHEMA = 'bot_management_db' 
  AND TABLE_NAME = 'bot_settings' 
  AND COLUMN_NAME = 'welcome_message';
