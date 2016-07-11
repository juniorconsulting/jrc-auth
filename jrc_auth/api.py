from uuid import uuid4
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.shortcuts import render
from rest_framework import serializers, viewsets, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
import redis

from jrc_auth.forms import JrCUserCreationForm

r = redis.StrictRedis(host='localhost', port=6379, db=0)
r_act = redis.StrictRedis(host='localhost', port=6379, db=1)


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


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def login(request, format=None):
    username = request.data['username']
    password = request.data['password']
    user = authenticate(username=username, password=password)
    if user is not None:
        token_str = r.get(str(user.id))
        if token_str:
            r.delete((str(user.id), token_str))
            r.delete(token_str, str(user.id))
        token = uuid4()
        r.set(str(user.id), str(token))
        r.expire(str(user.id), 86400 * 14)  # Expire in 14 days
        r.set(str(token), str(user.id))
        r.expire(str(token), 86400 * 14)
        return Response({'token': token, 'userid': user.id})
    return Response({'message': "Invalid username/password."})


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def check_token(request, format=None):
    token_str = request.data.get('token', None)
    if token_str is None:
        return Response({'message': "Token required."})
    userid = r.get(token_str)
    if userid:
        return Response({"userid": int(userid)})
    return Response({'message': "Invalid token."})


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def logout(request, format=None):
    token_str = request.data.get('token', None)
    if token_str is None:
        return Response({'message': "Token required."})
    if r.get(token_str):
        userid_str = r.get(token_str)
        r.delete(token_str, userid_str)
    return Response({'message': "User logged out."})


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def register(request, format=None):
    form = JrCUserCreationForm(request.data)
    if form.is_valid():
        user = form.save()
        return Response({'username': str(user), 'userid': user.pk})
    return Response(form.errors)


def activate(request, token=None):
    email = r_act.get(token)
    if email:
        r_act.delete(email)
        r_act.delete(token)
        user = User.objects.get(email=email)
        user.is_active = True
        user.save()
        return render(request, 'jrc_auth/success.html')
    return render(request, 'jrc_auth/error.html')
