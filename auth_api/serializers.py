from rest_framework import serializers

class LoginSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()
    
    class Meta:
        examples = {
            "login_example": {
                "username": "ali",
                "password": "123456"
            }
        }

class TokenSerializer(serializers.Serializer):
    token = serializers.CharField()
    
    class Meta:
        examples = {
            "token_example": {
                "token": "123456abcdef"
            }
        }
