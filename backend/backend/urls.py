from django.contrib import admin
from django.urls import path, include
from api.views import CreateUserView, simulacao, api_login,emprestimo
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView



# Os paths vão permitir irmos para uma pagina/chamar uma função/fazer alguma operação
urlpatterns = [
    path("emprestimo/",emprestimo.as_view(), name= "emprestimo"),
    path("",emprestimo.as_view(),name="default"),
    path('login/', api_login, name='login'),
    path('simulacao/', simulacao, name="Simulacao")]
