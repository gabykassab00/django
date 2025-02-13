from django.urls import path,include
from .views import Registerapiview,Loginapiview,Userapiview,Refreshapiview,Logoutapiview,Forgotapiview,Resetapiview,Googleauthapiview,Fileuploadview,GetStatsView,AIVIEW,AddDataToTeam,FetchTeamData
urlpatterns = [
    path('register',Registerapiview.as_view()),
    path('login',Loginapiview.as_view()),
    path('google',Googleauthapiview.as_view()),    
    path('user',Userapiview.as_view()),
    path('refresh',Refreshapiview.as_view()),
    path('logout',Logoutapiview.as_view()),
    path('forgot',Forgotapiview.as_view()),
    path('reset',Resetapiview.as_view()),
    path('upload',Fileuploadview.as_view()),
    path('stats', GetStatsView.as_view()),
    path('ai',AIVIEW.as_view()),
    path('team',AddDataToTeam.as_view()),
    path('save',FetchTeamData.as_view()),
]

