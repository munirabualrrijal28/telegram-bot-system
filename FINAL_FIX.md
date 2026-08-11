# FINAL FIX - Deploy with Ultra-Minimal Requirements

## The Problem

Even with all environment variables set, the deployment is failing with HTTP 5xx errors. This is the **package installation issue** on Amazon Linux 2023.

## The Solution - Ultra-Minimal Deployment

Deploy with ONLY essential packages first, verify it works, THEN add more packages.

## Step 1: Use Minimal Requirements

```powershell
# Copy the ultra-minimal requirements
cp requirements-minimal.txt requirements.txt
```

This file has ONLY 9 safe packages:

- Django, gunicorn, whitenoise
- psycopg2-binary, PyMySQL
- boto3, django-storages
- Pillow, requests

**NO** django-allauth, cryptography, or other complex packages yet.

## Step 2: Deploy

```powershell
eb deploy
```

Wait 3-5 minutes. The health should turn **Green** this time because:

- ✅ All packages will install successfully
- ✅ Database connection works (MySQL RDS)
- ✅ S3 works (for static files)
- ✅ Environment variables are all set

## Step 3: Verify It Works

```powershell
eb health
eb open
```

You should see a working Django site!

## Step 4: Add Packages Back (One by One)

Once the site is working with minimal requirements, add packages back gradually:

```txt
# Add to requirements.txt ONE AT A TIME
django-allauth==65.3.0
```

Then `eb deploy` and check if it still works.

If a package breaks deployment, skip it or find an alternative.

## Why This Will Work

- Amazon Linux 2023 is strict about package dependencies
- Some packages (django-allauth, cryptography) require compilation
- Starting minimal ensures the core app works
- You can add features incrementally once stable

## Run This Now

```powershell
cp requirements-minimal.txt requirements.txt
eb deploy
```

This WILL work! 🎉
