from uuid import uuid4

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import routers, serializers, viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
import redis

r = redis.StrictRedis(host='localhost', port=6379, db=0)

# Serializers define the API representation.
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
        Allow for someone unauthenticated to register, while restricting access to users other than themselves
        for non-superusers.
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
        r.set(str(token), str(user.id))
        return Response({'token': token, 'userid': user.id})
    return Response("Invalid username/password.")


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def check_token(request, format=None):
    token_str = request.data.get('token', None)
    if token_str is None:
        return Response("Token required.")
    userid = r.get(token_str)
    if userid:
        return Response({"userid": int(userid)})
    return Response("Invalid token.")


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def logout(request, format=None):
    token_str = request.data.get('token', None)
    if token_str is None:
        return Response("Token required.")
    if r.get(token_str):
        userid_str = r.get(token_str)
        r.delete(token_str, userid_str)
    return Response("User logged out.")



# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
