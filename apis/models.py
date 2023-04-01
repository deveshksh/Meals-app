from django.db import models
from django.dispatch import receiver
from django.contrib.auth.models import User 
from django.db.models.signals import post_save

class Preference(models.Model):
    name = models.CharField(max_length=50)

class Profile(models.Model):
    name = models.CharField(max_length = 100)
    preferences = models.ManyToManyField(
        Preference,
        blank = True
    )
    user = models.OneToOneField(
        User,
        related_name = "profile",
        on_delete = models.CASCADE
    )

    def __str__(self):
        return self.name

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
    quantity = models.IntegerField()
    unit = models.CharField(max_length = 10)
    recipe = models.ForeignKey(
        Recipe,
        related_name = "ingredients",
        on_delete = models.CASCADE,
        blank = True
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


@receiver(post_save, sender = User)
def create_profile(sender, instance, created, **kwargs): #sender is redundant. it's not being used in this case. used in multi models
    if created:
        user_profile = Profile(user = instance, name = instance.username)
        user_profile.save()

@receiver(post_save, sender = User)
def save_profile(sender, instance, **kwargs):
    instance.profile.save()

