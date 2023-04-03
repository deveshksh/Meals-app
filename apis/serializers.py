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
            "quantity",
            "unit"
        )

class RecipeSerializer(serializers.ModelSerializer):
    ingredients = IngredientSerializer(many = True)
    user = UserSerializer(read_only = True )
    liked_by = UserSerializer(read_only = True, many = True)
    disliked_by = UserSerializer(read_only = True, many = True)
    class Meta:
        model = Recipe
        fields = (
            "id",
            "name",
            "steps",
            "user",
            "ingredients",
            "liked_by",
            "disliked_by"
        )
    def create(self, validated_data):
        ingredients_data = validated_data.pop('ingredients')
        recipe = Recipe.objects.create(**validated_data)

        for ingredient_data in ingredients_data:
            Ingredient.objects.create(recipe=recipe, **ingredient_data)

        return recipe
    
    def get_liked_by(self, obj):
        return obj.liked_by.values('id', 'username')

    def get_disliked_by(self, obj):
        return obj.disliked_by.values('id', 'username')
    