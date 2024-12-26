from django.contrib import admin
from django.urls import path, include
from api.views import login, loan_simulator, Home, BankLogin, loan_status, loan_status_funcionarios
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView


# Os paths vão permitir irmos para uma pagina/chamar uma função/fazer alguma operação
urlpatterns = [
    path('login/', login, name='login'),
    path('loan_simulator/', loan_simulator, name="Simulacao"),
    path('Home/', Home, name='Home'),
    path('BankLogin/', BankLogin, name='BankLogin'),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('loan_status/', loan_status, name='loan_status'),
    path('loan_status_funcionarios/', loan_status_funcionarios, name='loan_status_funcionarios'),
    ]