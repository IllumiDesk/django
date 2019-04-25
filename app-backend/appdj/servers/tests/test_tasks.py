import uuid
from unittest import TestCase
from django.contrib.auth import get_user_model

from appdj.projects.utils import perform_project_copy
from appdj.projects.tests.factories import CollaboratorFactory, ProjectFactory
from appdj.teams.tests.factories import TeamFactory, GroupFactory
from appdj.users.tests.factories import UserFactory
from .factories import ServerFactory
from ..models import Server, ServerSize
from ..tasks import lti

User = get_user_model()


class LTITest(TestCase):
    def setUp(self):
        ServerSize.objects.get_or_create(
            name='Nano',
            cpu=1,
            memory=512,
            active=True,
            cost_per_second=0.0
        )
        col = CollaboratorFactory(
            project__copying_enabled=True,
            project__private=False
        )
        self.project = col.project
        self.project.resource_root().mkdir(parents=True, exist_ok=True)
        self.user = col.user

    def test_lti_copy(self):
        data = {
            'user_id': str(uuid.uuid4()),
            'lis_person_contact_email_primary': 'jdoe@example.com',
        }
        workspace_id, assignment_id = lti(
            str(self.project.pk), data, '')
        self.assertTrue(User.objects.filter(username='jdoe').exists())
        self.assertTrue(Server.objects.filter(pk=workspace_id).exists())

    def test_lti_user_exists(self):
        canvas_user_id = str(uuid.uuid4())
        learner = UserFactory()
        learner.profile.config = {'canvas_user_id': canvas_user_id}
        learner.profile.save()
        data = {
            'user_id': canvas_user_id,
            'lis_person_contact_email_primary': learner.email,
        }
        workspace_id, assignment_id = lti(
            str(self.project.pk), data, '')
        self.assertTrue(Server.objects.filter(pk=workspace_id).exists())
        workspace = Server.objects.get(pk=workspace_id)
        self.assertEqual(learner.pk, workspace.project.owner.pk)

    def test_lti_user_project_exists(self):
        canvas_user_id = str(uuid.uuid4())
        learner = UserFactory()
        learner.profile.config = {'canvas_user_id': canvas_user_id}
        learner.profile.save()
        data = {
            'user_id': canvas_user_id,
            'lis_person_contact_email_primary': learner.email,
        }
        learner_project = perform_project_copy(learner, str(self.project.pk))
        workspace_id, assignment_id = lti(
            str(self.project.pk), data, '')
        self.assertTrue(Server.objects.filter(pk=workspace_id).exists())
        workspace = Server.objects.get(pk=workspace_id)
        self.assertEqual(learner.pk, workspace.project.owner.pk)
        self.assertEqual(learner_project.pk, workspace.project.pk)

    def test_lti_user_project_server_exists(self):
        canvas_user_id = str(uuid.uuid4())
        learner = UserFactory()
        learner.profile.config = {'canvas_user_id': canvas_user_id}
        learner.profile.save()
        data = {
            'user_id': canvas_user_id,
            'lis_person_contact_email_primary': learner.email,
        }
        learner_project = perform_project_copy(learner, str(self.project.pk))
        workspace = ServerFactory(
            project=learner_project,
            config={'type': 'jupyter'},
            is_active=True
        )
        workspace_id, assingment_id = lti(
            str(self.project.pk), data, '')
        self.assertEqual(workspace_id, str(workspace.pk))


class LTITeamsTest(TestCase):
    def setUp(self):
        ServerSize.objects.get_or_create(
            name='Nano',
            cpu=1,
            memory=512,
            active=True,
            cost_per_second=0.0
        )
        self.user = UserFactory()
        self.team = TeamFactory()
        self.group = GroupFactory(name='owners', team=self.team)
        self.user.team_groups.add(self.group)
        self.project = ProjectFactory(team=self.team, private=False)
        self.project.resource_root().mkdir(parents=True, exist_ok=True)

    def test_lti_copy(self):
        data = {
            'user_id': str(uuid.uuid4()),
            'lis_person_contact_email_primary': 'jdoe@example.com',
        }
        workspace_id, assignment_id = lti(str(self.project.pk), data, '')
        self.assertTrue(User.objects.filter(username='jdoe').exists())
        self.assertTrue(Server.objects.filter(pk=workspace_id).exists())

    def test_lti_user_exists(self):
        canvas_user_id = str(uuid.uuid4())
        learner = UserFactory()
        learner.profile.config = {'canvas_user_id': canvas_user_id}
        learner.profile.save()
        data = {
            'user_id': canvas_user_id,
            'lis_person_contact_email_primary': learner.email,
        }
        workspace_id, assignment_id = lti(str(self.project.pk), data, '')
        self.assertTrue(Server.objects.filter(pk=workspace_id).exists())
        workspace = Server.objects.get(pk=workspace_id)
        self.assertEqual(learner.pk, workspace.project.owner.pk)

    def test_lti_user_project_exists(self):
        canvas_user_id = str(uuid.uuid4())
        learner = UserFactory()
        learner.profile.config = {'canvas_user_id': canvas_user_id}
        learner.profile.save()
        data = {
            'user_id': canvas_user_id,
            'lis_person_contact_email_primary': learner.email,
            'ext_roles': ''
        }
        learner_project = perform_project_copy(learner, str(self.project.pk))
        learner_project.team = None
        learner_project.save()
        workspace_id, assignment_id = lti(str(self.project.pk), data, '')
        self.assertTrue(Server.objects.filter(pk=workspace_id).exists())
        workspace = Server.objects.get(pk=workspace_id)
        self.assertEqual(learner.pk, workspace.project.owner.pk)
        self.assertEqual(learner_project.pk, workspace.project.pk)

    def test_lti_user_project_server_exists(self):
        canvas_user_id = str(uuid.uuid4())
        learner = UserFactory()
        learner.profile.config = {'canvas_user_id': canvas_user_id}
        learner.profile.save()
        data = {
            'user_id': canvas_user_id,
            'lis_person_contact_email_primary': learner.email,
            'ext_roles': ''
        }
        learner_project = perform_project_copy(learner, str(self.project.pk))
        workspace = ServerFactory(
            project=learner_project,
            config={'type': 'jupyter'},
            is_active=True
        )
        workspace_id, assingment_id = lti(
            str(self.project.pk), data, '')
        self.assertEqual(workspace_id, str(workspace.pk))