from appdj.base.models import TBSQuerySet
from appdj.base.utils import validate_uuid


class ProjectQuerySet(TBSQuerySet):
    def namespace(self, namespace):
        if namespace.type == 'user':
            return self.filter(collaborator__user=namespace.object)
        return self.filter(team=namespace.object)


class CollaboratorQuerySet(TBSQuerySet):
    def namespace(self, namespace):
        return self.filter(user=namespace.object)

    def tbs_get(self, value):
        if validate_uuid(value):
            return self.get(pk=value)
        return self.get(user__username=value)

    def _tbs_filter_str(self, value, *args, **kwargs):
        if validate_uuid(value):
            return self.filter(*args, user_id=value, **kwargs)
        return self.filter(*args, user__username=value, **kwargs)

    def _tbs_filter_iterable(self, value, *args, **kwargs):
        uuids = []
        natural_keys = []
        for val in value:
            if validate_uuid(val):
                uuids.append(val)
            else:
                natural_keys.append(val)
        return self.filter(*args, user_id__in=uuids, user__username__in=natural_keys, **kwargs)