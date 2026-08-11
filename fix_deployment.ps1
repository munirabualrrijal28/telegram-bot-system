# Quick Fix Deployment Script
# Run this to fix the Red health status

Write-Host "=== EB Deployment Fix ===" -ForegroundColor Cyan
Write-Host ""

Write-Host "Generated SECRET_KEY (save this!):" -ForegroundColor Yellow
Write-Host "+f#2_n_9b0-9-5*fqqb+3g9!)xg(fbi@043hpgmutek1kmhy" -ForegroundColor Green
Write-Host ""

Write-Host "Step 1: Set Environment Variables" -ForegroundColor Cyan
Write-Host "Run this command:" -ForegroundColor White
Write-Host ""
Write-Host 'eb setenv SECRET_KEY="+f#2_n_9b0-9-5*fqqb+3g9!)xg(fbi@043hpgmutek1kmhy" DEBUG="False" ALLOWED_HOSTS=".elasticbeanstalk.com" USE_S3="False"' -ForegroundColor Green
Write-Host ""

Write-Host "Step 2: Deploy with simplified config" -ForegroundColor Cyan
Write-Host "Run: eb deploy" -ForegroundColor Green
Write-Host ""

Write-Host "Step 3: SSH and run migrations" -ForegroundColor Cyan
Write-Host "Run: eb ssh" -ForegroundColor Green
Write-Host ""
Write-Host "Then inside the instance:" -ForegroundColor Yellow
Write-Host "  source /var/app/venv/*/bin/activate" -ForegroundColor White
Write-Host "  cd /var/app/current" -ForegroundColor White
Write-Host "  python manage.py migrate" -ForegroundColor White
Write-Host "  python manage.py collectstatic --noinput" -ForegroundColor White
Write-Host "  python manage.py createsuperuser" -ForegroundColor White
Write-Host "  sudo systemctl restart web" -ForegroundColor White
Write-Host "  exit" -ForegroundColor White
Write-Host ""

Write-Host "Step 4: Check health" -ForegroundColor Cyan
Write-Host "Run: eb health" -ForegroundColor Green
Write-Host ""

Write-Host "Step 5: Open application" -ForegroundColor Cyan
Write-Host "Run: eb open" -ForegroundColor Green
Write-Host ""
