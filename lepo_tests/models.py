from django.db import models


class Pet(models.Model):
    name = models.CharField(max_length=128)
    tag = models.CharField(max_length=128)
