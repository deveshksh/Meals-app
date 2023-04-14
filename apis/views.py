from rest_framework.views import APIView
from .models import *
from .serializers import *
from rest_framework.response import Response
from django.http import Http404
from rest_framework import status
from rest_framework import permissions
from django.db.models import Q
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.authentication import TokenAuthentication
from googleapiclient.discovery import build
import json
from django.http import JsonResponse
from .models import Recipe
from .serializers import RecipeSerializer
from googletrans import Translator
from django.http import HttpResponse

class SearchAPI(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        search_query = request.query_params.get('q', '')
        results = Recipe.objects.filter(Q(name__icontains = search_query))
        serializer = RecipeSerializer(results, many = True)
        return Response(serializer.data)

class RecipeList(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request):
        queryset = Recipe.objects.all()
        serializer = RecipeSerializer(queryset, many = True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = RecipeSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save(user = request.user)
            return Response(serializer.data)
        return Response(status = status.HTTP_400_BAD_REQUEST)

class RecipeDetail(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get_object(self, id):
        try:
            return Recipe.objects.get(id = id)
        except Recipe.DoesNotExist:
            raise Http404
        
    def get(self, request, id):
        queryset = self.get_object(id)
        serializer = RecipeSerializer(queryset)
        translator = Translator()

        description = serializer.data['name']
        translated = translator.translate(description,src = 'en', dest='hi')
        translated_text = translated.text

        updated_data = dict(serializer.data)
        updated_data['name'] = translated_text
        # Create a new instance of the serializer with the updated data
        updated_serializer = RecipeSerializer(instance=queryset, data=updated_data)
        updated_data_json = json.dumps(updated_data)

        return Response(updated_data_json)
    
    def put(self, request, id):
        queryset = self.get_object(id)
        if request.user == queryset.user:
            serializer = RecipeSerializer(queryset, data = request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(status = status.HTTP_400_BAD_REQUEST)
        return Response(status = status.HTTP_401_UNAUTHORIZED)
    
    def delete(self, request, id):
        queryset = self.get_object(id)
        if request.user == queryset.user:
            queryset.delete()
            return Response(status = status.HTTP_204_NO_CONTENT)
        return Response(status = status.HTTP_401_UNAUTHORIZED)
    
    
def RecipeTranslate(request, id):
    recipe = Recipe.objects.get(id=id)
    serializer = RecipeSerializer(recipe)
    data = serializer.data

    # Extract the recipe name and ingredients
    recipe_name = data['name']
    recipe_ingredients = data['ingredients']

    # Create a translator object
    translator = Translator()

    # Translate the recipe name and ingredients to Hindi
    hindi_recipe_name = translator.translate(recipe_name, dest='hi').text
    hindi_recipe_ingredients = []
    for ingredient in recipe_ingredients:
        hindi_recipe_ingredients.append(translator.translate(ingredient, dest='hi').text)

    # Replace the English recipe name and ingredients with their Hindi translations
    data['name'] = hindi_recipe_name
    data['ingredients'] = hindi_recipe_ingredients

    return Response(data)


class LikeRecipe(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, id):
        try:
            return Recipe.objects.get(id = id)
        except Recipe.DoesNotExist:
            raise Http404

    def put(self, request, id):
        recipe = self.get_object(id)
        users_who_disliked_post = recipe.disliked_by.all()
        users_who_liked_post = recipe.liked_by.all()

        if request.user in users_who_disliked_post:
            recipe.disliked_by.remove(request.user)
            recipe.liked_by.add(request.user)
            serializer = RecipeSerializer(recipe)
            return Response(serializer.data) #sending the data to test the api, send only status code in final implementation

        elif request.user in users_who_liked_post:
            recipe.liked_by.remove(request.user)
            serializer = RecipeSerializer(recipe)
            return Response(serializer.data) #sending the data to test the api, send only status code in final implementation
        
        recipe.liked_by.add(request.user)
        serializer = RecipeSerializer(recipe)
        return Response(serializer.data) #sending the data to test the api, send only status code in final implementation

class DislikeRecipe(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self, id):
        try:
            return Recipe.objects.get(id = id)
        except Recipe.DoesNotExist:
            raise Http404

    def put(self, request, id):
        recipe = self.get_object(id)
        users_who_disliked_post = recipe.disliked_by.all()
        users_who_liked_post = recipe.liked_by.all()

        if request.user in users_who_liked_post:
            recipe.liked_by.remove(request.user)
            recipe.disliked_by.add(request.user)
            serializer = RecipeSerializer(recipe)
            return Response(serializer.data) #sending the data to test the api, send only status code in final implementation

        elif request.user in users_who_disliked_post:
            recipe.disliked_by.remove(request.user)
            serializer = RecipeSerializer(recipe)
            return Response(serializer.data) #sending the data to test the api, send only status code in final implementation
        
        recipe.disliked_by.add(request.user)
        serializer = RecipeSerializer(recipe)
        return Response(serializer.data) #sending the data to test the api, send only status code in final implementation


class UserListView(APIView):
    
    def get(request, format = None):
        queryset = User.objects.all()
        serializer = ProfileSerializer(queryset, many = True)
        return Response(serializer.data)
    
    def post(self, request, format = None):
        serializer = ProfileSerializer(data = request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(status = status.HTTP_400_BAD_REQUEST)

class UserDetailView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    def get(self, request, id, format = None, *args, **kwargs):
        queryset = User.objects.get(id = id)
        serializer = ProfileSerializer(queryset)
        return Response(serializer.data)
    
class UserLoginView(APIView):
    @csrf_exempt
    def post(self, request, format = None):
        username = request.data.get("username")
        password = request.data.get("password")
        user = authenticate(request, username = username, password = password)
        
        if user is not None:
            token, created = Token.objects.get_or_create(user = user)
            return Response({"token": token.key})
        return Response(status = status.HTTP_400_BAD_REQUEST)

class YoutubeSearch(APIView):
    def get(self, request, recipe_id):
        # Get the recipe object from the database
        recipe = Recipe.objects.get(id=recipe_id)

        # Use the YouTube Data API to search for videos with the recipe title
        api_key = 'AIzaSyBI2-BjByIIfn_VDHm337dXScXxBdTwhz0'
        youtube = build('youtube', 'v3', developerKey=api_key)
        search_response = youtube.search().list(
            q=recipe.name + "recipe",
            type='video',
            part='id,snippet',
            maxResults=20
        ).execute()

        # Parse the API response and return the search results
        videos = []
        for search_result in search_response.get('items', []):
            video_id = search_result['id']['videoId']
            video_title = search_result['snippet']['title']
            video_thumbnail = search_result['snippet']['thumbnails']['medium']['url']
            video = {
                'id': video_id,
                'title': video_title,
                'thumbnail': video_thumbnail
            }
            videos.append(video)

        return Response(videos)
