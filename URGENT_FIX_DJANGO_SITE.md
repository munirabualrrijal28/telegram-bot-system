# URGENT FIX: Create django_site Table via MySQL Workbench

Your environment is currently in "Severe" status and SSH isn't working yet.
**The fastest fix is to use MySQL Workbench directly.**

## Step-by-Step Instructions

### 1. Find Your RDS Password

Run this command to see your environment variables:

```bash
eb printenv
```

Look for:

```
DB_USER = admin
DB_PASSWORD = your-password-here
DB_HOST = bot-management-db.cy32kskg2o9a.us-east-1.rds.amazonaws.com
```

### 2. Open MySQL Workbench

- Click **"+"** next to "MySQL Connections"
- Enter:
  - **Connection Name**: AWS RDS Bot Management
  - **Hostname**: `bot-management-db.cy32kskg2o9a.us-east-1.rds.amazonaws.com`
  - **Port**: `3306`
  - **Username**: `admin` (from step 1)
  - **Password**: Click "Store in Vault..." and enter password from step 1
  - **Default Schema**: `bot_management_db`

### 3. Test Connection

Click **"Test Connection"**

- ✅ If successful → Click **OK**
- ❌ If fails → Check Security Group (see Troubleshooting below)

### 4. Connect and Run SQL

1. Double-click your connection
2. Click the **SQL Editor** tab
3. Paste this SQL:

```sql
-- Select the correct database
USE bot_management_db;

-- Create django_site table
CREATE TABLE IF NOT EXISTS django_site (
    id INT AUTO_INCREMENT PRIMARY KEY,
    domain VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(50) NOT NULL
);

-- Insert the required site record
INSERT INTO django_site (id, domain, name)
VALUES (1, 'mytelebot.com', 'My Telebot')
ON DUPLICATE KEY UPDATE
    domain = 'mytelebot.com',
    name = 'My Telebot';

-- Verify it was created
SELECT * FROM django_site;

-- Also check what other tables exist
SHOW TABLES LIKE 'django%';
```

4. Click **Execute** (⚡ lightning bolt icon)

### 5. Verify Results

You should see:

```
Query OK, 1 row affected

id | domain         | name
---|----------------|-------------
1  | mytelebot.com  | My Telebot
```

### 6. Test Your Website

Go to: `https://mytelebot.com/owner/login/`

The error should be gone! ✅

---

## Troubleshooting

### Can't Connect to RDS

**Error**: "Can't connect to MySQL server"

**Fix**: Add your IP to RDS Security Group

1. Go to AWS Console → **EC2** → **Security Groups**
2. Find `bot-management-db-sg`
3. **Inbound Rules** → **Edit**
4. **Add Rule**:
   - Type: `MySQL/Aurora`
   - Port: `3306`
   - Source: **My IP** (auto-detects)
5. **Save**

Try connecting again!

---

## After This Fix

Once the table is created, your environment should recover from "Severe" status.

**Check health:**

```bash
eb health
```

**If still Severe**, check logs:

```bash
eb logs --all > logs.txt
```

Send me the logs and I'll help debug!
