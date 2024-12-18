from django.contrib import admin
from django.urls import path, include
from api.views import login, loan_simulator, home
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView



# Os paths vão permitir irmos para uma pagina/chamar uma função/fazer alguma operação
urlpatterns = [
    path('login/', login, name='login'),
    path('loan_simulator/', loan_simulator, name="Simulacao"),
    path('Home/', home, name='Home')]