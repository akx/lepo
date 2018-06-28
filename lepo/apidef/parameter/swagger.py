from django.utils.encoding import force_text

from lepo.apidef.parameter.base import BaseParameter, BaseTopParameter
from lepo.apidef.parameter.utils import read_body
from lepo.excs import InvalidBodyFormat

COLLECTION_FORMAT_SPLITTERS = {
    'csv': lambda value: force_text(value).split(','),
    'ssv': lambda value: force_text(value).split(' '),
    'tsv': lambda value: force_text(value).split('\t'),
    'pipes': lambda value: force_text(value).split('|'),
}


class Swagger2BaseParameter(BaseParameter):

    @property
    def collection_format(self):
        return self.data.get('collectionFormat')

    def arrayfy_value(self, value):
        collection_format = self.collection_format or 'csv'
        splitter = COLLECTION_FORMAT_SPLITTERS.get(collection_format)
        if not splitter:
            raise NotImplementedError('unsupported collection format in %r' % self)
        value = splitter(value)
        return value


class Swagger2Parameter(Swagger2BaseParameter, BaseTopParameter):

    def get_value(self, request, view_kwargs):
        if self.location == 'body':
            return self.read_body(request)

        if self.location == 'formData' and self.type == 'file':
            return request.FILES[self.name]

        if self.location in ('query', 'formData'):
            source = (request.POST if self.location == 'formData' else request.GET)
            print(self.name, self.data)
            if self.type == 'array' and self.collection_format == 'multi':
                return source.getlist(self.name)
            else:
                return source[self.name]

        return super().get_value(request, view_kwargs)

    def read_body(self, request):
        consumes = request.api_info.operation.consumes
        if request.content_type not in consumes:
            raise InvalidBodyFormat('Content-type %s is not supported (%r are)' % (
                request.content_type,
                consumes,
            ))

        return read_body(request, None)
