from django.urls import path, include
from rest_framework.routers import DefaultRouter
from ticket import views

app_name = 'ticket'
router = DefaultRouter()

router.register('tickets', views.TicketViewSet, basename='ticket')
router.register('ticket-details', views.TicketDetailViewSet, basename='ticket_details')
router.register('admin-tickets', views.AdminTicketListViewSet, basename='admin-ticket')
router.register('admin-reviewer-list', views.AdminTicketReviewerList, basename='admin_reviewer_list')

urlpatterns = [
    path('', include(router.urls)),
    ######### TICKET ######### 
    path('user-create-ticket/', views.UserCreateTicket.as_view(), ),
    path('create-ticket-detail/', views.CreateTicketDetail.as_view(), ),
    path('admin/edit-ticket/<uuid:id>/', views.AdminEditTicket.as_view(), ),
    path('admin/add-ticket-detail/<uuid:id>/', views.AdminAddTicketDetailView.as_view(), ),
    path('admin-tickets-create/', views.AdminCreateTicketAPIView.as_view(), name='admin-create-ticket'),
]
