import logging
import ujson

from django.contrib.auth import get_user_model
from django.http import HttpRequest, HttpResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.views import get_view_name
from jwt_auth.serializers import VerifyJSONWebTokenSerializer

from actions.models import Action
from triggers.models import Trigger

log = logging.getLogger('actions')

User = get_user_model()


def get_user_from_jwt(token):
    serializer = VerifyJSONWebTokenSerializer(data={'token': token})
    if serializer.is_valid():
        return serializer.validated_data.get('user')


def get_user_from_token_header(request):
    token_header = request.META.get('HTTP_AUTHORIZATION')
    if not token_header or ' ' not in token_header:
        return
    prefix, token = token_header.split()
    if prefix == 'Bearer':
        return get_user_from_jwt(token)


class ActionMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request: HttpRequest) -> HttpResponse:
        start = timezone.now()
        path = request.get_full_path()
        try:
            if request.content_type.lower() == "multipart/form-data":
                body = {}
            else:
                body = ujson.loads(request.body)
        except ValueError:
            body = {}
        user = get_user_from_token_header(request)
        trigger_cause = Trigger.objects.filter(
            cause__path=path,
            cause__user=user,
            cause__state=Action.CREATED
        ).first()
        if trigger_cause is not None:
            action = trigger_cause.cause
        else:
            action = Action.objects.create(
                path=path,
                user=user,
                method=request.method.lower(),
                user_agent=request.META.get('HTTP_USER_AGENT', ''),
                start_date=start,
                ip=self._get_client_ip(request),
                payload=body,
                state=Action.PENDING,
                headers=dict(request.META),
            )
        request.action = action

        response = self.get_response(request)  # type: HttpResponse

        action.refresh_from_db()
        action.action = self._get_action_name(request)
        self._set_action_state(action, response.status_code)
        self._set_action_object(action, request, response)
        action.end_date = timezone.now()
        if action.user is None:
            action.user = request.user if isinstance(request.user, User) else None
        action.save()
        return response

    @staticmethod
    def _set_action_state(action, status_code):
        action.state = Action.PENDING
        if action.can_be_cancelled:
            action.state = Action.IN_PROGRESS
        elif status.is_client_error(status_code):
            action.state = Action.FAILED
        elif status.is_success(status_code):
            action.state = Action.SUCCESS

    def _set_action_object(self, action, request, response):
        if request.resolver_match is None:
            return
        if 'pk' in request.resolver_match.kwargs:
            action.content_object = self._get_object_from_url(request)
        if request.method.lower() == 'post':
            content_object = self._get_object_from_post_data(request, response)
            if content_object is not None:
                action.content_object = content_object

    def _get_object_from_post_data(self, request, response):
        model = self._get_model_from_func(request.resolver_match.func)
        if model is not None:
            if hasattr(response, 'data'):
                data = response.data
                pk = self._get_object_pk_from_response_data(data)
                if pk:
                    return model.objects.filter(pk=pk).first()

    def _get_object_pk_from_response_data(self, data) -> str:
        pk = ''
        if data is None or isinstance(data, list):
            return pk
        for key in data:
            if key == 'id':
                pk = data[key]
            elif isinstance(data[key], dict):
                pk = self._get_object_pk_from_response_data(data[key])
            if pk:
                break
        return pk

    @staticmethod
    def _get_model_from_func(view_func):
        if hasattr(view_func, 'cls') and getattr(view_func.cls, 'queryset', None) is not None:
            return view_func.cls.queryset.model

    def _get_object_from_url(self, request: HttpRequest):
        model = self._get_model_from_func(request.resolver_match.func)
        if model is not None:
            pk = request.resolver_match.kwargs['pk']
            try:
                return model.objects.tbs_filter(pk).first()
            except AttributeError:
                return model.objects.filter(pk=pk).first()

    @staticmethod
    def _get_action_name(request: HttpRequest) -> str:
        if request.resolver_match is not None:
            if hasattr(request.resolver_match.func, 'cls'):
                name = get_view_name(request.resolver_match.func.cls)
            else:
                name = request.resolver_match.view_name.replace('_', ' ').replace('-', ' ').capitalize()
        else:
            name = 'Unknown'
        return name

    @staticmethod
    def _get_client_ip(request: HttpRequest) -> str:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[-1].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
