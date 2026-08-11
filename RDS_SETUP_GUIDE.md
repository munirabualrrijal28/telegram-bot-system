# RDS MySQL - Remaining Configuration Settings

## VPC Security Group (Firewall)

- ✅ Select: **Create new**
- **New VPC security group name**: `bot-management-db-sg` ✅ (keep exactly as you typed)

## Availability Zone

- ✅ Select: **No preference** (let AWS choose)

## RDS Proxy

- ❌ **Do NOT enable** (leave unchecked - adds extra cost and complexity)

## Certificate Authority

- ✅ Leave as: **rds-ca-rsa2048-g1 (default)** (it's fine)

## Additional Configuration

### Database Port

- ✅ Keep as: **3306** (MySQL default, don't change)

### Monitoring

- **Database Insights**: ❌ **Do NOT select** (leave unchecked - costs extra)
- **Enhanced Monitoring**: ❌ **Disable** (uncheck "Enable Enhanced monitoring")
- **Log exports**: ❌ **Don't check any boxes** (all logs disabled to save money)

### Database Options

- **Initial database name**: ✅ **`bot_management_db`** ⚠️ CRITICAL! Type this exactly!
- **DB parameter group**: ✅ `default.mysql8.0` (keep as is)
- **Option group**: ✅ `default:mysql-8-0` (keep as is)

### Backup

- **Enable automated backup**: ✅ **Checked** (keep enabled)
- **Backup retention period**: ✅ **7 days** (already set correctly)
- **Backup window**: ✅ **No preference**
- **Copy tags to automated backup**: ❌ Uncheck (optional)
- **Copy tags to snapshots**: ❌ Uncheck (optional)
- **Backup replication**: ❌ **Do NOT enable** (not needed, costs extra)

### Encryption

- **Enable encryption**: ✅ **Checked** (keep enabled - it's free and secure)
- **AWS KMS key**: ✅ `(default) aws/rds` (keep as is)

### Maintenance

- **Auto minor version upgrade**: ✅ **Enable** (check the box - gets security patches)
- **Maintenance window**: ✅ **No preference** (let AWS choose)

### Deletion Protection

- ❌ **Do NOT enable** (uncheck) - makes it easier to delete if you need to recreate

## Final Checklist Before Clicking "Create Database"

✅ Engine: MySQL 8.0.40
✅ Template: Dev/Test or Sandbox
✅ Availability: Single-AZ
✅ Instance: db.t3.micro or db.t4g.micro
✅ Storage: General Purpose SSD (gp3), 20 GiB
✅ Public access: Yes
✅ Security group: Create new (bot-management-db-sg)
✅ Initial database name: **bot_management_db**
✅ Monitoring: ALL DISABLED
✅ Deletion protection: DISABLED
✅ Estimated cost: ~$15-25/month (NOT $946!)

## After Clicking "Create Database"

1. **Wait 5-10 minutes** - Database status will change from "Creating" to "Available"

2. **Get the connection details**:
   - Click on your database name: `bot-management-db`
   - Under "Connectivity & security":
     - Copy **Endpoint**: `bot-management-db.xxxxx.us-east-1.rds.amazonaws.com`
     - Note **Port**: `3306`
   - Under "Configuration":
     - Master username: `admin`
     - Password: (the one you created/generated)

3. **Fix Security Group** (IMPORTANT!):
   - Go to **VPC** → **Security Groups**
   - Find `bot-management-db-sg`
   - Click **Edit inbound rules**
   - Click **Add rule**:
     - Type: **MySQL/Aurora** (port 3306 auto-fills)
     - Source: **Anywhere-IPv4** (`0.0.0.0/0`) - for now
     - Click **Save rules**

4. **Save these for later**:
   ```
   DB_ENGINE="django.db.backends.mysql"
   DB_NAME="bot_management_db"
   DB_USER="admin"
   DB_PASSWORD="<your password>"
   DB_HOST="<your endpoint from step 2>"
   DB_PORT="3306"
   ```

## Next Steps

Once RDS is created and you have the endpoint:

1. Create S3 bucket for media files
2. Set all environment variables in EB
3. Deploy your application
