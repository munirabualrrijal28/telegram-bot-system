# Next Steps After SSH Setup

## You're using MySQL locally, but on AWS you have SQLite configured

**Current AWS Setup:**

- Database: SQLite (temporary, not ideal for production)
- Environment variables: DB_ENGINE="django.db.backends.sqlite3"

**Your Local Setup:**

- Database: MySQL

## After SSH is Enabled

### 1. Deploy with SSH Enabled

```bash
eb deploy
```

### 2. SSH into Instance and Run Migrations

```bash
eb ssh

# Inside the instance:
source /var/app/venv/*/bin/activate
cd /var/app/current

# Run migrations with SQLite
python manage.py migrate --noinput

# Create superuser automatically
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else None" | python manage.py shell

# Restart web server
sudo systemctl restart web

exit
```

### 3. Check Health

```bash
eb health
eb open
```

## Recommended: Switch to RDS PostgreSQL (Production)

Since you're deploying to production, SQLite is NOT recommended because:

- ❌ Data is lost on every deployment
- ❌ Doesn't work with multiple instances (scaling)
- ❌ File-based, not suitable for cloud

**Better option: RDS PostgreSQL**

1. Create RDS instance in AWS Console
2. Set environment variables:

```bash
eb setenv \
  RDS_DB_NAME="bot_management_db" \
  RDS_USERNAME="dbadmin" \
  RDS_PASSWORD="YourSecurePassword123" \
  RDS_HOSTNAME="your-rds-endpoint.rds.amazonaws.com" \
  RDS_PORT="5432"
```

This will automatically switch from SQLite to PostgreSQL (your settings.py already handles this).

## MySQL on AWS (Alternative)

If you prefer MySQL (like your local setup):

1. Create RDS MySQL instance
2. Set:

```bash
eb setenv \
  DB_ENGINE="django.db.backends.mysql" \
  DB_NAME="bot_management_db" \
  DB_USER="admin" \
  DB_PASSWORD="password" \
  DB_HOST="your-mysql-endpoint.rds.amazonaws.com" \
  DB_PORT="3306"
```

Note: Your settings.py checks for `RDS_DB_NAME` first (PostgreSQL), then falls back to `DB_ENGINE` (MySQL/SQLite).
