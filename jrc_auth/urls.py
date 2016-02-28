from django.conf.urls import url, include
from django.contrib import admin

from jrc_auth.api import router


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^admin/', admin.site.urls),
    url(r'^api-auth', include('rest_framework.urls'))
]
