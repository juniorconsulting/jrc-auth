from django.conf.urls import url, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from jrc_auth.api import router, login, check_token, logout


urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^login/', login),
    url(r'^check-token', check_token),
    url(r'^logout/', logout),
    url(r'^admin/', admin.site.urls),
    url(r'^api-auth', include('rest_framework.urls'))
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

