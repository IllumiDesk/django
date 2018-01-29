from rest_framework import serializers
from oauth2_provider.models import Application


class ApplicationSerializer(serializers.ModelSerializer):
    user = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Application
        fields = ('client_id', 'redirect_uris', 'client_type', 'client_secret',
                  'name', 'authorization_grant_type', 'user')
        read_only_fields = ('client_id', 'client_secret')
