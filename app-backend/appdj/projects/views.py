import logging
import json
import shutil
from urllib.parse import quote

from django.http import Http404
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q

from oauth2_provider.models import Application as ProviderApp
from rest_framework import viewsets, status, permissions
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.generics import CreateAPIView
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView

from appdj.base.views import NamespaceMixin, LookupByMultipleFields
from appdj.base.utils import validate_uuid
from appdj.canvas.models import CanvasInstance
from appdj.servers.utils import get_server_url, create_server
from appdj.jwt_auth.utils import create_auth_jwt
from appdj.oauth2.models import Application
from appdj.teams.models import Team
from appdj.teams.permissions import TeamGroupPermission
from .serializers import (
    ProjectSerializer,
    CollaboratorSerializer,
    CloneGitProjectSerializer
)
from .models import Project, Collaborator
from .permissions import ProjectPermission, ProjectChildPermission
from .utils import (
    has_copy_permission,
    perform_project_copy,
    check_project_name_exists
)


logger = logging.getLogger(__name__)

User = get_user_model()


class ProjectViewSet(LookupByMultipleFields, NamespaceMixin, viewsets.ModelViewSet):
    queryset = Project.objects.filter(is_active=True)
    serializer_class = ProjectSerializer
    permission_classes = (permissions.IsAuthenticated, ProjectPermission, TeamGroupPermission)
    filter_fields = ('private', 'name')
    ordering_fields = ('name',)
    lookup_url_kwarg = 'project'

    def get_queryset(self):
        qs = super().get_queryset()
        return qs.filter(Q(private=False) | Q(collaborator__user=self.request.user)).distinct()

    def update(self, request, *args, **kwargs):
        if not validate_uuid(kwargs.get('project', '')):
            raise Http404
        return super().update(request, *args, **kwargs)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        user = request.user
        is_owner = Collaborator.objects.filter(project=instance,
                                               user=user,
                                               owner=True)
        if not is_owner.exists():
            return Response(data={'message': "Insufficient permissions to delete project"},
                            status=status.HTTP_403_FORBIDDEN)

        instance.is_active = False
        instance.save()
        if instance.resource_root().is_dir():
            shutil.rmtree(instance.resource_root())
        return Response(data={"message": "Project deleted."},
                        status=status.HTTP_204_NO_CONTENT)


@api_view(['post'])
def project_copy(request, *args, **kwargs):
    proj_identifier = request.data['project']
    new_project_name = request.data.get('name')

    if new_project_name:
        logger.info("Project name found in request during project copy. Validating name: %s", new_project_name)
        if check_project_name_exists(new_project_name, request, None):
            logger.exception("Project %s already exists.", new_project_name)
            resp_status = status.HTTP_400_BAD_REQUEST
            resp_data = {'message': f"A project named {new_project_name} already exists."}
            return Response(data=resp_data, status=resp_status)

    try:
        # If user didn't provide a name, perform_project_copy() will handle duplicates appropriately
        new_project = perform_project_copy(user=request.user,
                                           project_id=proj_identifier,
                                           request=request,
                                           new_name=new_project_name)
    except Exception as e:
        logger.exception(f"There was a problem attempting to copy project {proj_identifier}, {e}.", e)
        resp_status = status.HTTP_500_INTERNAL_SERVER_ERROR
        resp_data = {'message': "Internal Server Error when attempting to copy project."}
    else:
        if new_project is not None:
            resp_status = status.HTTP_201_CREATED
            serializer = ProjectSerializer(instance=new_project)
            resp_data = serializer.data
        else:
            resp_status = status.HTTP_404_NOT_FOUND
            resp_data = {'message': f"Project {proj_identifier} not found."}
    return Response(data=resp_data, status=resp_status)


@api_view(['post'])
def project_copy_check(request, *args, **kwargs):
    has_perm = has_copy_permission(request=request)
    if has_perm:
        resp_status = status.HTTP_200_OK
    else:
        resp_status = status.HTTP_404_NOT_FOUND

    return Response(status=resp_status)


class ProjectMixin(LookupByMultipleFields):
    permission_classes = (permissions.IsAuthenticated, ProjectChildPermission, TeamGroupPermission)


class CollaboratorViewSet(ProjectMixin, viewsets.ModelViewSet):
    queryset = Collaborator.objects.all()
    serializer_class = CollaboratorSerializer


class CloneGitProject(CreateAPIView):
    queryset = Project.objects.filter(is_active=True)
    serializer_class = CloneGitProjectSerializer


class FileSelection(APIView):
    permission_classes = ()
    parser_classes = (FormParser, MultiPartParser)
    renderer_classes = (TemplateHTMLRenderer,)

    def get(self, request, *args, **kwargs):
        return self._common(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        return self._common(request, *args, **kwargs)

    def _common(self, request, *args, **kwargs):
        projects = Project.objects.filter(
            Q(collaborator__user=request.user) | Q(team__in=Team.objects.filter(groups__user=request.user)),
            Q(is_active=True),
            Q(collaborator__owner=True)
        )

        projects_context = []
        for project in projects:
            project_root = project.resource_root()
            if not project_root.exists():
                continue
            workspace = project.servers.filter(config__type='jupyter', is_active=True).first()
            if workspace is None:
                workspace = create_server(request.user, project, 'workspace')
            files = []
            assignment_id = request.data.get('ext_lti_assignment_id')
            if assignment_id and (project_root / 'release').exists():
                root = project_root / 'release'
            else:
                root = project_root
            for f in self._iterate_dir(root):
                path = str(f.relative_to(project_root))
                quoted = quote(path, safe='/')
                scheme = 'https' if settings.HTTPS else 'http'
                url = get_server_url(str(project.pk), str(workspace.pk), scheme,
                                     f"/{quoted}", namespace=project.namespace_name)
                files.append({
                    'path': path,
                    'project': project.id,
                    'content_items': json.dumps({
                        "@context": "http://purl.imsglobal.org/ctx/lti/v1/ContentItem",
                        "@graph": [{
                            "@type": "LtiLinkItem",
                            "@id": url,
                            "url": url,
                            "title": f.name,
                            "text": f.name,
                            "mediaType": "application/vnd.ims.lti.v1.ltilink",
                            "placementAdvice": {"presentationDocumentTarget": "frame"}
                        }]
                    })
                })
            projects_context.append({
                'name': project.name,
                'files': files
            })

        if 'lti_version' in request.data:
            context = self.get_v1_context(request, projects_context)
        else:
            context = self.get_v13_context(request, projects_context)

        return Response(context, template_name='projects/file_selection.html')

    @staticmethod
    def get_v1_context(request, projects_context):
        course_id = request.META['HTTP_REFERER'].split('/')[4]
        oauth_app, _ = Application.objects.get_or_create(
            application=ProviderApp.objects.get(client_id=request.data['oauth_consumer_key']))
        return {
            'course_id': course_id,
            'token': create_auth_jwt(request.user),
            'lti_version': request.data['lti_version'],
            'projects': projects_context,
            'action_url': request.data['content_item_return_url'],
            'assignment_id': request.data['ext_lti_assignment_id'],
            'canvas_instance_id': CanvasInstance.objects.filter(
                instance_guid=request.data['tool_consumer_instance_guid']).first().pk,
            'oauth_app': str(oauth_app.pk),
            'version': request.version,
            'namespace': request.namespace
        }

    @staticmethod
    def get_v13_context(request, projects_context):
        instance_guid = request.auth['https://purl.imsglobal.org/spec/lti/claim/tool_platform']['guid']
        oauth_app, _ = Application.objects.get_or_create(
            application=ProviderApp.objects.get(client_id=request.auth['aud']))
        return {
            'token': create_auth_jwt(request.user),
            'lti_version': request.auth['https://purl.imsglobal.org/spec/lti/claim/version'],
            'projects': projects_context,
            'action_url': request.auth['https://purl.imsglobal.org/spec/lti/claim/launch_presentation']['return_url'],
            'course_id': request.auth['https://purl.imsglobal.org/spec/lti/claim/context']['id'],
            'canvas_instance_id': CanvasInstance.objects.filter(
                instance_guid=instance_guid).first().pk,
            'oauth_app': str(oauth_app.pk),
            'version': request.version,
            'namespace': request.user.username
        }

    def _iterate_dir(self, directory):
        for item in directory.iterdir():
            if item.name.startswith('.') or item.name.startswith('submissions'):
                continue
            if item.is_dir():
                yield from self._iterate_dir(item)
            else:
                yield item
