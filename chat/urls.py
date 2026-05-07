# urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ChatViewSet, MessageViewSet

router = DefaultRouter()
app_name = "chat"

router.register('chats', ChatViewSet, basename='chat')
router.register('messages', MessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)),
]