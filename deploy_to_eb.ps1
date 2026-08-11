# AWS Elastic Beanstalk Deployment Script
# This script helps you deploy the bot_management_system to AWS EB

Write-Host "=== AWS Elastic Beanstalk Deployment Helper ===" -ForegroundColor Cyan
Write-Host ""

# Check if in virtual environment
if (-not $env:VIRTUAL_ENV) {
    Write-Host "⚠️  Virtual environment not activated!" -ForegroundColor Yellow
    Write-Host "Activating django_env..." -ForegroundColor Yellow
    .\django_env\Scripts\Activate.ps1
}

Write-Host "Step 1: Initialize Elastic Beanstalk Application" -ForegroundColor Green
Write-Host "---------------------------------------------------"
Write-Host ""
Write-Host "Run the following command to initialize EB:" -ForegroundColor White
Write-Host ""
Write-Host "  eb init -p python-3.11 bot-management-system --region us-east-1" -ForegroundColor Cyan
Write-Host ""
Write-Host "You'll be prompted for:" -ForegroundColor Yellow
Write-Host "  - AWS credentials (if not configured)" -ForegroundColor Yellow
Write-Host "  - Application name (suggested: bot-management-system)" -ForegroundColor Yellow
Write-Host "  - SSH key setup (recommended: yes)" -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter when ready to continue"

Write-Host ""
Write-Host "Step 2: Create Load-Balanced Environment" -ForegroundColor Green
Write-Host "---------------------------------------------------"
Write-Host ""
Write-Host "Run the following command to create the environment:" -ForegroundColor White
Write-Host ""
Write-Host "  eb create bot-management-prod --elb-type application --scale 1 --instance_type t3.micro" -ForegroundColor Cyan
Write-Host ""
Write-Host "This will:" -ForegroundColor Yellow
Write-Host "  - Create an Application Load Balancer" -ForegroundColor Yellow
Write-Host "  - Start with 1 t3.micro instance" -ForegroundColor Yellow
Write-Host "  - Deploy your application" -ForegroundColor Yellow
Write-Host "  - Wait 5-10 minutes for setup" -ForegroundColor Yellow
Write-Host ""
Read-Host "Press Enter when ready to continue"

Write-Host ""
Write-Host "Step 3: Set Environment Variables" -ForegroundColor Green
Write-Host "---------------------------------------------------"
Write-Host ""
Write-Host "Before you start, you'll need:" -ForegroundColor Yellow
Write-Host "  1. A new SECRET_KEY (generate with Django)" -ForegroundColor Yellow
Write-Host "  2. Your RDS database credentials" -ForegroundColor Yellow  
Write-Host "  3. Your S3 bucket name and AWS credentials" -ForegroundColor Yellow
Write-Host "  4. Your EB application URL (after creation)" -ForegroundColor Yellow
Write-Host ""
Write-Host "See 'eb_setenv_commands.txt' for the complete command template" -ForegroundColor White
Write-Host ""

Write-Host "✅ Deployment helper complete!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Run: eb init -p python-3.11 bot-management-system --region us-east-1" -ForegroundColor White
Write-Host "  2. Run: eb create bot-management-prod --elb-type application --scale 1 --instance_type t3.micro" -ForegroundColor White
Write-Host "  3. Review and run commands from 'eb_setenv_commands.txt'" -ForegroundColor White
Write-Host "  4. Run: eb open" -ForegroundColor White
Write-Host ""
