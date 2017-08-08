from rest_framework import serializers
from rest_framework_jwt.serializers import JSONWebTokenSerializer, VerificationBaseSerializer

from servers.models import Server


class JWTSerializer(JSONWebTokenSerializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields[self.username_field] = serializers.CharField(write_only=True)
        self.fields['token'] = serializers.CharField(read_only=True)


class VerifyJSONWebTokenServerSerializer(VerificationBaseSerializer):
    def validate(self, attrs):
        token = attrs['token']

        payload = self._check_payload(token=token)
        user = self._check_user(payload=payload)
        server = self._check_server(payload=payload)

        return {
            'token': token,
            'user': user,
            'server': server
        }

    def _check_server(self, payload):
        server_id = payload.get('server_id')
        try:
            server = Server.objects.get(pk=server_id)
        except Server.DoesNotExist:
            raise serializers.ValidationError("Server doesn't exists.")
        return server
