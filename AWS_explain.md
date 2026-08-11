# AWS Deployment Guide - Complete Explanation

## Table of Contents

1. [What is AWS and Why Use It?](#what-is-aws-and-why-use-it)
2. [AWS Services We Use](#aws-services-we-use)
3. [Complete Deployment Process](#complete-deployment-process)
4. [Detailed Service Explanations](#detailed-service-explanations)
5. [Cost Considerations](#cost-considerations)
6. [Troubleshooting](#troubleshooting)

---

## What is AWS and Why Use It?

**AWS (Amazon Web Services)** is a cloud computing platform that provides on-demand computing resources and services over the internet on a pay-as-you-go basis.

### Why Deploy to AWS?

1. **Scalability**: Automatically handle traffic spikes without crashing
2. **Reliability**: 99.99% uptime guarantee with automatic backups
3. **Global Reach**: Deploy your app close to users worldwide
4. **Security**: Enterprise-grade security with automatic updates
5. **Managed Services**: AWS handles server maintenance, patching, and monitoring
6. **Cost-Effective**: Pay only for what you use (Free Tier available for 12 months)

### Alternative Options

- **Heroku**: Easier but more expensive ($7-25/month for basic apps)
- **DigitalOcean**: Simpler but requires manual server management
- **Vercel/Netlify**: Great for static sites, not ideal for Django
- **AWS**: Best balance of features, cost, and scalability

---

## AWS Services We Use

Our Django application uses 5 main AWS services:

| Service               | Purpose              | Cost (Approx.)         | Alternative                    |
| --------------------- | -------------------- | ---------------------- | ------------------------------ |
| **Elastic Beanstalk** | Hosting & Deployment | Free (uses EC2)        | Heroku, DigitalOcean           |
| **RDS MySQL**         | Database             | Free Tier (t4g.micro)  | Heroku Postgres, MongoDB Atlas |
| **S3**                | Static/Media Files   | ~$0.50/month           | Cloudinary, Backblaze          |
| **Route 53**          | Domain Management    | $0.50/month + $12/year | Namecheap, GoDaddy             |
| **ACM**               | SSL Certificates     | **FREE**               | Let's Encrypt, Cloudflare      |

**Total Monthly Cost**: ~$1-5/month (with Free Tier)

---

## Complete Deployment Process

### Phase 1: Prerequisites (5 minutes)

1. **AWS Account**
   - Go to https://aws.amazon.com
   - Click "Create an AWS Account"
   - Provide credit card (required, but Free Tier won't charge you)
   - Verify email and phone

2. **Domain Name** (Optional but Recommended)
   - Purchase from Namecheap, GoDaddy, or Route 53 (~$12/year)
   - Example: `mytelebot.com`

3. **Install AWS CLI & EB CLI**

   ```bash
   # Install AWS CLI
   pip install awscli --upgrade --user

   # Install Elastic Beanstalk CLI
   pip install awsebcli --upgrade --user

   # Verify installation
   aws --version
   eb --version
   ```

---

### Phase 2: Database Setup (15 minutes)

#### Why Do We Need a Database?

Your Django app stores data (users, bots, messages) in a database. In production, we use **AWS RDS** instead of local SQLite/MySQL for:

- **Automatic Backups**: Daily snapshots
- **High Availability**: 99.9% uptime
- **Security**: Encrypted connections
- **Scalability**: Upgrade storage without downtime

#### Steps to Create RDS MySQL Database

1. **Go to AWS Console** → Search for "RDS"

2. **Create Database**:
   - Click **"Create database"**
   - **Engine**: MySQL (compatible with your local dev)
   - **Version**: MySQL 8.0 (latest stable)
   - **Templates**: **Free tier** (t4g.micro = 1GB RAM)
3. **Settings**:
   - **DB Instance Identifier**: `bot-management-db`
   - **Master Username**: `admin` (or custom)
   - **Master Password**: Create strong password (save it!)
4. **Instance Configuration**:
   - **DB Instance Class**: `db.t4g.micro` (FREE TIER)
   - **Storage**: 20GB SSD (FREE TIER)
   - **Enable Storage Autoscaling**: Yes (max 100GB)
5. **Connectivity**:
   - **VPC**: Default VPC
   - **Public Access**: **Yes** (allows Elastic Beanstalk to connect)
   - **VPC Security Group**: Create new → `bot-management-db-sg`
6. **Database Authentication**:
   - **Password authentication** (default)
7. **Additional Configuration**:
   - **Initial DB Name**: `bot_management_db`
   - **Backup Retention**: 7 days
   - **Enable Encryption**: Yes (free)
8. **Create Database** (takes 5-10 minutes)

9. **Save These Details**:

   ```
   Endpoint: bot-management-db.xxxxx.us-east-1.rds.amazonaws.com
   Port: 3306
   Database Name: bot_management_db
   Username: admin
   Password: [your password]
   ```

10. **Update Security Group** (CRITICAL):
    - Go to **EC2** → **Security Groups**
    - Find `bot-management-db-sg`
    - **Edit Inbound Rules** → **Add Rule**:
      - Type: `MySQL/Aurora (3306)`
      - Source: `Anywhere-IPv4 (0.0.0.0/0)` (for testing)
      - OR: `Your Elastic Beanstalk Security Group` (production)

---

### Phase 3: S3 Bucket for Static Files (10 minutes)

#### Why S3 Instead of Local Storage?

Django's static files (CSS, JS, images) need to be served efficiently. **S3** provides:

- **Fast CDN**: Files served from edge locations worldwide
- **Unlimited Storage**: $0.023/GB (extremely cheap)
- **Reliability**: 99.999999999% durability (won't lose files)
- **No Server Load**: Your EC2 instance doesn't serve files

#### Steps to Create S3 Bucket

1. **Go to AWS Console** → Search for "S3"

2. **Create Bucket**:
   - **Bucket Name**: `bot-management-media-2026` (globally unique)
   - **Region**: `us-east-1` (same as your EB environment)
   - **Block Public Access**: **UNCHECK** "Block all public access"
   - ⚠️ Warning: Acknowledge that files will be public
3. **Enable Static Website Hosting** (Optional):
   - Go to bucket → **Properties**
   - Scroll to **Static website hosting** → **Enable**
   - Index document: `index.html`
4. **Configure CORS** (Required for Django):
   - Go to **Permissions** tab
   - Scroll to **CORS configuration**
   - Paste:

   ```json
   [
     {
       "AllowedHeaders": ["*"],
       "AllowedMethods": ["GET", "POST", "PUT", "DELETE"],
       "AllowedOrigins": ["*"],
       "ExposeHeaders": []
     }
   ]
   ```

5. **Create IAM User for Django** (Programmatic Access):
   - Go to **IAM** → **Users** → **Create User**
   - Username: `django-deployer`
   - Access type: **Programmatic access** (no console)
   - **Attach Policies**: `AmazonS3FullAccess`
   - **Create User** → **Download CSV** (save Access Key & Secret Key!)

6. **Save These Details**:
   ```
   AWS_ACCESS_KEY_ID: AKIAxxxxxxxxxxxxx
   AWS_SECRET_ACCESS_KEY: xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   AWS_STORAGE_BUCKET_NAME: bot-management-media-2026
   AWS_S3_REGION_NAME: us-east-1
   ```

---

### Phase 4: Elastic Beanstalk Setup (20 minutes)

#### What is Elastic Beanstalk?

**Elastic Beanstalk (EB)** is AWS's Platform-as-a-Service (PaaS) that:

- **Automatically** manages EC2 instances, Load Balancers, and Auto Scaling
- **Handles** deployments, health monitoring, and logging
- **Supports** multiple platforms (Python, Node.js, Java, etc.)
- **Provides** zero-downtime deployments

Think of it as "Heroku built by AWS" - you upload your code, AWS handles the rest.

#### Steps to Deploy to Elastic Beanstalk

1. **Initialize EB Application**:

   ```bash
   cd "d:\Desktop Projects 2025\bot_management_system"
   eb init
   ```

   **Answer Prompts**:
   - Region: `us-east-1` (N. Virginia - cheapest, closest to RDS/S3)
   - Application Name: `bot-management-system`
   - Platform: `Python 3.11`
   - SSH: `No` (unless you need remote access)

2. **Create Environment**:

   ```bash
   eb create bot-management-prod
   ```

   **What This Creates**:
   - EC2 Instance (t2.micro = Free Tier)
   - Load Balancer (distributes traffic)
   - Auto Scaling Group (handles traffic spikes)
   - Security Groups (firewall rules)
   - CloudWatch Logs (monitoring)

3. **Set Environment Variables** (CRITICAL):

   ```bash
   eb setenv \
     SECRET_KEY="your-django-secret-key" \
     DEBUG=False \
     ALLOWED_HOSTS="bot-management-prod.us-east-1.elasticbeanstalk.com,mytelebot.com" \
     DB_ENGINE="django.db.backends.mysql" \
     DB_NAME="bot_management_db" \
     DB_USER="admin" \
     DB_PASSWORD="your-rds-password" \
     DB_HOST="bot-management-db.xxxxx.us-east-1.rds.amazonaws.com" \
     DB_PORT="3306" \
     USE_S3=True \
     AWS_ACCESS_KEY_ID="AKIAxxxxx" \
     AWS_SECRET_ACCESS_KEY="xxxxxxxx" \
     AWS_STORAGE_BUCKET_NAME="bot-management-media-2026" \
     AWS_S3_REGION_NAME="us-east-1"
   ```

4. **Deploy Application**:

   ```bash
   python create_deploy_zip.py  # Create deployment package
   eb deploy  # Upload and deploy
   ```

5. **Check Health**:

   ```bash
   eb health --refresh
   ```

   - **Green** = Healthy ✅
   - **Yellow** = Degraded (warnings)
   - **Red** = Severe (check logs: `eb logs`)

6. **Open Application**:
   ```bash
   eb open
   ```

---

### Phase 5: Domain & SSL Setup (30 minutes)

#### Why Use a Custom Domain?

Instead of `bot-management-prod.us-east-1.elasticbeanstalk.com`, use `mytelebot.com`:

- **Professional**: Easier to remember, share, and market
- **SEO**: Better search engine rankings
- **Branding**: Builds trust with users
- **Portability**: If you switch hosts, domain stays the same

#### Step 1: Register Domain

**Option A: Route 53** (AWS)

- Go to **Route 53** → **Register Domain**
- Search for `mytelebot.com` (~$12-15/year)
- Auto-creates Hosted Zone ($0.50/month)

**Option B: Namecheap/GoDaddy** (Cheaper)

- Register domain (~$8-12/year)
- Manually transfer nameservers to Route 53

#### Step 2: Create Hosted Zone (If Using External Registrar)

1. **Go to Route 53** → **Hosted Zones** → **Create Hosted Zone**
   - Domain Name: `mytelebot.com`
   - Type: Public Hosted Zone
   - **Create**

2. **Copy Nameservers** (shown in NS record):

   ```
   ns-123.awsdns-12.com
   ns-456.awsdns-34.net
   ns-789.awsdns-56.org
   ns-012.awsdns-78.co.uk
   ```

3. **Update Your Domain Registrar**:
   - Go to Namecheap/GoDaddy domain settings
   - Change nameservers to AWS nameservers above
   - **Wait 24-48 hours** for DNS propagation

#### Step 3: Point Domain to Elastic Beanstalk

1. **Go to Route 53** → **Hosted Zones** → `mytelebot.com`

2. **Create Record**:
   - Record Name: _(leave blank for root domain)_
   - Record Type: **A - IPv4 address**
   - Value: **Alias**
     - Alias Target: **Elastic Beanstalk environment**
     - Region: `us-east-1`
     - Environment: `bot-management-prod.us-east-1.elasticbeanstalk.com`
   - Routing Policy: **Simple**
   - **Create Record**

3. **Test** (after 5-10 minutes):
   ```bash
   ping mytelebot.com
   # Should resolve to AWS IP
   ```

#### Step 4: Request SSL Certificate (HTTPS)

**Why SSL?**

- **Security**: Encrypts data between user and server
- **Trust**: Browsers show "Secure" lock icon
- **SEO**: Google ranks HTTPS sites higher
- **Required**: For Google OAuth, payment processing, etc.

**Steps**:

1. **Go to ACM (AWS Certificate Manager)** → `us-east-1` region
   - **IMPORTANT**: Must be `us-east-1` for Load Balancer!

2. **Request Certificate**:
   - Certificate Type: **Public Certificate**
   - Domain Name: `mytelebot.com`
   - Add Another: `www.mytelebot.com` (wildcard: `*.mytelebot.com`)
   - Validation: **DNS Validation** (automatic)
   - **Request**

3. **Validate Certificate**:
   - Click certificate ID → **Domains** section
   - Click **"Create records in Route 53"**
   - **Create records** (adds CNAME automatically)
   - Status changes to **"Issued"** in 2-5 minutes

4. **Add HTTPS Listener to Load Balancer**:
   - Go to **EC2** → **Load Balancers**
   - Select your EB Load Balancer (`awseb-...`)
   - **Listeners** tab → **Add listener**:
     - Protocol: **HTTPS**
     - Port: **443**
     - Default Action: **Forward to** your Target Group
     - Security Policy: Default (TLS 1.2+)
     - **Default SSL Certificate**: Select `mytelebot.com`
   - **Add**

5. **Update Security Group**:
   - **Security Groups** → Load Balancer SG
   - **Edit Inbound Rules** → **Add Rule**:
     - Type: **HTTPS**
     - Port: **443**
     - Source: **Anywhere-IPv4 (0.0.0.0/0)**
   - **Save**

6. **Test HTTPS**:
   ```
   https://mytelebot.com
   ```

   - Should show 🔒 lock icon in browser

---

## Detailed Service Explanations

### 1. Elastic Beanstalk Architecture

```
Internet → Route 53 (DNS) → Application Load Balancer → EC2 Instance(s) → RDS Database
                                         ↓
                                    S3 (Static Files)
```

**Components**:

- **Load Balancer**: Distributes traffic, handles HTTPS, health checks
- **EC2 Instance**: Runs your Django app (managed by EB)
- **Auto Scaling**: Adds/removes instances based on traffic
- **CloudWatch**: Logs and monitors application health

**How It Works**:

1. User visits `mytelebot.com`
2. Route 53 resolves to Load Balancer IP
3. Load Balancer forwards request to healthy EC2 instance
4. Django app processes request, queries RDS database
5. Static files (CSS/JS) served directly from S3
6. Response returned to user

### 2. Environment Variables (Why?)

**Problem**: Hardcoding secrets in code is:

- ❌ Insecure (anyone with code can access DB)
- ❌ Inflexible (different settings for dev/prod)
- ❌ Version control risk (exposed in Git history)

**Solution**: Environment Variables

- ✅ Secure (stored in AWS, not in code)
- ✅ Easy to update (no redeployment needed)
- ✅ Environment-specific (different DB for dev/prod)

**How to Set**:

```bash
eb setenv KEY=value
```

**How Django Reads**:

```python
import os
SECRET_KEY = os.environ.get('SECRET_KEY', 'fallback-value')
```

### 3. Static Files Strategy

**Local Development**:

- Static files in `static/` folder
- Django serves them automatically (`DEBUG=True`)

**Production (Django + S3)**:

1. Run `python manage.py collectstatic`
2. Uploads all static files to S3
3. Django settings:
   ```python
   STATICFILES_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
   STATIC_URL = 'https://bot-management-media-2026.s3.amazonaws.com/'
   ```
4. Templates use `{% static %}` tag → auto-generates S3 URL

**Benefits**:

- **100x Faster**: S3 CDN vs Django server
- **Scalable**: No load on EC2 instance
- **Cached**: Browser caches CSS/JS efficiently

### 4. Health Checks (Why App Was "Severe")

**What's a Health Check?**

- Load Balancer pings your app every 30 seconds at `/`
- Expects HTTP 200 response
- If 5 consecutive failures → removes instance from rotation

**Why We Had "Severe" Health**:

1. **400 Bad Request**: `ALLOWED_HOSTS` blocked health check IP
2. **500 Server Error**: Database connection failed
3. **Timeout**: Database migrations taking too long

**Solutions We Applied**:

1. Set `ALLOWED_HOSTS = ['*']` (allows all IPs)
2. Fixed database connection (correct port, credentials)
3. Added `migrate` command to `.ebextensions` (runs before health checks)

---

## Cost Considerations

### Free Tier Limits (First 12 Months)

| Service           | Free Tier                      | Overage Cost                    |
| ----------------- | ------------------------------ | ------------------------------- |
| **EC2**           | 750 hours/month (t2.micro)     | $0.012/hour (~$8/month)         |
| **RDS**           | 750 hours/month (db.t4g.micro) | $0.017/hour (~$12/month)        |
| **S3**            | 5GB storage, 20K GET requests  | $0.023/GB + $0.0004/1K requests |
| **Load Balancer** | Not Free                       | ~$16/month                      |
| **Route 53**      | Not Free                       | $0.50/month + $12/year (domain) |
| **ACM**           | **FREE**                       | Always free!                    |

**Total Monthly Cost**:

- **Year 1 (Free Tier)**: ~$17/month (Load Balancer + Route 53)
- **Year 2+**: ~$45-60/month (EC2 + RDS + LB + Route 53)

### Cost Optimization Tips

1. **Use Reserved Instances** (Year 2+):
   - Save 40-60% vs on-demand pricing
   - Commit to 1-3 years

2. **Downgrade After Testing**:
   - RDS: `db.t4g.micro` → `db.t3.micro` (50% cheaper)
   - EC2: Consider Lightsail ($10/month flat rate)

3. **Delete Unused Resources**:
   - Old Elastic Beanstalk environments
   - Unattached Load Balancers
   - Old S3 files (set lifecycle rules)

4. **Use CloudWatch Alarms**:
   - Alert when costs exceed $20/month
   - Prevent surprise bills

---

## Troubleshooting

### Issue: "Environment Health is Degraded/Severe"

**Check Logs**:

```bash
eb logs
```

**Common Causes**:

1. **Database Connection Failed**
   - Verify `DB_HOST`, `DB_PASSWORD` in environment variables
   - Check RDS Security Group allows EC2 instance

2. **Missing Dependencies**
   - Check `requirements.txt` includes all packages
   - Redeploy: `eb deploy`

3. **Migrations Failed**
   - SSH into instance: `eb ssh`
   - Manually run: `python manage.py migrate`

### Issue: "502 Bad Gateway"

**Cause**: App crashed or timed out

**Solutions**:

1. Check logs: `eb logs --all`
2. Verify `Procfile` exists:
   ```
   web: gunicorn bot_management_system.wsgi --log-file -
   ```
3. Test locally:
   ```bash
   gunicorn bot_management_system.wsgi
   ```

### Issue: "Static Files Not Loading (404)"

**Causes**:

1. `collectstatic` not run during deployment
2. S3 bucket permissions wrong
3. `STATIC_URL` incorrect

**Solutions**:

1. Check `.ebextensions/01_django.config`:
   ```yaml
   container_commands:
     02_collectstatic:
       command: "source /var/app/venv/*/bin/activate && python manage.py collectstatic --noinput"
   ```
2. Verify S3 bucket is public
3. Test S3 URL directly: `https://bot-management-media-2026.s3.amazonaws.com/css/style.css`

### Issue: "Google OAuth Not Working"

**Causes**:

1. Redirect URIs not updated in Google Console
2. HTTPS not configured
3. `django-allauth` not installed

**Solutions**:

1. Go to Google Cloud Console → Credentials → OAuth 2.0 Client
2. Add Authorized Redirect URIs:
   ```
   https://mytelebot.com/accounts/google/login/callback/
   ```
3. Ensure HTTPS listener is active (port 443)

### Issue: "Cannot Connect to RDS from MySQL Workbench"

**Causes**:

1. Security Group blocking your IP
2. Public Access disabled
3. Wrong credentials

**Solutions**:

1. RDS → Security Groups → Add your IP (Use "My IP" option)
2. RDS → Modify → Public Access = Yes
3. Verify username/password from EB environment variables

---

## Final Checklist

Before going live:

- [ ] RDS database created and accessible
- [ ] S3 bucket created with CORS configured
- [ ] Elastic Beanstalk environment deployed
- [ ] Environment variables set (check `eb printenv`)
- [ ] Migrations run successfully (`eb logs` confirms)
- [ ] Static files uploaded to S3 (`collectstatic` in logs)
- [ ] Domain pointed to Load Balancer (A record)
- [ ] SSL certificate issued and attached to Load Balancer
- [ ] HTTPS working (`https://yourdomain.com` shows lock icon)
- [ ] Google OAuth redirect URIs updated
- [ ] Health status is "Green" (`eb health`)
- [ ] All features tested on production domain

---

## Additional Resources

- **AWS Free Tier**: https://aws.amazon.com/free
- **Elastic Beanstalk Docs**: https://docs.aws.amazon.com/elasticbeanstalk
- **Django on EB Tutorial**: https://docs.aws.amazon.com/elasticbeanstalk/latest/dg/create-deploy-python-django.html
- **AWS Architecture Best Practices**: https://aws.amazon.com/architecture/well-architected/
- **Cost Calculator**: https://calculator.aws

---

**Need Help?** Check `problem_solve.md` for issues we already fixed!
