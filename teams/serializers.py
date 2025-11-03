from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Team

class UserSimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']

class TeamSerializer(serializers.ModelSerializer):
    members = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        many=True,
        write_only=True
    )
    members_info = UserSimpleSerializer(
        source='members',
        many=True,
        read_only=True
    )

    class Meta:
        model = Team
        fields = ['id', 'name', 'members', 'members_info']
