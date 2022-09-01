from django.urls import path
from rest_framework.routers import DefaultRouter

from .views import ChatThreadViewSet,ChatViewSet

router = DefaultRouter()
router.register('', ChatThreadViewSet, basename='chat_thread_view')
router.register('chat-messages',ChatViewSet,basename="chat")
urlpatterns = [
]
urlpatterns += router.urls
