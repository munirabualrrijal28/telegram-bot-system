# Accessing AWS RDS MySQL Database

## Connection Details

Your RDS MySQL database is hosted on AWS. Here are the connection details:

- **Host**: `bot-management-db.cy32kskg2o9a.us-east-1.rds.amazonaws.com`
- **Port**: `3306`
- **Database Name**: `bot_management_db`
- **Username**: (Check your AWS Console or Environment Variables)
- **Password**: (Check your AWS Console or Environment Variables)

## Option 1: MySQL Workbench (Recommended)

### Step 1: Download MySQL Workbench

If you haven't already, download from: https://dev.mysql.com/downloads/workbench/

### Step 2: Create New Connection

1. Open MySQL Workbench
2. Click the **"+"** button next to "MySQL Connections"
3. Fill in the connection details:
   - **Connection Name**: `AWS RDS - Bot Management`
   - **Hostname**: `bot-management-db.cy32kskg2o9a.us-east-1.rds.amazonaws.com`
   - **Port**: `3306`
   - **Username**: Your RDS username
   - **Password**: Click "Store in Vault" and enter your RDS password
4. Click **"Test Connection"**
   - If successful, click **OK** to save
   - If it fails, see troubleshooting below

### Step 3: Open Connection

1. Double-click the connection you just created
2. You should see the `bot_management_db` database in the left sidebar
3. You can now browse tables, run queries, and view data

## Option 2: Command Line (mysql client)

```bash
mysql -h bot-management-db.cy32kskg2o9a.us-east-1.rds.amazonaws.com -P 3306 -u YOUR_USERNAME -p bot_management_db
```

Enter your password when prompted.

## Troubleshooting

### Connection Timeout / Cannot Connect

**Cause**: Your IP address is not allowed in the RDS Security Group.

**Solution**:

1. Go to **AWS Console** → **RDS** → **Databases** → Click your database
2. Scroll down to **"Security group rules"**
3. Click on the security group link (e.g., `sg-xxxxx`)
4. Click **"Edit inbound rules"**
5. Click **"Add rule"**:
   - **Type**: `MySQL/Aurora`
   - **Port**: `3306`
   - **Source**: `My IP` (automatically detects your current IP)
   - OR use `0.0.0.0/0` (Anywhere) for testing (⚠️ NOT recommended for production)
6. Click **"Save rules"**
7. Try connecting again

### "Access Denied" Error

**Cause**: Incorrect username or password.

**Solution**:

- Verify credentials in your AWS Console:
  1. Go to **Elastic Beanstalk** → **bot-management-prod** → **Configuration** → **Software**
  2. Check `DB_USER` and `DB_PASSWORD` environment variables
- OR reset the RDS password:
  1. Go to **RDS** → **Databases** → Select your database
  2. Click **"Modify"**
  3. Scroll to **"Database authentication"** section
  4. Enter new master password
  5. Click **"Continue"** → **"Apply immediately"** → **"Modify DB instance"**

## Useful Queries

### View all tables

```sql
SHOW TABLES;
```

### View users

```sql
SELECT * FROM auth_user;
```

### View workspaces

```sql
SELECT * FROM core_workspace;
```

### View Telegram users

```sql
SELECT * FROM core_telegramuser;
```

### View table structure

```sql
DESCRIBE table_name;
```

## Notes

- Your local MySQL Workbench connects directly to the AWS RDS instance
- Any changes you make in Workbench will affect the production database
- **Always be careful when modifying production data!**
- For backups, consider using AWS RDS automated backups (configured in RDS console)
