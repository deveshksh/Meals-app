from django.db import models
from django.contrib.auth.models import User 

class Profile(models.Model):
    name = models.CharField(max_length = 100)
    user = models.OneToOneField(
        User,
        on_delete = models.CASCADE
    )


class Recipe(models.Model):
    name = models.CharField(max_length = 30)
    steps = models.TextField()
    user = models.ForeignKey(
        User,
        related_name = "recipes",
        on_delete = models.DO_NOTHING
    )

    def __str__(self):
        return self.name

class Ingredient(models.Model):
    name = models.CharField(max_length=30)
    quantity = models.CharField(max_length = 10)
    recipe = models.ForeignKey(
        Recipe,
        related_name = "ingredients",
        on_delete = models.CASCADE
    )

    def __str__(self):
        return f"{self.name} {self.quantity}"

class Cart(models.Model):
    user = models.OneToOneField(
        User,
        on_delete = models.CASCADE
    )
    ingredients = models.ManyToManyField(
        Ingredient
    )
    