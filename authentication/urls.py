from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import RegisterView, AuthView

router = DefaultRouter()
router.register('', AuthView, basename='auth_view')
urlpatterns = [
    path('register/', RegisterView.as_view(), name='auth_register'),
]
urlpatterns += router.urls
