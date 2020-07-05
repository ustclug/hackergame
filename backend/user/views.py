from django.contrib.auth import authenticate, login, logout
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import User
from .serializer import RegisterSerializer


class LoginAPI(APIView):
    def post(self, request):
        username = request.data['username']
        password = request.data['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise AuthenticationFailed()


class LogoutAPI(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        logout(request)


class RegisterAPI(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
