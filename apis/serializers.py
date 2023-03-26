from rest_framework import serializers
from .models import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("id", "username")

class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = (
            "name",
            "quantity"
        )

class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many = True)
    user = UserSerializer(read_only = True)
    class Meta:
        model = Recipe
        fields = (
            "name",
            "steps",
            "user",
            "ingredients"

        )
    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)

        for ingredient_data in ingredients_data:
            Ingredient.objects.create(recipe=recipe, **ingredient_data)

        return recipe
    