import redis
import jwt
import hashlib

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import serializers, viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from uuid import uuid4
from datetime import datetime

from jrc_auth.forms import JrCUserCreationForm
from jrc_auth.settings import EXPIRATION_TIME, SECRET_SEPARATOR, JWT_SECRET

activation_tokens = redis.StrictRedis(host='localhost', port=6379, db=0)
user_keys = redis.StrictRedis(host='localhost', port=6379, db=1)


class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email')


# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (permissions.AllowAny,)

    def get_queryset(self):
        """
        Allow for someone unauthenticated to register, while
        restricting access to users other than themselves for
        non-superusers.
        """
        if self.request.user.is_superuser:
            return User.objects.all()
        else:
            return User.objects.filter(id=self.request.user.id)


def create_session_key(user_id, device_id, issued_at):
    return \
        hashlib.md5(
            str(user_id) +
            str(device_id) +
            issued_at.strftime("%s")
        ).hexdigest()


def create_secret(user_key):
    return ("{}".format(SECRET_SEPARATOR)).join([JWT_SECRET, user_key])


def create_jwt(user, device_id, user_key, issued_at, expires_at):
    payload = {
        'username': user.username,
        'userid': user.id,
        'deviceId': device_id,
        'jti': create_session_key(user.id, device_id, issued_at),
        'iat': issued_at,
        'exp': expires_at
    }
    return jwt.encode(payload, create_secret(user_key), algorithm='HS256')


def get_jwt(user, device_id):
    user_key = str(uuid4())
    issued_at = datetime.utcnow()
    expires_at = issued_at + EXPIRATION_TIME

    jwt = create_jwt(user, device_id, user_key, issued_at, expires_at)
    session_key = create_session_key(user.id, device_id, issued_at)

    user_keys.setex(str(session_key), EXPIRATION_TIME, user_key)

    return jwt


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def login(request, format=None):
    username = request.data['username']
    password = request.data['password']
    device_id = request.data['device_id']
    if None in (username, password, device_id):
        return Response({'message':
                         "username, password, device_id are required fields"})
    user = authenticate(username=username, password=password)
    if user is not None:
        token = get_jwt(user, device_id)
        return Response({'token': token})
    return Response({'message': "Invalid username/password."})


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def register(request, format=None):
    form = JrCUserCreationForm(request.data)
    if form.is_valid():
        user = form.save()
        return Response({'username': str(user), 'userid': user.pk})
    return Response(form.errors)


def activate(request, token=None):
    email = activation_tokens.get(token)
    if email:
        activation_tokens.delete(email)
        activation_tokens.delete(token)
        user = User.objects.get(email=email)
        user.is_active = True
        user.save()
        return render(request, 'jrc_auth/success.html')
    return render(request, 'jrc_auth/error.html')


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def get_user_key(request, session_key=None):
    if session_key is None:
        return Response({'message': "session_key is a mandatory parameter"})
    user_key = user_keys.get(str(session_key))
    if user_key:
        return Response({'user_key': user_key})
    return Response({'message': "Session does not exist or has expired."})


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def delete_user_key(request, session_key=None):
    if session_key is None:
        return Response({'message': "session_key is a mandatory parameter"})
    if user_keys.delete(session_key):
        return HttpResponse()
    return Response({'message': "User session expired or already deleted."})
