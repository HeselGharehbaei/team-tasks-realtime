from django.db import models
from django.contrib.auth.models import User


NOTIFICATION_TYPES = [
        ('assignment', 'Assignment'),
        ('mention', 'Mention'),
        ('overdue', 'Overdue'),
]


class Notification(models.Model):
    user = models.ForeignKey(
        User,
        related_name='notifications',
        on_delete=models.CASCADE
    )    
    type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    title = models.CharField(max_length=200)
    message = models.TextField()
    task = models.ForeignKey(
        'tasks.Task',
        related_name='notifications',
        null=True,
        blank=True,
        on_delete=models.SET_NULL
    )


    class Meta:
        indexes = [
            models.Index(fields=['user']),
        ]

    def __str__(self):
        return f"{self.user.username} - {self.type} - {self.title}"
