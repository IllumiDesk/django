from django.conf.urls import url
from .views import NotificationViewSet, NotificationSettingsViewset


urlpatterns = [
    url(r'^settings/$', NotificationSettingsViewset.as_view({'post': 'create',
                                                             'patch': 'partial_update',
                                                             'delete': 'destroy',
                                                             'get': 'retrieve'}),
        name='notification-settings'),
    url(r'^settings/entity/(?P<entity>[\w-]+)/$', NotificationSettingsViewset.as_view({'post': 'create',
                                                                                       'patch': 'partial_update',
                                                                                       'delete': 'destroy',
                                                                                       'get': 'retrieve'}),
        name='notification-settings-with-entity'),
    url(r'^$',
        NotificationViewSet.as_view({'get': 'list', 'patch': 'partial_update'}),
        name='notification-list'),
    url(r'^(?P<pk>[a-f0-9]{8}-?[a-f0-9]{4}-?4[a-f0-9]{3}-?[89ab][a-f0-9]{3}-?[a-f0-9]{12})/$',
        NotificationViewSet.as_view({'get': 'retrieve', 'patch': 'partial_update'}),
        name='notification-detail'),
    url(r'^entity/(?P<entity>[\w-]+)/$',
        NotificationViewSet.as_view({'get': 'list', 'patch': 'partial_update'}),
        name='notification-with-entity-list'),


]