from django.utils.functional import cached_property

from lepo.apidef.operation.base import Operation
from lepo.apidef.parameter.swagger import Swagger2Parameter


class Swagger2Operation(Operation):
    parameter_class = Swagger2Parameter

    @cached_property
    def consumes(self):
        value = self._get_overridable('consumes', [])
        if not isinstance(value, (list, tuple)):
            raise TypeError('`consumes` must be a list, got %r' % value)  # pragma: no cover
        return value

    @cached_property
    def produces(self):
        value = self._get_overridable('produces', [])
        if not isinstance(value, (list, tuple)):
            raise TypeError('`produces` must be a list, got %r' % value)  # pragma: no cover
        return value
