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
    assert not tags
    pets = Pet.objects.all()[:limit]
    return PetSchema().dump(pets, many=True).data


def add_pet(request, pet):
    pet = PetSchema().load(pet).data
    pet.save()
    return PetSchema().dump(pet).data


def find_pet_by_id(request, id):
    return PetSchema().dump(Pet.objects.get(id=id)).data


def delete_pet(request, id):
    Pet.objects.filter(id=id).delete()
