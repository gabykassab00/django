from django.urls import path,include
from .views import Registerapiview
urlpatterns = [
    path('register',Registerapiview.as_view())
]
