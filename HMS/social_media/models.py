from django.db import models
from accountss.models import Custom_user # Import the custom User model

class SocialMediaPost(models.Model):
    PLATFORM_CHOICES = (
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter'),
        ('instagram', 'Instagram'),
        ('linkedin', 'LinkedIn'),
    )

    user = models.ForeignKey(Custom_user, on_delete=models.CASCADE)  # Use the custom User model
    platform = models.CharField(max_length=20, choices=PLATFORM_CHOICES)
    message = models.TextField()
    post_date = models.DateTimeField(auto_now_add=True)
    posted = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.platform} post by {self.user.username} on {self.post_date}'


class ChatMessage(models.Model):
    user = models.ForeignKey(Custom_user, on_delete=models.CASCADE)
    message = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Message by {self.user.username} on {self.timestamp}'
    

class ChatBot(models.Model):
    user = models.ForeignKey(Custom_user, on_delete=models.CASCADE)
    message = models.TextField()
    response = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Chat with {self.user.username} on {self.timestamp}'