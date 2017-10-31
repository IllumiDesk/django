"""appdj URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf import settings
from django.conf.urls import url, include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from rest_framework.decorators import api_view
from rest_framework.exceptions import NotFound, APIException
from rest_framework_nested import routers

from billing import urls as billing_urls
from infrastructure import urls as infra_urls
from projects import urls as project_urls
from servers import urls as servers_urls
from users import urls as user_urls

from servers import views as servers_views
from users import views as user_views
from triggers import views as trigger_views
from search.views import SearchView
from projects import views as project_views

router = routers.DefaultRouter()
router.register(r'projects', project_views.ProjectViewSet)
router.register(r'triggers', trigger_views.TriggerViewSet)
router.register(r'service/(?P<server>[^/.]+)/trigger', trigger_views.ServerActionViewSet)

urlpatterns = [
    url(r'^me/$', user_views.me, name="me"),
    url(r'^(?P<namespace>[\w-]+)/search/$', SearchView.as_view(), name='search'),
    url(r'^actions/', include('actions.urls')),
    url(r'^(?P<namespace>[\w-]+)/triggers/send-slack-message/$', trigger_views.SlackMessageView.as_view(),
        name='send-slack-message'),
    url(r'^(?P<namespace>[\w-]+)/triggers/(?P<trigger>[\w-]+)/start/$', trigger_views.start,
        name='trigger-start'),
    url(r'^(?P<namespace>[\w-]+)/triggers/(?P<trigger>[\w-]+)/stop/$', trigger_views.stop,
        name='trigger-stop'),
    url(r'^(?P<namespace>[\w-]+)/', include(router.urls)),
    url(r'^(?P<namespace>[\w-]+)/', include(project_urls.project_router.urls)),
    url(r'^users/', include(user_urls.user_router.urls)),
    url(r'^users/(?P<user_pk>[\w-]+)/ssh-key/$', user_views.ssh_key, name='ssh_key'),
    url(r'^users/(?P<user_pk>[\w-]+)/ssh-key/reset/$', user_views.reset_ssh_key,
        name='reset_ssh_key'),
    url(r'^users/(?P<user_pk>[\w-]+)/api-key/$', user_views.api_key, name='api_key'),
    url(r'^users/(?P<user_pk>[\w-]+)/avatar/$', user_views.avatar, name='avatar'),
    url(r'^(?P<namespace>[\w-]+)/service/(?P<server>[^/.]+)/trigger/(?P<pk>[^/.]+)/call/$',
        trigger_views.call_trigger, name='server-trigger-call'),
    url(r'^(?P<namespace>[\w-]+)/projects/(?P<project_project>[\w-]+)/servers/(?P<server>[^/.]+)/start/$',
        servers_views.start, name='server-start'),
    url(r'^(?P<namespace>[\w-]+)/projects/(?P<project_project>[\w-]+)/servers/(?P<server>[^/.]+)/stop/$',
        servers_views.stop, name='server-stop'),
    url(r'^(?P<namespace>[\w-]+)/projects/(?P<project_project>[\w-]+)/servers/(?P<server>[^/.]+)/terminate/$',
        servers_views.terminate, name='server-terminate'),

    url(r'^(?P<namespace>[\w-]+)/projects/(?P<project_project>[\w-]+)/servers/(?P<server>[^/.]+)/api-key/verify/$',
        servers_views.VerifyJSONWebTokenServer.as_view(), name='server-api-key-verify'),
    url(r'^(?P<namespace>[\w-]+)/projects/(?P<project_project>[\w-]+)/servers/(?P<server>[^/.]+)/auth/$',
        servers_views.check_token, name='server-auth'),
    url(r'^servers/', include(servers_urls.servers_router.urls)),
    url(r'^(?P<namespace>[\w-]+)/notifications/', include("notifications.urls"))

]


@api_view()
def handler404(request):
    raise NotFound()


@api_view()
def handler500(request):
    raise APIException(detail="Internal Server Error", code=500)


if settings.DEBUG:
    urlpatterns = staticfiles_urlpatterns() + urlpatterns
