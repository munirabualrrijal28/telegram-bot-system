-- Delete incomplete user account "amv" and start fresh
-- Run this to clean up the failed signup attempt

USE bot_management_db;

-- Step 1: Delete any social accounts linked to user "amv" (id=1)
DELETE FROM socialaccount_socialtoken WHERE account_id IN (
    SELECT id FROM socialaccount_socialaccount WHERE user_id = 1
);

DELETE FROM socialaccount_socialaccount WHERE user_id = 1;

-- Step 2: Delete any email addresses
DELETE FROM account_emailaddress WHERE user_id = 1;

-- Step 3: Delete telegram_user (if exists)
DELETE FROM telegram_user WHERE user_id = 1;

-- Step 4: Delete workspace (if exists)
DELETE FROM workspace WHERE owner_id = 1;

-- Step 5: Delete the Django user
DELETE FROM auth_user WHERE id = 1;

-- Step 6: Verify everything is deleted
SELECT '✅ User account deleted. You can now sign up again!' AS Status;

SELECT 'Remaining users:' AS Info;
SELECT * FROM auth_user;

SELECT 'If no rows above, database is clean!' AS Message;
