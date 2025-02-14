from django.urls import path
from . import views

urlpatterns = [
    path('api/get_nft_probabilities/', views.get_nft_probabilities, name='get_nft_probabilities'),
]
