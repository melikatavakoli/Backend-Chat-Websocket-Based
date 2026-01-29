from django.urls import path, include
from rest_framework.routers import DefaultRouter
from chat import views

app_name = 'ticket'
router = DefaultRouter()

message_list = views.MessageViewSet.as_view({
    'get': 'list',
    'post': 'create'
})
 
router.register(r'profiles', views.ProfileViewSet, basename='profile')
router.register(r'chats', views.ChatViewSet, basename='chat')
router.register(r'messages', views.MessageViewSet, basename='message')

urlpatterns = [
    path('', include(router.urls)),
    path('create-chat-messages/<uuid:chat_id>/', views.MessageCreateView.as_view(), name='chat-messages-create'),
    path('chats-messages/<uuid:chat_id>/', message_list, name='chat-messages'),

]
