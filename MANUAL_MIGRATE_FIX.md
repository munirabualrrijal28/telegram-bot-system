# Quick Fix: Manually Run Migrations on AWS

## Option 1: SSH into Elastic Beanstalk and Run Migrations (Recommended)

### Step 1: Enable SSH (if not already enabled)

```bash
# From your local project directory
eb ssh --setup
```

### Step 2: SSH into the instance

```bash
eb ssh
```

### Step 3: Navigate to app directory

```bash
cd /var/app/current
```

### Step 4: Activate virtual environment

```bash
source /var/app/venv/*/bin/activate
```

### Step 5: Run migrations

```bash
python manage.py migrate
```

Expected output:

```
Running migrations:
  Applying sites.0001_initial... OK
  Applying sites.0002_alter_domain_unique... OK
  ...
```

### Step 6: Exit SSH

```bash
exit
```

---

## Option 2: Create Site Record via MySQL Workbench (Quick Workaround)

If SSH doesn't work, you can manually create the table using MySQL Workbench:

### Step 1: Connect to RDS

Use the connection details from `RDS_ACCESS_GUIDE.md`

### Step 2: Run this SQL

```sql
-- Create django_site table
CREATE TABLE IF NOT EXISTS django_site (
    id INT AUTO_INCREMENT PRIMARY KEY,
    domain VARCHAR(100) NOT NULL UNIQUE,
    name VARCHAR(50) NOT NULL
);

-- Insert default site
INSERT INTO django_site (id, domain, name) VALUES (1, 'mytelebot.com', 'My Telebot');
```

### Step 3: Verify

```sql
SELECT * FROM django_site;
```

Should show:

```
| id | domain         | name         |
|----|----------------|--------------|
| 1  | mytelebot.com  | My Telebot   |
```

---

## Option 3: Force Migrations via EB Console

### Step 1: Go to AWS Console

https://console.aws.amazon.com/elasticbeanstalk

### Step 2: Select Environment

Click `bot-management-prod`

### Step 3: Run Command

- Go to **Configuration** → **Software** → **Edit**
- Scroll to **Container commands**
- Or Go to **Environment actions** → **Restart app server**

### Step 4: Check Logs

```bash
eb logs
```

Look for migration output.

---

## Why Migrations Didn't Run Automatically

**Check `.ebextensions/01_django.config`:**

It should contain:

```yaml
container_commands:
  01_migrate:
    command: "source /var/app/venv/*/bin/activate && python manage.py migrate"
    leader_only: true
```

If this file is missing or incorrect:

1. Migrations won't run on deployment
2. You'll need to manually run them using Option 1 or 2 above

---

## After Running Migrations

The login page should work! Try:

- https://mytelebot.com/owner/login/

Both email/password login AND Google OAuth should now function correctly.
