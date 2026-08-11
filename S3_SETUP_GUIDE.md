# Complete Production Deployment - Step by Step

## ✅ Completed So Far

1. ✅ RDS MySQL Database Created
   - Endpoint: `bot-management-db.cy32kskg2o9a.us-east-1.rds.amazonaws.com`
   - Database: `bot_management_db`
   - Username: `admin`
   - Password: `777928412Munir28`
   - Security group: Fixed ✅

## 📋 Next Steps

### Step 1: Create S3 Bucket

1. Go to **S3 Console**: https://console.aws.amazon.com/s3

2. Click **"Create bucket"**

3. **Bucket settings**:
   - **Bucket name**: `bot-management-media-2026` (or add your initials if taken)
     - Must be globally unique
     - All lowercase, no spaces
     - ⚠️ SAVE THIS NAME!
   - **Region**: **US East (N. Virginia) us-east-1**
   - **Object Ownership**:
     - ✅ **ACLs enabled**
     - ✅ **Bucket owner preferred**
   - **Block Public Access**:
     - ❌ **Uncheck "Block all public access"**
     - ✅ Check the acknowledgment box
   - **Bucket Versioning**: Disable
   - **Encryption**: Enable (default)

4. Click **"Create bucket"**

### Step 2: Configure Bucket CORS

1. Click on your bucket name (e.g., `bot-management-media-2026`)

2. Go to **"Permissions"** tab

3. Scroll to **"Cross-origin resource sharing (CORS)"**

4. Click **"Edit"**

5. Paste this:

```json
[
  {
    "AllowedHeaders": ["*"],
    "AllowedMethods": ["GET", "HEAD", "PUT", "POST", "DELETE"],
    "AllowedOrigins": ["*"],
    "ExposeHeaders": []
  }
]
```

6. Click **"Save changes"**

### Step 3: Create IAM User for S3

1. Go to **IAM Console**: https://console.aws.amazon.com/iam

2. Click **"Users"** → **"Create user"**

3. **User name**: `bot-management-s3-user`

4. Click **"Next"**

5. **Permissions**:
   - Select **"Attach policies directly"**
   - Search: `AmazonS3FullAccess`
   - ✅ Check the box next to **AmazonS3FullAccess**

6. Click **"Next"** → **"Create user"**

### Step 4: Create Access Keys

1. Click on the user: `bot-management-s3-user`

2. Click **"Security credentials"** tab

3. Scroll to **"Access keys"**

4. Click **"Create access key"**

5. Select: **"Application running outside AWS"**

6. Click **"Next"** → **"Create access key"**

7. **⚠️ SAVE BOTH** (you won't see secret key again!):
   - **Access key ID**: `AKIA...` (starts with AKIA)
   - **Secret access key**: Long random string

8. Click **"Done"**

## After Completing S3 Setup

Once you have:

- ✅ S3 bucket name
- ✅ AWS Access Key ID
- ✅ AWS Secret Access Key

We'll set ALL environment variables and deploy your application!
