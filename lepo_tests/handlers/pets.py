from functools import reduce

from django.db.models import Q
from marshmallow import Schema, fields, post_load

from lepo_tests.models import Pet


class PetSchema(Schema):
    id = fields.Integer(required=False)
    name = fields.Str(required=True)
    tag = fields.Str(required=False)

    @post_load
    def petify(self, data):
        return Pet(**data)


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
