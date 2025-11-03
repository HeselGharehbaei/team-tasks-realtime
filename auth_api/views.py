from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate
from drf_spectacular.utils import extend_schema
from .serializers import LoginSerializer, TokenSerializer
from drf_spectacular.utils import extend_schema, OpenApiExample


class LoginView(APIView):
    authentication_classes= []
    permission_classes= []

    @extend_schema(
        request=LoginSerializer,
        responses={200: TokenSerializer},
        summary="ورود کاربر",
        description="لاگین با نام کاربری و رمز عبور و دریافت توکن",
        tags=['Auth'],
        examples=[
            OpenApiExample(
                "نمونه لاگین",
                value={
                    "username": "ali",
                    "password": "12345678"
                },
                request_only=True,
                response_only=False
            ),
            OpenApiExample(
                "نمونه توکن",
                value={
                    "token": "123456abcdef"
                },
                request_only=False,
                response_only=True
            )
        ]
    )


    def post(self, request):
        username= request.data.get('username')
        password= request.data.get('password')
        user= authenticate(username=username, password=password)
        if not user:
            return Response({"detail": "Invalid credentials"}, status= status.HTTP_401_UNAUTHORIZED)
        token,_=Token.objects.get_or_create(user=user)
        return Response({"token": token.key})


