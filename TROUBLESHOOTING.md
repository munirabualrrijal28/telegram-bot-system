# AWS Elastic Beanstalk Deployment Troubleshooting Guide

## Current Issue: Red Health Status

Your environment was created but has **Red health** status. This is typically caused by:

1. ✅ **Fixed**: Invalid package versions in requirements.txt
2. ⚠️ **Current Issue**: Container commands (migrate, collectstatic) failing due to missing environment variables

## Root Cause

The `.ebextensions/01_django.config` was trying to run:

- `python manage.py migrate` - **Fails** without database configuration
- `python manage.py collectstatic` - **Fails** without S3 configuration or STATIC_ROOT setup
- `python manage.py createsu` - **Fails** without database

Since you haven't set environment variables yet (SECRET_KEY, database credentials, S3 credentials), these commands fail during deployment.

## Solution: Two-Phase Deployment

### Phase 1: Deploy Basic Application (CURRENT)

1. **Simplified .ebextensions** (now updated)
   - Removed container commands that require configuration
   - Application will deploy but won't run migrations yet

2. **Deploy the simplified version**:
   ```bash
   eb deploy
   ```

### Phase 2: Configure and Finalize

1. **Generate SECRET_KEY**:

   ```bash
   python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
   ```

2. **Set Environment Variables**:

   ```bash
   eb setenv \
     SECRET_KEY="your-generated-key" \
     DEBUG="False" \
     ALLOWED_HOSTS=".elasticbeanstalk.com" \
     USE_S3="False"
   ```

   **Note**: Setting `USE_S3=False` for initial deployment to avoid S3 requirement.

3. **For Database**: Either attach RDS or use SQLite for testing:

   ```bash
   # Option A: Continue without database (will fail to start)

   # Option B: Attach RDS (recommended)
   # Go to EB Console → Configuration → Database → Edit

   # Option C: Use SQLite temporarily (not recommended for production)
   eb setenv DB_ENGINE="django.db.backends.sqlite3"
   ```

4. **SSH into instance and run migrations manually**:

   ```bash
   eb ssh

   # Inside the instance:
   source /var/app/venv/*/bin/activate
   cd /var/app/current

   # Run migrations
   python manage.py migrate

   # Collect static files
   python manage.py collectstatic --noinput

   # Create superuser
   python manage.py createsuperuser

   # Restart application
   sudo systemctl restart web

   exit
   ```

5. **Check health**:
   ```bash
   eb health
   ```

## Quick Fix: Deploy with Minimal Configuration

Run these commands in order:

```bash
# 1. Generate SECRET_KEY
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# 2. Set minimum environment variables (copy the SECRET_KEY from step 1)
eb setenv SECRET_KEY="paste-your-key-here" DEBUG="False" ALLOWED_HOSTS=".elasticbeanstalk.com" USE_S3="False"

# 3. Deploy again with simplified config
eb deploy

# 4. Wait for deployment (2-3 minutes)
# Monitor with: eb health

# 5. SSH in and run migrations
eb ssh

# Inside instance:
source /var/app/venv/*/bin/activate
cd /var/app/current
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
sudo systemctl restart web
exit

# 6. Test the application
eb open
```

## Alternative: Use RDS Database Immediately

If you have RDS PostgreSQL set up:

```bash
# Set environment variables including RDS
eb setenv \
  SECRET_KEY="your-key" \
  DEBUG="False" \
  ALLOWED_HOSTS=".elasticbeanstalk.com" \
  USE_S3="False" \
  RDS_DB_NAME="your_db_name" \
  RDS_USERNAME="your_user" \
  RDS_PASSWORD="your_password" \
  RDS_HOSTNAME="your-rds-endpoint.rds.amazonaws.com" \
  RDS_PORT="5432"

# Deploy
eb deploy

# Then SSH and run migrations as described above
```

## Checking Logs

To see what went wrong:

```bash
# View recent logs
eb logs

# Or via AWS Console
# Navigate to: EB Console → Environments → bot-management-prod → Logs → Request Logs
```

Look for errors in:

- `/var/log/eb-engine.log`
- `/var/log/web.stdout.log`
- `/var/log/eb-hooks.log`

## Common Errors

### Import Errors (Module Not Found)

- **Cause**: Package installation failed
- **Fix**: Check requirements.txt for invalid versions

### Database Connection Errors

- **Cause**: No database configured
- **Fix**: Set RDS environment variables or use SQLite temporarily

### Static Files Errors

- **Cause**: S3 not configured or STATIC_ROOT missing
- **Fix**: Set `USE_S3=False` initially

### SECRET_KEY Not Set

- **Cause**: Django requires SECRET_KEY
- **Fix**: Generate and set via `eb setenv`

## Next Steps After Fixing

Once the application is running (green health):

1. **Set up S3** for static files:

   ```bash
   eb setenv USE_S3="True" AWS_ACCESS_KEY_ID="..." AWS_SECRET_ACCESS_KEY="..." AWS_STORAGE_BUCKET_NAME="..."
   eb deploy
   ```

2. **Configure Google OAuth** redirect URIs

3. **Set up custom domain** (optional)

4. **Enable SSL** via AWS Certificate Manager

## Re-enable Automated Migrations (Later)

Once everything is working, you can restore the original `.ebextensions/01_django.config` with container commands for automated migrations on future deployments.

## Summary

The current issue is that EB tried to run database migrations before you configured the database. The fix is:

1. ✅ Deploy with simplified config (no container commands)
2. ⏳ Set minimal environment variables
3. ⏳ Deploy again
4. ⏳ SSH in and run migrations manually
5. ⏳ Verify application works
