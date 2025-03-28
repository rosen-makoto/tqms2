from django.db import models

class Role(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name

class Location(models.Model):
    name = models.CharField(max_length=255, unique=True)
    registered_location = models.BooleanField(default=False)

    def __str__(self):
        return self.name
