from rest_framework.views import APIView
from rest_framework.authtoken.models import Token
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import authenticate


class LoginView(APIView):
    authentication_classes= []
    permission_classes= []


    def post(self, request):
        username= request.data.get('username')
        password= request.data.get('password')
        user= authenticate(username=username, password=password)
        if not user:
            return Response({"detail": "Invalid credentials"}, status= status.HTTP_401_UNAUTHORIZED)
        token,_=Token.objects.get_or_create(user=user)
        return Response({"token": token.key})


