from django.contrib.auth import authenticate, login, logout
from rest_framework import status, generics
from rest_framework.views import APIView
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response
from rest_framework.permissions import AllowAny

from user.models import User, Term
from user.serializer import RegisterSerializer, TermSerializer, LoginSerializer, \
                        ProfileSerializer, ProfileUpdateSerializer


class LoginAPI(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = authenticate(request, username=serializer.data['username'],
                            password=serializer.data['password'])
        if user.groups.filter(name='banned').exists():
            raise AuthenticationFailed('你已被封禁, 如有疑问请与管理员联系.')
        if user is not None:
            if not user.term_agreed:
                if not serializer.data.get('allow_terms'):
                    data = {"term": TermSerializer(Term.objects.enabled_term(), many=True).data}
                    return Response(data, status=status.HTTP_403_FORBIDDEN)
                user.term_agreed = True
                user.save()
            login(request, user)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise AuthenticationFailed()


class LogoutAPI(APIView):
    def post(self, request):
        logout(request)
        return Response(status=status.HTTP_204_NO_CONTENT)


class RegisterAPI(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = RegisterSerializer


class ProfileAPI(APIView):
    def get(self, request):
        user = request.user
        serializer = ProfileSerializer(user)
        return Response(serializer.data)

    def put(self, request):
        user = request.user
        serializer = ProfileUpdateSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_204_NO_CONTENT)
