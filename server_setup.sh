#!/bin/bash
# ==============================================================================
# AWS LIGHTSAIL / EC2 (UBUNTU) ONE-TIME SETUP SCRIPT
# Run this ONCE on your new server to install all required software.
# Do not run this on your local Windows PC.
#
# RUN COMMAND: sudo bash server_setup.sh
# ==============================================================================

PROJECT_NAME="bot_management_system"
DB_NAME="bot_management_db"
DB_USER="admin"

# Change this to a secure database password!
DB_PASSWORD="secure_password_123!"

echo ">>> Updating Server..."
apt-get update -y
apt-get upgrade -y

echo ">>> Installing Requirements (Python, Nginx, MySQL)..."
apt-get install -y python3-pip python3-venv nginx mysql-server libmysqlclient-dev pkg-config python3-dev jq curl

echo ">>> Configuring MySQL Database..."
# Secure MySQL installation & configure databases
mysql -e "CREATE DATABASE IF NOT EXISTS ${DB_NAME} CHARACTER SET UTF8;"
mysql -e "CREATE USER IF NOT EXISTS '${DB_USER}'@'localhost' IDENTIFIED BY '${DB_PASSWORD}';"
mysql -e "GRANT ALL PRIVILEGES ON ${DB_NAME}.* TO '${DB_USER}'@'localhost';"
mysql -e "FLUSH PRIVILEGES;"

echo ">>> Setting up Project Directories..."
mkdir -p /var/www/${PROJECT_NAME}
mkdir -p /var/www/${PROJECT_NAME}/media
mkdir -p /var/www/${PROJECT_NAME}/staticfiles
mkdir -p /var/log/gunicorn

# Give ubuntu user permissions
chown -R ubuntu:www-data /var/www/${PROJECT_NAME}
chmod -R 775 /var/www/${PROJECT_NAME}

echo ">>> Creating Systemd service for Gunicorn..."
cat > /etc/systemd/system/gunicorn.service << EOF
[Unit]
Description=gunicorn daemon for ${PROJECT_NAME}
After=network.target

[Service]
User=ubuntu
Group=www-data
WorkingDirectory=/var/www/${PROJECT_NAME}
ExecStart=/var/www/${PROJECT_NAME}/venv/bin/gunicorn --access-logfile - --workers 3 --bind unix:/var/www/${PROJECT_NAME}/${PROJECT_NAME}.sock ${PROJECT_NAME}.wsgi:application

[Install]
WantedBy=multi-user.target
EOF

echo ">>> Creating Nginx Configuration..."
cat > /etc/nginx/sites-available/${PROJECT_NAME} << EOF
server {
    listen 80;
    server_name _;

    client_max_body_size 50M;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        alias /var/www/${PROJECT_NAME}/staticfiles/;
    }

    location /media/ {
        alias /var/www/${PROJECT_NAME}/media/;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/var/www/${PROJECT_NAME}/${PROJECT_NAME}.sock;
    }
}
EOF

# Enable Nginx site
ln -s /etc/nginx/sites-available/${PROJECT_NAME} /etc/nginx/sites-enabled/ 2>/dev/null
rm /etc/nginx/sites-enabled/default 2>/dev/null

echo ">>> Restarting Services..."
systemctl daemon-reload
systemctl enable gunicorn
systemctl restart nginx

echo "====================================================================="
echo "✅ Server Setup Complete!"
echo "Your Database Password is: ${DB_PASSWORD}"
echo "Keep this safe. We will use it in your local deployment script."
echo "====================================================================="
