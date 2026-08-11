#!/bin/bash
set -e

PROJECT_NAME="bot_management_system"
SERVER_USER="ubuntu"
DB_PASSWORD="secure_password_123!"

# Fix Windows line endings safely
tr -d '\r' < /home/${SERVER_USER}/server_setup.sh > /home/${SERVER_USER}/server_setup_clean.sh
mv /home/${SERVER_USER}/server_setup_clean.sh /home/${SERVER_USER}/server_setup.sh
chmod +x /home/${SERVER_USER}/server_setup.sh

# Run Initial Setup if missing
if [ ! -d "/var/www/$PROJECT_NAME" ]; then
    echo "Running Initial Server Setup (Installing Nginx, Python, MySQL)..."
    sudo bash /home/${SERVER_USER}/server_setup.sh
    
    # Enable a small swap space for 512MB RAM instances
    if [ ! -f "/swapfile" ]; then
        sudo fallocate -l 1G /swapfile
        sudo chmod 600 /swapfile
        sudo mkswap /swapfile
        sudo swapon /swapfile
    fi
fi

echo "Extracting code..."
cd /var/www/$PROJECT_NAME
sudo tar -xzf /home/${SERVER_USER}/deploy.tar.gz -C /var/www/$PROJECT_NAME
sudo chown -R ubuntu:www-data /var/www/$PROJECT_NAME

# Remove conflicting PyMySQL patches from the user's code dynamically
echo "Securing compatibilities..."
sudo sed -i 's/import pymysql/# import pymysql/g' bot_management_system/settings.py
sudo sed -i 's/pymysql.install_as_MySQLdb()/# pymysql.install_as_MySQLdb()/g' bot_management_system/settings.py

echo "Configuring Environment..."
cat > .env << 'EOF'
DEBUG="True"
SECRET_KEY="+f#2_n_9b0-9-5*fqqb+3g9!)xg(fbi@043hpgmutek1kmhy"
ALLOWED_HOSTS="*"
DB_ENGINE="django.db.backends.mysql"
DB_NAME="bot_management_db"
DB_USER="admin"
DB_PASSWORD="secure_password_123!"
DB_HOST="localhost"
DB_PORT=""
EOF

echo "Fixing Gunicorn Service..."
cat > gunicorn.service << 'EOF'
[Unit]
Description=gunicorn daemon for bot_management_system
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/var/www/bot_management_system
EnvironmentFile=/var/www/bot_management_system/.env
ExecStart=/var/www/bot_management_system/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/var/www/bot_management_system/bot_management_system.sock bot_management_system.wsgi:application

[Install]
WantedBy=multi-user.target
EOF
sudo mv gunicorn.service /etc/systemd/system/gunicorn.service

if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn mysqlclient

echo "Running Django Migrations..."
set -a
source .env
set +a
python manage.py makemigrations
python manage.py migrate
python manage.py collectstatic --noinput

echo "Restarting Services..."
sudo systemctl daemon-reload
sudo systemctl restart gunicorn
sudo systemctl restart nginx
