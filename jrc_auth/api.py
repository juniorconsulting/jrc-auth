from uuid import uuid4, UUID

from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework import routers, serializers, viewsets, permissions, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response

# Two dictionaries for easy reverse lookup.
logged_in_token = {}
logged_in_userid = {}


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
        if user.id not in logged_in_userid:
            token = uuid4()
            logged_in_token[token] = user.id
            logged_in_userid[user.id] = token
        else:
            token = logged_in_userid[user.id]
        return Response({'token': token, 'userid': user.id})
    return Response("Invalid username/password.", status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def check_token(request, format=None):
    token_str = request.data.get('token', None)
    if token_str is not None:
        token = UUID(token_str)
    else:
        return Response("Token required.", status=status.HTTP_400_BAD_REQUEST)
    if token in logged_in_token:
        return Response({"userid": logged_in_token[token]})
    return Response("Invalid token.", status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes((permissions.AllowAny,))
def logout(request, format=None):
    token_str = request.data.get('token', None)
    if token_str is not None:
        token = UUID(token_str)
    else:
        return Response("Token required.", status=status.HTTP_400_BAD_REQUEST)
    if token in logged_in_token:
        userid = logged_in_token[token]
        del logged_in_token[token]
        del logged_in_userid[userid]
    return Response("User logged out.")



# Routers provide an easy way of automatically determining the URL conf.
router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
