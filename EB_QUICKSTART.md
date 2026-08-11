# Quick Start: AWS Elastic Beanstalk Deployment

## Prerequisites Checklist

Before running deployment commands, ensure you have:

- [ ] AWS Account with appropriate permissions
- [ ] AWS CLI configured with credentials (`aws configure`)
- [ ] S3 bucket created for static/media files
- [ ] RDS PostgreSQL database created (optional but recommended)
- [ ] Generated a new Django SECRET_KEY

## Deployment Commands

### 1. **Initialize EB Application**

```bash
eb init -p python-3.11 bot-management-system --region us-east-1
```

**Prompts you'll see:**

- Select a region (or use the one specified above)
- Enter application name: `bot-management-system`
- Do you want to set up SSH: **Yes** (recommended)

### 2. **Create Load-Balanced Environment**

```bash
eb create bot-management-prod --elb-type application --scale 1 --instance_type t3.micro
```

**What this does:**

- Creates environment named `bot-management-prod`
- Sets up Application Load Balancer
- Starts with 1 `t3.micro` instance
- Waits 5-10 minutes for completion

**Monitor progress:**

```bash
eb status
eb health
```

### 3. **Generate Django SECRET_KEY**

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output for the next step.

### 4. **Set Environment Variables**

**Option A: All at once (recommended)**

```bash
eb setenv \
  SECRET_KEY="paste-your-generated-key-here" \
  DEBUG="False" \
  ALLOWED_HOSTS=".elasticbeanstalk.com" \
  USE_S3="True" \
  AWS_ACCESS_KEY_ID="your-aws-key" \
  AWS_SECRET_ACCESS_KEY="your-aws-secret" \
  AWS_STORAGE_BUCKET_NAME="your-bucket-name" \
  AWS_S3_REGION_NAME="us-east-1" \
  GOOGLE_OAUTH_CLIENT_ID="your-client-id" \
  GOOGLE_OAUTH_CLIENT_SECRET="your-client-secret" \
  CSRF_TRUSTED_ORIGINS="https://your-app.elasticbeanstalk.com"
```

**Option B: Via Console**

- Go to AWS EB Console → Your Environment → Configuration → Software → Edit
- Add each variable under "Environment properties"

### 5. **Attach RDS Database** (if not done during creation)

**Via Console (recommended):**

1. EB Console → Your Environment → Configuration → Database
2. Select your existing RDS instance

**Via CLI (creates new database):**

```bash
eb create bot-management-prod \
  --elb-type application \
  --scale 1 \
  --instance_type t3.micro \
  --database.engine postgres \
  --database.username dbadmin \
  --database.password YourSecurePassword123
```

### 6. **Deploy Application**

```bash
eb deploy
```

### 7. **Run Post-Deployment Commands**

SSH into your instance:

```bash
eb ssh
```

Inside the instance:

```bash
source /var/app/venv/*/bin/activate
cd /var/app/current

# Run migrations
python manage.py migrate

# Create superuser (or will be created automatically by .ebextensions)
python manage.py createsuperuser

exit
```

### 8. **Open Application**

```bash
eb open
```

## Verification Checklist

After deployment, verify:

- [ ] Application loads without errors
- [ ] Static files (CSS, JS, images) load correctly
- [ ] Admin panel accessible at `/admin/`
- [ ] User login/logout works
- [ ] Google OAuth works (update redirect URIs!)
- [ ] File uploads work (saves to S3)
- [ ] Database operations work

## Common Post-Deployment Tasks

### Update Google OAuth Redirect URIs

1. Go to [Google Cloud Console](https://console.cloud.google.com)
2. APIs & Services → Credentials
3. Edit OAuth 2.0 Client
4. Add: `https://your-app.elasticbeanstalk.com/accounts/google/login/callback/`

### View Logs

```bash
# Recent logs
eb logs

# Real-time logs
eb logs --stream
```

### Update Application

```bash
# Make code changes
git add .
git commit -m "Update description"

# Deploy
eb deploy
```

### Scale Application

```bash
# Scale to 2 instances
eb scale 2
```

## Troubleshooting

**Application won't start:**

```bash
eb logs
eb ssh
# Check logs in /var/log/
```

**Database connection errors:**

- Verify RDS security group allows EB instances
- Check environment variables: `eb printenv`

**Static files not loading:**

- Verify S3 bucket permissions
- Check AWS credentials: `eb printenv`
- SSH in and run: `python manage.py collectstatic`

**Environment variables not set:**

```bash
eb printenv  # View all variables
eb setenv KEY="value"  # Set individual variable
```

## Useful Commands Reference

| Command               | Description                    |
| --------------------- | ------------------------------ |
| `eb status`           | Show environment status        |
| `eb health`           | Show health status             |
| `eb logs`             | View application logs          |
| `eb logs --stream`    | Real-time logs                 |
| `eb printenv`         | List environment variables     |
| `eb setenv KEY=value` | Set environment variable       |
| `eb config`           | Edit environment configuration |
| `eb ssh`              | SSH into instance              |
| `eb deploy`           | Deploy application             |
| `eb open`             | Open app in browser            |
| `eb terminate`        | Terminate environment          |

## Next Steps

1. Configure custom domain (optional)
2. Set up SSL certificate via AWS Certificate Manager
3. Configure auto-scaling rules
4. Set up CloudWatch alarms
5. Configure backup policies for RDS

For detailed instructions, see [DEPLOYMENT.md](./DEPLOYMENT.md)
