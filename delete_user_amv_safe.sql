-- Delete user "amv" (ID=1) - Safe mode compatible version
-- Run this to clean up the failed signup attempt

USE bot_management_db;

-- First, find and display the records we'll delete
SELECT 'Social accounts to delete:' AS Info;
SELECT id FROM socialaccount_socialaccount WHERE user_id = 1;

SELECT 'Email addresses to delete:' AS Info;
SELECT id FROM account_emailaddress WHERE user_id = 1;

-- Now delete them using direct ID references (safe mode compatible)

-- Delete social tokens (if any exist)
DELETE FROM socialaccount_socialtoken WHERE account_id = (
    SELECT id FROM (SELECT id FROM socialaccount_socialaccount WHERE user_id = 1 LIMIT 1) AS temp
);

-- Delete social accounts
DELETE FROM socialaccount_socialaccount WHERE user_id = 1;

-- Delete email addresses
DELETE FROM account_emailaddress WHERE user_id = 1;

-- Delete telegram_user (if exists)
DELETE FROM telegram_user WHERE user_id = 1;

-- Delete workspace (if exists)  
DELETE FROM workspace WHERE owner_id = 1;

-- Finally, delete the user
DELETE FROM auth_user WHERE id = 1;

-- Verify deletion
SELECT '✅ Cleanup complete! Database is ready for fresh signup.' AS Status;
SELECT COUNT(*) AS 'Remaining users' FROM auth_user;
