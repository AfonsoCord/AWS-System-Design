from django.contrib import admin
from django.urls import path, include
from api.views import CreateUserView, api_login,emprestimo, loan_simulator
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView



# Os paths vão permitir irmos para uma pagina/chamar uma função/fazer alguma operação
urlpatterns = [
    path("emprestimo/",emprestimo.as_view(), name= "emprestimo"),
    path("",emprestimo.as_view(),name="default"),
    path('api_login/', api_login, name='api_login'),
    path('loan_simulator/', loan_simulator, name="Simulacao")]
