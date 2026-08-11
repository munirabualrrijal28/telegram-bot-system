-- Fix: Manually create Workspace and TelegramUser for user "amv"
USE bot_management_db;

-- Generate a UUID for workspace (you can change this if needed)
SET @workspace_uuid = UUID();
SET @telegram_user_uuid = UUID();

-- Step 1: Create Workspace for user "amv" (owner_id = 1)
INSERT INTO workspace (id, owner_id, name, address, contact_phone, contact_email, created_at, updated_at)
VALUES (
    @workspace_uuid,
    1,  -- amv's user id
    "AMV LORD28's Workspace",
    'To be updated',
    '',
    'moneermoneer28@gmail.com',
    NOW(),
    NOW()
);

-- Step 2: Create TelegramUser profile for user "amv"
INSERT INTO telegram_user (id, user_id, name, email, role, status, workspace_id, has_used_free_trial, created_at, updated_at)
VALUES (
    @telegram_user_uuid,
    1,  -- amv's user id
    'AMV LORD28',
    'moneermoneer28@gmail.com',
    'owner',
    'active',
    @workspace_uuid,  -- Link to the workspace we just created
    0,
    NOW(),
    NOW()
);

-- Step 3: Verify the records were created
SELECT '✅ Workspace created:' AS Status;
SELECT * FROM workspace WHERE owner_id = 1;

SELECT '✅ TelegramUser created:' AS Status;
SELECT * FROM telegram_user WHERE user_id = 1;

SELECT '✅ You can now access the dashboard!' AS Message;
