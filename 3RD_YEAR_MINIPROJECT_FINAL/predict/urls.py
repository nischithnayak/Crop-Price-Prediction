from django.urls import path
from .views import predict_modal_price,home,coconut
from . import views

urlpatterns = [
    path('landing/', views.land, name='landing'),
    path('signup/', views.signup, name='signup'),
    path('login/', views.login, name='login'),
    path('onion/', views.onion, name='onion'),
    path('home/', home, name='home'),
    path('predict/', predict_modal_price, name='predict'),
    path('coconut/', coconut, name='coconut'),
    path('arecanut/', views.arecanut, name='arecanut'),
   
]
