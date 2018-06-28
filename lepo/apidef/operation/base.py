from collections.__init__ import OrderedDict

from django.utils.functional import cached_property

from lepo.utils import maybe_resolve


class Operation:
    parameter_class = None  # This should never be used

    def __init__(self, api, path, method, data):
        """
        :type api: lepo.apidef.doc.APIDefinition
        :type path: lepo.apidef.path.Path
        :type method: str
        :type data: dict
        """
        self.api = api
        self.path = path
        self.method = method
        self.data = data

    @property
    def id(self):
        return self.data['operationId']

    @cached_property
    def parameters(self):
        """
        Combined path-level and operation-level parameters.

        Any $refs are resolved here.

        Note that this implementation differs from the spec in that we only use
        the _name_ of a parameter to consider its uniqueness, not the name and location.

        This is because we end up passing parameters to the handler by name anyway,
        so any duplicate names, even if they had different locations, would be horribly mangled.

        :rtype: list[Parameter]
        """
        return list(self.get_parameter_dict().values())

    def get_parameter_dict(self):
        parameters = OrderedDict()
        for parameter in self._get_regular_parameters():
            parameters[parameter.name] = parameter
        return parameters

    def _get_regular_parameters(self):
        for source in (
            self.path.mapping.get('parameters', ()),
            self.data.get('parameters', {}),
        ):
            source = maybe_resolve(source, self.api.resolve_reference)
            for parameter in source:
                parameter_data = maybe_resolve(parameter, self.api.resolve_reference)
                parameter = self.parameter_class(data=parameter_data, operation=self, api=self.api)
                yield parameter

    def _get_overridable(self, key, default=None):
        # TODO: This probes a little too deeply into the specifics of these objects, I think...
        for obj in (
            self.data,
            self.path.mapping,
            self.api.doc,
        ):
            if key in obj:
                return obj[key]
        return default
