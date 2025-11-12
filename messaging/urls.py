from django.urls import path
from . import views

urlpatterns = [
    path('product/<int:product_id>/send/', views.message_to_seller, name='message_to_seller'),
    path('inbox/', views.inbox, name='inbox'),
]
