from collections import Iterable
from django.db.models import QuerySet, Q

from .utils import validate_uuid


class TBSQuerySet(QuerySet):
    def tbs_filter(self, value, *args, **kwargs):
        """
        Filters objects against pk or natural key.
        :param value: PK or natural key
        :return: Django queryset
        """
        if isinstance(value, str):
            return self._tbs_filter_str(value, *args, **kwargs)
        if isinstance(value, Iterable):
            return self._tbs_filter_iterable(value, *args, **kwargs)
        return self.filter(*args, **kwargs)

    def tbs_get(self, value):
        """
        Gets object by pk or natural key
        :param value: pk or natural key
        :return: django queryset
        """
        if validate_uuid(value):
            return self.get(pk=value)
        return self.get(**{self.model.NATURAL_KEY: value})

    def _tbs_filter_str(self, value, *args, **kwargs):
        if validate_uuid(value):
            return self.filter(*args, pk=value, **kwargs)
        return self.filter(*args, **{self.model.NATURAL_KEY: value}, **kwargs)

    def _tbs_filter_iterable(self, value, *args, **kwargs):
        uuids = [val for val in value if validate_uuid(val)]
        natural_keys = [val for val in value if not validate_uuid(val)]
        q = Q(pk__in=uuids) | Q(**{f"{self.model.NATURAL_KEY}__in": natural_keys})
        return self.filter(q, *args, **kwargs)


class TBSModelMixin:
    NATURAL_KEY = 'name'

    objects = TBSQuerySet.as_manager()
