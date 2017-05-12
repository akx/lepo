from functools import reduce

from django.db.models import Q
from marshmallow import Schema, fields, post_load

from lepo.handlers import CRUDModelHandler
from lepo_tests.models import Pet


class PetSchema(Schema):
    id = fields.Integer(required=False)
    name = fields.Str(required=True)
    tag = fields.Str(required=False)

    @post_load
    def petify(self, data):
        return Pet(**data)


class PetHandler(CRUDModelHandler):
    model = Pet
    queryset = Pet.objects.all()
    schema_class = PetSchema
    create_data_name = 'pet'

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
        return super(PetHandler, self).process_object_list(purpose, object_list)


find_pets = PetHandler.get_handler('handle_list')
add_pet = PetHandler.get_handler('handle_create')
find_pet_by_id = PetHandler.get_handler('handle_retrieve')
delete_pet = PetHandler.get_handler('handle_delete')

# Could instead do this:
"""
def find_pets(request, limit=None, tags=()):
    pets = Pet.objects.all()[:limit]
    if tags:
        tags_q = reduce(
            lambda q, term: q | Q(tag=term),
            tags,
            Q()
        )
        pets = pets.filter(tags_q)
    return PetSchema().dump(pets, many=True).data


def add_pet(request, pet):
    pet = PetSchema().load(pet).data
    pet.save()
    return PetSchema().dump(pet).data


def find_pet_by_id(request, id):
    return PetSchema().dump(Pet.objects.get(id=id)).data


def delete_pet(request, id):
    Pet.objects.filter(id=id).delete()
"""
