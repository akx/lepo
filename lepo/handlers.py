from functools import wraps

from copy import deepcopy


class BaseHandler:
    def __init__(self, request, args):
        self.request = request
        self.args = args

    @classmethod
    def get_handler(cls, method_name):
        method = getattr(cls, method_name)

        @wraps(method)
        def view(request, **kwargs):
            handler = cls(request, kwargs)
            return method(handler)

        return view


class BaseModelHandler(BaseHandler):
    model = None
    queryset = None
    schema_class = None

    id_data_name = 'id'
    id_field_name = 'pk'

    def get_schema(self, purpose, object=None):
        return self.schema_class()

    def get_queryset(self, purpose):
        return deepcopy(self.queryset)

    def process_object_list(self, purpose, object_list):
        return object_list

    def retrieve_object(self):
        queryset = self.get_queryset('retrieve')
        return queryset.get(**{self.id_field_name: self.args[self.id_data_name]})


class ModelHandlerReadMixin(BaseModelHandler):
    def handle_list(self):
        queryset = self.get_queryset('list')
        object_list = self.process_object_list('list', queryset)
        schema = self.get_schema('list')
        return schema.dump(object_list, many=True).data

    def handle_retrieve(self):
        object = self.retrieve_object()
        schema = self.get_schema('retrieve')
        return schema.dump(object).data


class ModelHandlerCreateMixin(BaseModelHandler):
    create_data_name = 'data'

    def handle_create(self):
        schema = self.get_schema('create')
        result = schema.load(self.args[self.create_data_name])
        assert not result.errors
        data = result.data
        if not isinstance(data, self.model):
            data = self.model(**data)

        data.full_clean()
        data.save()

        schema = self.get_schema('post-create', object=data)
        return schema.dump(data).data


class ModelHandlerUpdateMixin(BaseModelHandler):
    update_data_name = 'data'

    def handle_update(self):
        object = self.retrieve_object()
        schema = self.get_schema('update', object=object)
        result = schema.load(self.args[self.update_data_name])
        assert not result.errors
        for key, value in result.data.items():
            setattr(object, key, value)
        object.full_clean()
        object.save()
        schema = self.get_schema('post-update', object=object)
        return schema.dump(object).data


class ModelHandlerDeleteMixin(BaseModelHandler):
    def handle_delete(self):
        object = self.retrieve_object()
        object.delete()


class CRUDModelHandler(
    ModelHandlerCreateMixin,
    ModelHandlerReadMixin,
    ModelHandlerUpdateMixin,
    ModelHandlerDeleteMixin,
):
    pass
