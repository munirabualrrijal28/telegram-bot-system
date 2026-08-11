# Getting RDS Connection Details

## Step 1: Get Database Endpoint

1. **Click on your database name**: `bot-management-db` (in the list)

2. On the database details page, find the **"Connectivity & security"** tab

3. Copy these values:

   **Endpoint**:
   - Look for "Endpoint" (should be something like):
   - `bot-management-db.xxxxxxxxxxxxx.us-east-1.rds.amazonaws.com`
   - ⚠️ **Copy this entire endpoint - you'll need it!**

   **Port**:
   - Should show: `3306`

4. Under **"Configuration"** tab:
   - Master username: `admin`
   - (You already have the password you created)

## Step 2: Fix Security Group

The security group `bot-management-db-sg` was created but doesn't have the correct rules yet.

1. In the **"Connectivity & security"** section, find **"VPC security groups"**
2. Click on the security group name (should be `bot-management-db-sg`)
3. This opens the security group page
4. Click **"Edit inbound rules"**
5. Click **"Add rule"**:
   - Type: **MySQL/Aurora** (this auto-fills Port 3306)
   - Source: **Anywhere-IPv4** (`0.0.0.0/0`)
     - ⚠️ This allows connections from anywhere - for production, you'd restrict this to your EB security group
     - For now, this is fine to get it working
6. Click **"Save rules"**

## Step 3: Save Your Database Credentials

Create a text file or note with these values (you'll need them in a minute):

```
DB_ENGINE=django.db.backends.mysql
DB_NAME=bot_management_db
DB_USER=admin
DB_PASSWORD=<your password from RDS creation>
DB_HOST=<endpoint you copied in Step 1>
DB_PORT=3306
```

## Next: Create S3 Bucket

After you have the endpoint, we'll:

1. Create S3 bucket for static/media files
2. Set all environment variables in EB
3. Deploy your application with proper production config
