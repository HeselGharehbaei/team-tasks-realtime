from django.db import models
from django.contrib.auth.models import User
from teams.models import Team


PRIORITY_CHOICES = [
    ('low', 'Low'),
    ('medium', 'Medium'),
    ('high', 'High'),
]


class Task(models.Model):
    title= models.CharField(max_length=250)
    creator=models.ForeignKey(User, related_name='created_tasks', on_delete=models.CASCADE)
    description= models.TextField(max_length=500)
    due_date= models.DateTimeField()
    priority= models.CharField(max_length=10, choices=PRIORITY_CHOICES)
    assignee=models.ForeignKey(User, null= True, blank= True, related_name='assigned_tasks', on_delete=models.SET_NULL)
    tagged_users= models.ManyToManyField(User, related_name='tagged_in_tasks')
    team= models.ForeignKey(Team, related_name='tasks', on_delete=models.CASCADE)


    def __str__(self):
        return self.title


     