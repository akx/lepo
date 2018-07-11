from lepo.apidef.operation.base import Operation
from lepo.apidef.parameter.openapi import OpenAPI3BodyParameter, OpenAPI3Parameter
from lepo.utils import maybe_resolve


class OpenAPI3Operation(Operation):
    parameter_class = OpenAPI3Parameter
    body_parameter_class = OpenAPI3BodyParameter

    def _get_body_parameter(self):
        for source in (
            self.path.mapping.get('requestBody'),
            self.data.get('requestBody'),
        ):
            if source:
                source = maybe_resolve(source, self.api.resolve_reference)
                body_parameter = self.body_parameter_class(data=source, operation=self, api=self.api)
                # TODO: Document x-lepo-body-name
                body_parameter.name = self.data.get('x-lepo-body-name', body_parameter.name)
                return body_parameter

    def get_parameter_dict(self):
        parameter_dict = super().get_parameter_dict()
        for parameter in parameter_dict.values():
            if parameter.in_body:  # pragma: no cover
                raise ValueError('Regular parameter declared to be in body while parsing OpenAPI 3')
        body_parameter = self._get_body_parameter()
        if body_parameter:
            parameter_dict[body_parameter.name] = body_parameter
        return parameter_dict
