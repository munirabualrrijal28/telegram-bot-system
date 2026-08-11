# CRITICAL FIX: Enable SSH and Run Migrations

## Current Status

- Environment: **Degraded** (1 severe instance)
- Database: SQLite configured ✅
- Issue: Migrations not run yet, SSH not enabled

## Root Cause

Django applications require database migrations to be run before they can serve requests. The database tables don't exist yet, causing 5xx errors.

## Solution

### Option 1: Enable SSH and Run Migrations (Recommended)

1. **Rebuild environment with SSH enabled**:

   ```bash
   eb init
   # When prompted "Do you want to set up SSH for your instances?" → Select YES
   # Choose or create a keypair
   ```

2. **Apply the SSH configuration**:

   ```bash
   eb deploy
   ```

3. **SSH into the instance**:

   ```bash
   eb ssh
   ```

4. **Run migrations inside the instance**:

   ```bash
   source /var/app/venv/*/bin/activate
   cd /var/app/current

   # Run migrations
   python manage.py migrate

   # Create superuser (will prompt for password)
   python manage.py createsuperuser

   # Restart the web server
   sudo systemctl restart web

   exit
   ```

5. **Check health**:
   ```bash
   eb health
   eb open
   ```

### Option 2: Add Migration Hook to .ebextensions (Alternative)

If you can't enable SSH, we can add a post-deployment hook:

1. Update `.ebextensions/01_django.config` to add migrations
2. Deploy again

But this requires the database to be accessible, which might still fail.

### Option 3: Use RDS Instead of SQLite (Production-Ready)

SQLite on EB is problematic because:

- File doesn't persist across deployments
- Not suitable for multi-instance setups
- Gets reset on every deploy

**Recommended**: Set up RDS PostgreSQL:

1. Create RDS instance in AWS Console
2. Set environment variables:
   ```bash
   eb setenv RDS_DB_NAME="your_db" RDS_USERNAME="user" RDS_PASSWORD="pass" RDS_HOSTNAME="endpoint.rds.amazonaws.com" RDS_PORT="5432"
   ```
3. Deploy
4. SSH and run migrations

## Quick Fix Command Sequence

```bash
# 1. Re-initialize with SSH
eb init
# Select: Yes for SSH, choose/create keypair

# 2. Deploy
eb deploy

# 3. SSH and migrate
eb ssh
source /var/app/venv/*/bin/activate && cd /var/app/current
python manage.py migrate --noinput
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else None" | python manage.py shell
sudo systemctl restart web
exit

# 4. Verify
eb health
eb open
```

## What to Expect

After running migrations:

- Health should change from **Degraded/Severe** → **Ok/Green**
- Application should load without 5xx errors
- You can access `/admin/` with the superuser credentials

## Next Steps After Success

1. ✅ Migrations run
2. Set up RDS for persistent database
3. Configure S3 for static files
4. Update Google OAuth credentials
5. Test all functionality
