from collections import namedtuple, OrderedDict

from django.utils.functional import cached_property

from lepo.apidef.parameter.base import BaseParameter, BaseTopParameter, NO_VALUE
from lepo.apidef.parameter.utils import comma_split, pipe_split, read_body, space_split, validate_schema, dot_split
from lepo.excs import InvalidBodyFormat, InvalidParameterDefinition
from lepo.parameter_utils import cast_primitive_value
from lepo.utils import get_content_type_specificity, match_content_type, maybe_resolve


class OpenAPI3Schema:
    def __init__(self, data):
        self.data = data

    @property
    def type(self):
        return self.data.get('type')

    @property
    def format(self):
        return self.data.get('format')

    @property
    def items(self):
        return self.data['items']

    @property
    def has_default(self):
        return 'default' in self.data

    @property
    def default(self):
        return self.data.get('default')

    def cast(self, api, value):
        value = cast_primitive_value(self.type, self.format, value)
        value = validate_schema(self.data, api, value)
        return value


class OpenAPI3BaseParameter(BaseParameter):
    @cached_property
    def schema(self):
        schema = self.data['schema']
        schema = maybe_resolve(schema, resolve=(self.api.resolve_reference if self.api else None))
        return OpenAPI3Schema(schema)

    @property
    def type(self):
        return self.schema.type

    @property
    def has_default(self):
        return self.schema.has_default

    @property
    def default(self):
        return self.schema.default

    def cast_array(self, api, value):
        assert isinstance(value, list)
        item_schema = OpenAPI3Schema(self.schema.items)
        return [item_schema.cast(api, item) for item in value]

    def cast(self, api, value):
        if self.type == 'array':
            value = self.cast_array(api, value)

        return self.schema.cast(api, value)


class OpenAPI3Parameter(OpenAPI3BaseParameter, BaseTopParameter):
    location_to_style_and_explode = {
        'query': ('form', True),
        'path': ('simple', False),
        'header': ('simple', False),
        'cookie': ('form', True),
    }

    def get_style_and_explode(self):
        explicit_style = self.data.get('style')
        explicit_explode = self.data.get('explode')
        default_style, default_explode = self.location_to_style_and_explode[self.location]
        style = (explicit_style if explicit_style is not None else default_style)
        explode = (explicit_explode if explicit_explode is not None else default_explode)
        return (style, explode)

    def get_value(self, request, view_kwargs):  # noqa: C901
        if self.location == 'body':  # pragma: no cover
            raise NotImplementedError('Should never get here, this is covered by OpenAPI3BodyParameter')

        (style, explode) = self.get_style_and_explode()
        type = self.schema.type
        splitter = comma_split

        if style == 'deepObject':
            raise NotImplementedError('deepObjects are not supported at present. PRs welcome.')

        if self.location == 'query':
            if type == 'array' and style == 'form' and explode:
                return request.GET.getlist(self.name, NO_VALUE)
            if self.name not in request.GET:
                return NO_VALUE
            value = request.GET[self.name]
            splitter = {
                'form': comma_split,
                'spaceDelimited': space_split,
                'pipeDelimited': pipe_split,
            }.get(style)

        elif self.location == 'header':
            if style != 'simple':  # pragma: no cover
                raise InvalidParameterDefinition('Header parameters always use the simple style, says the spec')
            meta_key = 'HTTP_%s' % self.name.upper().replace('-', '_')
            if meta_key not in request.META:
                return NO_VALUE
            value = request.META[meta_key]
        elif self.location == 'cookie':
            if style != 'form':  # pragma: no cover
                raise InvalidParameterDefinition('Cookie parameters always use the form style, says the spec')
            if self.name not in request.COOKIES:
                return NO_VALUE
            value = request.COOKIES[self.name]
        elif self.location == 'path':
            if self.name not in view_kwargs:
                return NO_VALUE
            value = view_kwargs[self.name]
            if style == 'simple':
                pass
            elif style == 'label':
                value = value.lstrip('.')
                splitter = (dot_split if explode else comma_split)
            elif style == 'matrix':
                raise NotImplementedError('...')  # TODO: Implement me
        else:
            return super().get_value(request, view_kwargs)

        if type in ('array', 'object'):
            if not splitter:
                raise InvalidParameterDefinition('The location/style/explode combination %s/%s/%s is not supported' % (
                    self.location,
                    style,
                    explode,
                ))
            value = splitter(value)
            if type == 'object':
                value = OrderedDict(zip(value[::2], value[1::2]))

        return value


WrappedValue = namedtuple('WrappedValue', ('parameter', 'value'))


class OpenAPI3BodyParameter(OpenAPI3Parameter):
    """
    OpenAPI 3 Body Parameter
    """

    name = '_body'

    @property
    def location(self):
        return 'body'

    @cached_property
    def media_map(self):
        return OpenAPI3MediaMap(api=self.api, mapping_data=self.data['content'])

    def get_value(self, request, view_kwargs):
        media_map = self.media_map
        content_type_name = media_map.match(request.content_type)
        if not content_type_name:
            raise InvalidBodyFormat('Content-type %s is not supported (%r are)' % (
                request.content_type,
                media_map.keys(),
            ))
        parameter = media_map[content_type_name]
        value = read_body(request, parameter=parameter)
        return WrappedValue(parameter, value)

    def cast(self, api, value):
        if not isinstance(value, WrappedValue):  # pragma: no cover
            raise TypeError('Expected a wrappedvalue :(')
        parameter, value = value
        return parameter.cast(api, value)


class OpenAPI3MediaMap(OrderedDict):
    def __init__(self, api, mapping_data):
        self.api = api
        self.mapping_data = mapping_data
        selector_to_param = [
            (selector, OpenAPI3BaseParameter(content_description, api=self.api))
            for (selector, content_description)
            in self.mapping_data.items()
        ]
        super().__init__(
            sorted(selector_to_param, key=lambda kv: get_content_type_specificity(kv[0]))
        )

    def match(self, content_type):
        return match_content_type(content_type, self)
