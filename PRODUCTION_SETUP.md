# Production Deployment Setup - Proper Configuration

## Your Requirements ✅

- Database: MySQL (RDS) - matching your local setup
- Storage: S3 for static/media files
- Domain: Custom domain (you own)
- Proper production setup

## Step 1: Create RDS MySQL Database

### Via AWS Console (Recommended):

1. Go to **RDS Console**: https://console.aws.amazon.com/rds
2. Click **Create database**
3. Choose:
   - Engine: **MySQL 8.0**
   - Template: **Free tier** (or Production for production)
   - DB instance identifier: `bot-management-db`
   - Master username: `admin`
   - Master password: (create strong password, save it!)
   - DB instance class: `db.t3.micro` (free tier)
   - Storage: 20 GB
   - VPC: **Same as your EB environment** (important!)
   - Public access: **No**
   - Database name: `bot_management_db` (matches your local)
4. Click **Create database**
5. Wait 5-10 minutes for creation
6. Note down the **Endpoint** (e.g., `bot-management-db.xxxxx.us-east-1.rds.amazonaws.com`)

### Via AWS CLI (Alternative):

```bash
aws rds create-db-instance \
  --db-instance-identifier bot-management-db \
  --db-instance-class db.t3.micro \
  --engine mysql \
  --master-username admin \
  --master-user-password YourStrongPassword123 \
  --allocated-storage 20 \
  --db-name bot_management_db \
  --vpc-security-group-ids sg-xxxxx
```

## Step 2: Create S3 Bucket

### Via AWS Console:

1. Go to **S3 Console**: https://console.aws.amazon.com/s3
2. Click **Create bucket**
3. Bucket name: `bot-management-media` (must be globally unique)
4. Region: **us-east-1** (same as EB)
5. Uncheck "Block all public access" (needed for static files)
6. Click **Create bucket**

### Configure CORS:

1. Click on your bucket → **Permissions** → **CORS**
2. Add this configuration:

```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "HEAD"],
    "AllowedOrigins": ["*"],
    "ExposeHeaders": []
  }
]
```

### Create IAM User for S3 Access:

1. Go to **IAM Console**: https://console.aws.amazon.com/iam
2. **Users** → **Create user**
3. User name: `bot-management-s3-user`
4. Click **Next**
5. Attach policy: **AmazonS3FullAccess** (or create custom policy)
6. Click **Create user**
7. **Security credentials** → **Create access key**
8. Choose **Application running outside AWS**
9. Note down:
   - **Access key ID**
   - **Secret access key** (won't be shown again!)

## Step 3: Proper Environment Variables

Once RDS and S3 are ready, set these environment variables:

```bash
eb setenv \
  SECRET_KEY="+f#2_n_9b0-9-5*fqqb+3g9!)xg(fbi@043hpgmutek1kmhy" \
  DEBUG="False" \
  ALLOWED_HOSTS=".elasticbeanstalk.com,yourdomain.com,www.yourdomain.com" \
  USE_S3="True" \
  AWS_ACCESS_KEY_ID="YOUR_ACCESS_KEY_ID" \
  AWS_SECRET_ACCESS_KEY="YOUR_SECRET_ACCESS_KEY" \
  AWS_STORAGE_BUCKET_NAME="bot-management-media" \
  AWS_S3_REGION_NAME="us-east-1" \
  DB_ENGINE="django.db.backends.mysql" \
  DB_NAME="bot_management_db" \
  DB_USER="admin" \
  DB_PASSWORD="YourRDSPassword" \
  DB_HOST="bot-management-db.xxxxx.us-east-1.rds.amazonaws.com" \
  DB_PORT="3306" \
  GOOGLE_OAUTH_CLIENT_ID="your_google_client_id" \
  GOOGLE_OAUTH_CLIENT_SECRET="your_google_secret" \
  CSRF_TRUSTED_ORIGINS="https://your-eb-url.elasticbeanstalk.com,https://yourdomain.com"
```

## Step 4: Update Requirements for MySQL

Your current `requirements-minimal.txt` needs `PyMySQL` (already included). But for better performance with MySQL, add:

```txt
# requirements.txt
Django==5.1.4
gunicorn==22.0.0
whitenoise==6.8.2
psycopg2-binary==2.9.9
PyMySQL==1.1.1
cryptography  # Required by PyMySQL for secure connections
boto3==1.35.0
django-storages==1.14.4
Pillow==10.4.0
requests==2.32.3
django-allauth==65.3.0
```

## Step 5: Update settings.py for MySQL

Your `settings.py` already supports this! It checks for `DB_ENGINE` environment variable:

```python
DATABASES = {
    'default': {
        'ENGINE': get_env('DB_ENGINE', default='django.db.backends.mysql'),
        'NAME': get_env('DB_NAME', default='bot_management_db'),
        'USER': get_env('DB_USER', default='bot_user'),
        'PASSWORD': get_env('DB_PASSWORD'),
        'HOST': get_env('DB_HOST', default='127.0.0.1'),
        'PORT': get_env('DB_PORT', default='3306'),
        'OPTIONS': {
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"
        }
    }
}
```

##Step 6: Deploy with Migrations

Once environment is created and environment variables are set:

1. **Restore migrations** to `.ebextensions/01_django.config`:

```yaml
option_settings:
  aws:elasticbeanstalk:application:environment:
    DJANGO_SETTINGS_MODULE: "bot_management_system.settings"
    PYTHONPATH: "/var/app/current:$PYTHONPATH"
  aws:elasticbeanstalk:container:python:
    WSGIPath: "bot_management_system.wsgi:application"

container_commands:
  01_migrate:
    command: "source /var/app/venv/*/bin/activate && python manage.py migrate --noinput"
    leader_only: true
  02_collectstatic:
    command: "source /var/app/venv/*/bin/activate && python manage.py collectstatic --noinput"
    leader_only: true
  03_createsu:
    command: "source /var/app/venv/*/bin/activate && python manage.py createsu"
    leader_only: true
    ignoreErrors: true
```

2. **Deploy**:

```bash
eb deploy
```

## Step 7: Custom Domain Setup

1. **Get SSL Certificate** (AWS Certificate Manager):
   - Go to ACM Console
   - Request certificate for `yourdomain.com` and `*.yourdomain.com`
   - Validate via DNS or email

2. **Configure EB Environment**:

   ```bash
   eb create --cname yourdomain  # If creating new
   # Or configure existing via EB Console
   ```

3. **Update DNS**:
   - In your domain registrar, add CNAME:
   - `www.yourdomain.com` → `bot-management-v2.us-east-1.elasticbeanstalk.com`
   - Or use Route 53 for better AWS integration

## Quick Reference Commands

```bash
# 1. Wait for current eb create to finish or terminate it

# 2. Set ALL environment variables at once
eb setenv SECRET_KEY="..." DEBUG="False" ALLOWED_HOSTS="..." USE_S3="True" AWS_ACCESS_KEY_ID="..." AWS_SECRET_ACCESS_KEY="..." AWS_STORAGE_BUCKET_NAME="..." DB_ENGINE="django.db.backends.mysql" DB_NAME="bot_management_db" DB_USER="admin" DB_PASSWORD="..." DB_HOST="your-rds-endpoint.rds.amazonaws.com" DB_PORT="3306"

# 3. Deploy
eb deploy

# 4. Check health
eb health

# 5. Open app
eb open
```

## Summary

The SQLite approach I suggested was just to troubleshoot the deployment issues. For production, you should definitely use:

- ✅ RDS MySQL (matching your local setup)
- ✅ S3 for media/static files
- ✅ Your custom domain with SSL
- ✅ Proper environment variables
