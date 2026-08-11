# AWS Elastic Beanstalk Deployment Guide

This guide provides step-by-step instructions for deploying the Bot Management System to AWS Elastic Beanstalk.

## Prerequisites

Before deploying, ensure you have:

1. **AWS Account** with appropriate permissions
2. **AWS EB CLI** installed ([Installation Guide](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3-install.html))
3. **Python 3.9+** installed locally
4. **Git** installed (for version control)

## AWS Services Setup

### 1. Create an S3 Bucket

1. Go to AWS S3 Console
2. Click "Create bucket"
3. Choose a unique bucket name (e.g., `bot-management-static-files`)
4. Select your preferred region
5. **Uncheck** "Block all public access" (static files need to be publicly accessible)
6. Create the bucket
7. Under "Permissions" → "CORS configuration", add:

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

### 2. Create an RDS PostgreSQL Database

1. Go to AWS RDS Console
2. Click "Create database"
3. Choose **PostgreSQL**
4. Select **Free tier** (if applicable) or appropriate instance size
5. Configure:
   - DB instance identifier: `bot-management-db`
   - Master username: `postgres` (or your choice)
   - Master password: (set a strong password)
6. Under "Connectivity":
   - Choose "Yes" for public accessibility (for initial setup)
   - Create a new VPC security group or use existing
7. Create database
8. **Note down**: endpoint, port, username, and password

### 3. Configure IAM Permissions

Your Elastic Beanstalk instance needs permissions to access S3:

1. Go to IAM Console → Roles
2. Find the role `aws-elasticbeanstalk-ec2-role` (created during EB setup)
3. Attach policy: `AmazonS3FullAccess` (or create a custom policy with specific bucket access)

## Project Preparation

### 1. Install Dependencies Locally

```bash
cd "d:\Desktop Projects 2025\bot_management_system"
.\django_env\Scripts\activate
pip install -r requirements.txt
```

### 2. Create Environment File

Copy `.env.example` to `.env` and configure for local testing:

```bash
cp .env.example .env
```

Edit `.env` with your local settings:

```env
SECRET_KEY=your-new-secret-key-generate-one
DEBUG=False
ALLOWED_HOSTS=127.0.0.1,localhost
USE_S3=False
# ... other settings
```

Generate a new SECRET_KEY:

```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 3. Test Locally (Optional but Recommended)

```bash
# Collect static files
python manage.py collectstatic --noinput

# Run with production settings
python manage.py check --deploy

# Test the server
gunicorn bot_management_system.wsgi
```

Visit `http://localhost:8000` to verify everything works.

## Elastic Beanstalk Deployment

### 1. Initialize EB Application

```bash
cd "d:\Desktop Projects 2025\bot_management_system"
eb init
```

Follow the prompts:

- **Region**: Choose your preferred AWS region (e.g., us-east-1)
- **Application name**: `bot-management-system`
- **Platform**: Python
- **Platform version**: Python 3.11 (or latest available)
- **SSH**: Yes (recommended for debugging)

### 2. Create EB Environment

```bash
eb create bot-management-env
```

This will:

- Create a new environment
- Upload your application
- Install dependencies from `requirements.txt`
- Run the Procfile command

**Note**: Initial creation takes 5-10 minutes.

### 3. Configure Environment Variables

Set environment variables in Elastic Beanstalk:

```bash
# Django settings
eb setenv SECRET_KEY="your-production-secret-key"
eb setenv DEBUG=False
eb setenv ALLOWED_HOSTS=".elasticbeanstalk.com"

# AWS S3
eb setenv USE_S3=True
eb setenv AWS_ACCESS_KEY_ID="your-access-key"
eb setenv AWS_SECRET_ACCESS_KEY="your-secret-key"
eb setenv AWS_STORAGE_BUCKET_NAME="your-bucket-name"
eb setenv AWS_S3_REGION_NAME="us-east-1"

# Google OAuth (update with production credentials)
eb setenv GOOGLE_OAUTH_CLIENT_ID="your-client-id"
eb setenv GOOGLE_OAUTH_CLIENT_SECRET="your-client-secret"

# Security
eb setenv CSRF_TRUSTED_ORIGINS="https://your-eb-url.elasticbeanstalk.com"
```

**For RDS Database**, Elastic Beanstalk automatically sets these when you attach RDS:

- `RDS_DB_NAME`
- `RDS_USERNAME`
- `RDS_PASSWORD`
- `RDS_HOSTNAME`
- `RDS_PORT`

### 4. Attach RDS Database to Environment

Option A: Via Console (Recommended for production)

1. Go to Elastic Beanstalk Console
2. Select your environment
3. Configuration → Database
4. Edit and select your existing RDS instance

Option B: Via CLI (for new database)

```bash
eb create --database.engine postgres --database.username dbuser --database.password yourpassword
```

### 5. Update Security Groups

After attaching RDS:

1. Go to RDS Console → Your database → Connectivity & Security
2. Click on the VPC security group
3. Add inbound rule:
   - Type: PostgreSQL
   - Port: 5432
   - Source: The Elastic Beanstalk security group

### 6. Deploy Application

```bash
eb deploy
```

### 7. Run Database Migrations

SSH into your instance and run migrations:

```bash
eb ssh
source /var/app/venv/*/bin/activate
cd /var/app/current
python manage.py migrate
python manage.py createsuperuser  # Create admin user
exit
```

Or create a custom management command for superuser creation (already configured in `.ebextensions/01_django.config`).

### 8. Verify Deployment

```bash
# Check application health
eb health

# View logs
eb logs

# Open application in browser
eb open
```

## Post-Deployment Tasks

### 1. Configure Google OAuth

Update your Google OAuth settings:

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. Select your project
3. APIs & Services → Credentials
4. Edit your OAuth 2.0 Client ID
5. Add authorized redirect URIs:
   - `https://your-eb-url.elasticbeanstalk.com/accounts/google/login/callback/`

### 2. Configure Custom Domain (Optional)

1. In Route 53, create a CNAME record pointing to your EB environment
2. Update `ALLOWED_HOSTS` and `CSRF_TRUSTED_ORIGINS`:
   ```bash
   eb setenv ALLOWED_HOSTS=".elasticbeanstalk.com,yourdomain.com"
   eb setenv CSRF_TRUSTED_ORIGINS="https://your-eb-url.elasticbeanstalk.com,https://yourdomain.com"
   ```

### 3. Set Up SSL Certificate (Recommended)

1. Request a certificate in AWS Certificate Manager
2. In EB Console → Configuration → Load Balancer
3. Add listener on port 443 with your SSL certificate
4. Update security settings to redirect HTTP to HTTPS

## Maintenance & Updates

### Deploy New Changes

```bash
# Make code changes
git add .
git commit -m "Update description"

# Deploy to EB
eb deploy
```

### View Logs

```bash
# View recent logs
eb logs

# Tail logs in real-time
eb logs --stream
```

### Scale Application

```bash
# Scale to 2 instances
eb scale 2
```

### Update Environment Variables

```bash
eb setenv VARIABLE_NAME="new-value"
```

## Troubleshooting

### Static Files Not Loading

1. Verify S3 bucket permissions
2. Check AWS credentials in environment variables
3. Run collectstatic manually:
   ```bash
   eb ssh
   source /var/app/venv/*/bin/activate
   python manage.py collectstatic --noinput
   ```

### Database Connection Errors

1. Verify RDS security group allows connections from EB
2. Check environment variables: `eb printenv`
3. Verify RDS instance is running

### Application Won't Start

1. Check logs: `eb logs`
2. Verify all dependencies in `requirements.txt`
3. Ensure `Procfile` is correct
4. Check migrations are applied

### 500 Internal Server Error

1. Set `DEBUG=True` temporarily to see detailed errors
2. Check logs: `eb logs`
3. Verify all environment variables are set
4. Check database connectivity

## Environment Variables Reference

| Variable                     | Description                       | Example                                    |
| ---------------------------- | --------------------------------- | ------------------------------------------ |
| `SECRET_KEY`                 | Django secret key                 | `django-insecure-xyz...`                   |
| `DEBUG`                      | Debug mode (False for production) | `False`                                    |
| `ALLOWED_HOSTS`              | Allowed hostnames                 | `.elasticbeanstalk.com,example.com`        |
| `USE_S3`                     | Enable S3 storage                 | `True`                                     |
| `AWS_ACCESS_KEY_ID`          | AWS access key                    | `AKIAIOSFODNN7EXAMPLE`                     |
| `AWS_SECRET_ACCESS_KEY`      | AWS secret key                    | `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY` |
| `AWS_STORAGE_BUCKET_NAME`    | S3 bucket name                    | `my-bucket`                                |
| `AWS_S3_REGION_NAME`         | S3 region                         | `us-east-1`                                |
| `GOOGLE_OAUTH_CLIENT_ID`     | Google OAuth client ID            | `123456789.apps.googleusercontent.com`     |
| `GOOGLE_OAUTH_CLIENT_SECRET` | Google OAuth secret               | `GOCSPX-...`                               |
| `CSRF_TRUSTED_ORIGINS`       | Trusted CSRF origins              | `https://example.com`                      |

RDS variables (auto-set by EB):

- `RDS_DB_NAME`
- `RDS_USERNAME`
- `RDS_PASSWORD`
- `RDS_HOSTNAME`
- `RDS_PORT`

## Backup & Disaster Recovery

### Database Backups

1. Enable automated backups in RDS (default is enabled)
2. Set backup retention period (recommended: 7-30 days)
3. Take manual snapshots before major updates

### Code Backups

Use Git for version control:

```bash
git push origin main
```

## Cost Optimization

1. **Use Free Tier** (if eligible): t2.micro instance, RDS free tier
2. **Auto Scaling**: Set min=1, max=2 for small apps
3. **Right-size Instances**: Monitor and adjust instance types
4. **S3 Lifecycle Policies**: Archive old media files to Glacier
5. **Delete Unused Resources**: Remove old EB environments

## Security Best Practices

1. ✅ Never commit `.env` file or credentials to Git
2. ✅ Use IAM roles instead of access keys when possible
3. ✅ Enable RDS encryption at rest
4. ✅ Use SSL/HTTPS for all traffic
5. ✅ Regularly update dependencies
6. ✅ Enable AWS CloudWatch for monitoring
7. ✅ Set up CloudWatch alarms for errors and high CPU
8. ✅ Restrict RDS access to EB security group only

## Additional Resources

- [Elastic Beanstalk Python Guide](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-django.html)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/stable/howto/deployment/checklist/)
- [AWS S3 with Django](https://django-storages.readthedocs.io/en/latest/backends/amazon-S3.html)
- [EB CLI Reference](https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/eb-cli3.html)
