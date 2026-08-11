# SSH Setup Confirmation Required

## What's Happening

The command `eb ssh --setup` is asking you to confirm because it needs to:

1. **Terminate** the current instance
2. **Create** a new instance with SSH enabled
3. This causes **temporary downtime** (~2-3 minutes)

## What You Need to Do

**Type this exactly in your terminal:**

```
bot-management-prod
```

Then press Enter.

## After Confirmation

The setup will:

1. Terminate current instance
2. Create new instance with SSH key
3. Wait for the environment to become ready (~2-3 minutes)
4. Prompt you to select/create an SSH keypair

## Next Commands (After SSH Setup Completes)

```bash
# 1. Deploy to apply SSH configuration
eb deploy

# 2. SSH into the instance
eb ssh

# 3. Inside the instance, run these commands:
source /var/app/venv/*/bin/activate
cd /var/app/current
python manage.py migrate --noinput
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.create_superuser('admin', 'admin@example.com', 'admin123') if not User.objects.filter(username='admin').exists() else None" | python manage.py shell
sudo systemctl restart web
exit

# 4. Check health
eb health

# 5. Open application
eb open
```

## Current Wait

⏳ Waiting for you to type: **bot-management-prod** in the terminal
