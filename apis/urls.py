from django.urls import path
from .views import *

urlpatterns = [
    path("", RecipeList.as_view()),
    path("<int:id>/", RecipeDetail.as_view()),
    path("search/", SearchAPI.as_view()),
    path("<int:id>/like/", LikeRecipe.as_view()),
    path("<int:id>/dislike/", DislikeRecipe.as_view()),
    path("users/", UserListView.as_view()),
    path("users/<int:id>/", UserDetailView.as_view()),
    path("users/login/", UserLoginView.as_view())
]