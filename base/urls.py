from django.urls import path
from .views import recommend_music

urlpatterns = [
    path('recommend/', recommend_music, name='recommend_music'),
]
