from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Task

class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class TaskSerializer(serializers.ModelSerializer):
    tagged_users = serializers.PrimaryKeyRelatedField(queryset=User.objects.all(), many=True, write_only=True)
    tagged_users_info = UserSimpleSerializer(source='tagged_users', many=True, read_only=True)
    creator_info = UserSimpleSerializer(source='creator', read_only=True)
    assignee_info = UserSimpleSerializer(source='assignee', read_only=True)

    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'due_date', 'priority',
            'creator', 'creator_info',
            'assignee', 'assignee_info',
            'tagged_users', 'tagged_users_info',
            'team'
        ]


class TaskAssignResponseSerializer(serializers.Serializer):
    message = serializers.CharField()
    assigned_to = serializers.DictField()
    task = serializers.CharField()
