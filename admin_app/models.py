from django.db import models



class SystemNotification(models.Model):
    TYPE_CHOICES = [
        ('in_app', 'In-App Notification'),
        ('email', 'Email'),
        ('both', 'Both'),
    ]
    
    title = models.CharField(max_length=255)
    message = models.TextField()
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='in_app')
    created_at = models.DateTimeField(auto_now_add=True)
    sent_by = models.ForeignKey('core.SystemAdmin', on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        
    def __str__(self):
        return self.title



