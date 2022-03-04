"""
Class-based implementation of the pet resource.
"""

from functools import reduce

from django.db.models import Q

from lepo.handlers import CRUDModelHandler
from lepo_tests.models import Pet
from lepo_tests.schemata import PetSchema


class PetHandler(CRUDModelHandler):
    model = Pet
    queryset = Pet.objects.all()
    schema_class = PetSchema
    create_data_name = 'pet'
    update_data_name = 'pet'

    def process_object_list(self, purpose, object_list):
        if purpose == 'list':
            tags = self.args.get('tags')
            if tags:
                tags_q = reduce(
                    lambda q, term: q | Q(tag=term),
                    tags,
                    Q()
                )
                object_list = object_list.filter(tags_q)
            limit = self.args.get('limit')
            if limit is not None:
                object_list = object_list[:limit]
        return super().process_object_list(purpose, object_list)


find_pets = PetHandler.get_view('handle_list')
add_pet = PetHandler.get_view('handle_create')
find_pet_by_id = PetHandler.get_view('handle_retrieve')
delete_pet = PetHandler.get_view('handle_delete')
update_pet = PetHandler.get_view('handle_update')
