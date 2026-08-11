# Create New S3 Bucket - Quick Steps

## You're on the S3 Console - Perfect!

The `elasticbeanstalk-us-east-1-671484840498` bucket is Elastic Beanstalk's own bucket. You need a **separate bucket** for your Django files.

## Click "Create bucket" Button

Fill in these settings:

### General Configuration

1. **Bucket name**: `bot-management-media-2026`
   - If taken, try: `bot-media-2026` or `bot-media-ms-2026`
   - Must be globally unique, all lowercase, no spaces

2. **AWS Region**: **US East (N. Virginia) us-east-1**

### Object Ownership

3. **ACLs**: ✅ **ACLs enabled**
4. Select: ✅ **Bucket owner preferred**

### Block Public Access

5. ❌ **UNCHECK** "Block all public access"
6. ✅ **CHECK** the acknowledgment box that appears

### Bucket Versioning

7. **Disable** (leave unchecked)

### Default Encryption

8. **Enable** - Server-side encryption with Amazon S3 managed keys (SSE-S3) - keep default

### Click "Create bucket"

## After Bucket is Created

1. Click on your new bucket name
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

## Then Tell Me the Bucket Name

Once created, tell me the exact bucket name and we'll deploy immediately!
