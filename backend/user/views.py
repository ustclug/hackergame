from django.contrib.auth import authenticate, login, logout
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from user.models import User, Term
from user.serializer import RegisterSerializer, TermSerializer, LoginSerializer, ProfileSerializer


class LoginAPI(APIView):
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(request, username=serializer.data['username'],
                            password=serializer.data['password'])
        if user is not None:
            if not user.term_agreed:
                if not serializer.data['allow_terms']:
                    return Response(TermSerializer(Term.objects.enabled_term()),
                                    status=status.HTTP_403_FORBIDDEN)
                user.term_agreed = True
                user.save()
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


class ProfileAPI(generics.RetrieveAPIView):
    queryset = User.objects.all()
    serializer_class = ProfileSerializer
