# ==================================================================
# SINGLE VPS DEPLOYMENT SCRIPT
# Run this script whenever you make changes to your code.
# ==================================================================

$SERVER_IP = "51.44.10.159"
$SSH_KEY = "bot-key.pem"
$SERVER_USER = "ubuntu"

Write-Host "🚀 Starting Deployment Process..." -ForegroundColor Cyan



# Ensure SSH key permissions are strict (Windows OpenSSH requirement)
if (Test-Path $SSH_KEY) {
    # Skip if running inside IDE where ACL changes might block Git, but try anyway
    $acl = Get-Acl $SSH_KEY
    $acl.SetAccessRuleProtection($true, $false)
    $acl.Access | ForEach-Object { $acl.RemoveAccessRule($_) } | Out-Null
    $rule = New-Object System.Security.AccessControl.FileSystemAccessRule($env:USERNAME, "Read", "Allow")
    $acl.AddAccessRule($rule)
    Set-Acl -Path $SSH_KEY -AclObject $acl
}
else {
    Write-Host "❌ ERROR: Cannot find bot-key.pem in the current folder!" -ForegroundColor Red
    exit 1
}

$TAR_PATH = "$PSScriptRoot\deploy.tar.gz"

Write-Host "📦 Creating deployment package..." -ForegroundColor Yellow
tar.exe -czf $TAR_PATH --exclude=venv --exclude=django_env --exclude=env --exclude=media --exclude=staticfiles --exclude=.git --exclude=__pycache__ --exclude=db.sqlite3 --exclude=.ebextensions --exclude=deploy.tar.gz --exclude=bot-key.pem .

Write-Host "📤 Uploading package & setup scripts to server ($SERVER_IP)..." -ForegroundColor Yellow
scp -o ServerAliveInterval=60 -o StrictHostKeyChecking=no -i $SSH_KEY server_setup.sh ${SERVER_USER}@${SERVER_IP}:/home/${SERVER_USER}/server_setup.sh
scp -o ServerAliveInterval=60 -o StrictHostKeyChecking=no -i $SSH_KEY remote_deploy.sh ${SERVER_USER}@${SERVER_IP}:/home/${SERVER_USER}/remote_deploy.sh
scp -o ServerAliveInterval=60 -o StrictHostKeyChecking=no -i $SSH_KEY $TAR_PATH ${SERVER_USER}@${SERVER_IP}:/home/${SERVER_USER}/deploy.tar.gz

Write-Host "⚙️  Installing updates and restarting server..." -ForegroundColor Yellow
# Using an intermediate cleanup to avoid pipe character corruption on ssh stdin
ssh -t -o ServerAliveInterval=60 -o StrictHostKeyChecking=no -i $SSH_KEY ${SERVER_USER}@${SERVER_IP} "tr -d '\r' < /home/${SERVER_USER}/remote_deploy.sh > /home/${SERVER_USER}/clean_deploy.sh && bash /home/${SERVER_USER}/clean_deploy.sh"

Remove-Item $TAR_PATH -ErrorAction SilentlyContinue

Write-Host "✅ DEPLOYMENT COMPLETE! Your site is live!" -ForegroundColor Green
