"""
Bare view implementation of the pet resource.
"""

from functools import reduce

from django.db.models import Q

from lepo_tests.models import Pet
from lepo_tests.schemata import PetSchema


def find_pets(request, limit=None, tags=()):
    pets = Pet.objects.all()[:limit]
    if tags:
        tags_q = reduce(
            lambda q, term: q | Q(tag=term),
            tags,
            Q()
        )
        pets = pets.filter(tags_q)
    return PetSchema().dump(pets, many=True)


def add_pet(request, pet):
    pet_data = PetSchema().load(pet)
    pet = Pet(**pet_data)
    pet.save()
    return PetSchema().dump(pet)


def find_pet_by_id(request, id):
    return PetSchema().dump(Pet.objects.get(id=id))


def delete_pet(request, id):
    Pet.objects.filter(id=id).delete()


def update_pet(request, id, pet):
    old_pet = Pet.objects.get(id=id)
    for key, value in PetSchema().load(pet).items():
        setattr(old_pet, key, value)
    old_pet.save()
    return PetSchema().dump(old_pet)
