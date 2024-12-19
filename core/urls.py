from django.urls import path,include
from .views import Registerapiview,Loginapiview,Userapiview
urlpatterns = [
    path('register',Registerapiview.as_view()),
    path('login',Loginapiview.as_view()),
    path('user',Userapiview.as_view()),

]
