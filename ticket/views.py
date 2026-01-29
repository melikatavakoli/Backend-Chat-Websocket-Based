from django.db.models import Q
from rest_framework import filters as drf_filters
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, viewsets, status
from rest_framework import generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from django.contrib.auth import get_user_model
from common.paginations import CustomLimitOffsetPagination
from ticket.models import (
    Ticket, 
    TicketDetail
    )
from ticket.serializers import (
    AdminCreateTicketSerializer, 
    TicketSerializer,
    WriteTicketSerializer, 
    TicketDetailSerializer,
    WriteTicketDetailSerializer, 
    UserTicketSerializer, 
    CreateTicketDetailSerializer,
    TicketReviewerListSerializer,
    AdminEditTicketSerializer, 
    )
from rest_framework.permissions import IsAuthenticated
User = get_user_model()
from rest_framework.views import APIView
from rest_framework.decorators import action
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# User Create Ticket view
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class UserCreateTicket(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserTicketSerializer

    def post(self, request):
        serializer = UserTicketSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            ser = serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_201_CREATED
            )
        else:
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# User Ticket List view
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class UserTicketList(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = UserTicketSerializer
    pagination_class = CustomLimitOffsetPagination
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter, ]
    search_fields = ["title"]
    ordering_fields=['created_at', 'number', 'title,', 'category', 'status']
    ordering = ["-created_at"]
    filterset_fields = ['category', 'status']

    def get_queryset(self):
        if getattr(self, "swagger_fake_view", False):
            return Ticket.objects.none()

        queryset = Ticket.objects.filter(user=self.request.user)
        q = self.request.GET.get('q')
        if q:
            queryset = queryset.filter(Q(title__icontains=q))
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        ordering = self.request.GET.get('ordering')
        if ordering == 'created_at':
            queryset = queryset.order_by('created_at')
        elif ordering == '-created_at':
            queryset = queryset.order_by('-created_at')
        return queryset

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Ticket Detail ViewSet
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class TicketDetailViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter,]
    search_fields = ["ticket__title",]
    ordering_fields = ["created_at"]
    filterset_fields = ["ticket__category",]

    def get_queryset(self):
        queryset = TicketDetail.objects.all()
        ticket = self.request.GET.get('ticket')
        if ticket:
            queryset = queryset.filter(ticket_id=ticket)
        return queryset

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TicketDetailSerializer
        return WriteTicketDetailSerializer

    def list(self, request, *args, **kwargs):
        ticket_id = request.GET.get('ticket')
        if not ticket_id:
            return Response({"error": "ticket id is required"}, status=400)
        details_qs = TicketDetail.objects.filter(ticket_id=ticket_id)
        if not details_qs.exists():
            return Response({"error": "ticket not found"}, status=404)

        ticket_obj = details_qs.first().ticket 

        details_data = TicketDetailSerializer(details_qs, many=True).data
        response_data = {
            "title_ticket": ticket_obj.title,
            "number_ticket": ticket_obj.number,
            "status_ticket": ticket_obj.status,
            "_created_by": str(ticket_obj._created_by) if ticket_obj._created_by else "",
            "reviewer_ticket": str(ticket_obj.reviewer.full_name) if ticket_obj.reviewer else "",
            "category_ticket": str(ticket_obj.category) if ticket_obj.category else "",
            "details": details_data
        }
        return Response(response_data)
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.can_delete():
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def perform_create(self, serializer):
        serializer.save(
            created_by=self.request.user,
            updated_by=self.request.user
        )

    def perform_update(self, serializer):
        serializer.save(
            updated_by=self.request.user
        )

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Create Ticket Detail view
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class CreateTicketDetail(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CreateTicketDetailSerializer

    def post(self, request):
        serializer = CreateTicketDetailSerializer(
        data=request.data,
        context={'request': request}
        )
        if serializer.is_valid():
            ser = serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Ticket view
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class TicketViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Ticket.objects.all()

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TicketSerializer
        return WriteTicketSerializer

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if instance.can_delete():
            self.perform_destroy(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def perform_update(self, serializer):
        instance = self.get_object()
        if instance.user == self.request.user:
            serializer.save(
                updated_by=self.request.user,
                reviewer=self.request.user
            )

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Admin-Ticket List ViewSet
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class AdminTicketListViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]
    pagination_class = CustomLimitOffsetPagination
    serializer_class = TicketSerializer
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter, ]
    search_fields = [
        "title", 
        "category",
        'number',
        'created_by__first_name',
        'created_by__last_name'
    ]
    ordering_fields=[
        'created_at',
        'number',
        'title',
        'category',
        'status',
        'created_by__first_name',
        'created_by__last_name',
    ]
    ordering = ['-created_at']
    filterset_fields = ["category", "status"]

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Admin Edit Ticket view
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class AdminEditTicket(APIView):
    permission_classes = [IsAuthenticated]
    serializer_class = AdminEditTicketSerializer

    def put(self, request, id):
        ticket_obj = Ticket.objects.filter(id=id).first()
        change_reviewer = request.data.get('change_reviewer')
        if change_reviewer:
            if request.user == ticket_obj.reviewer:
                pass
            else:
                ticket_obj.reviewer = request.user
                ticket_obj.save()
                return Response({'message': 'شما با موفقیت بازبین کننده این تیکت شدید.'}, status=status.HTTP_200_OK)
        if not ticket_obj.reviewer == request.user:
            return Response(
                {'message': 'شما به دلیل این که بازبین کننده این تیکت نیستید، نمی توانید تیکت را ویرایش کنید.'},
                status=status.HTTP_400_BAD_REQUEST)
        else:
            is_resolved = request.data.get('is_resolved')
            ticket_status = request.data.get('status')
            can_reply = request.data.get('can_reply')
            can_upload_attachment = request.data.get('can_upload_attachment')

            ticket_obj.is_resolved = is_resolved
            ticket_obj.can_reply = can_reply
            ticket_obj.can_upload_attachment = can_upload_attachment
            ticket_obj.status = ticket_status
            ticket_obj.save()

            return Response(
                {'message': 'تیکت با موفقیت ویرایش شد.'}, status=status.HTTP_200_OK)

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Admin Ticket Reviewer List
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class AdminTicketReviewerList(mixins.ListModelMixin, viewsets.GenericViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TicketReviewerListSerializer
    pagination_class = CustomLimitOffsetPagination
    filter_backends = [DjangoFilterBackend, drf_filters.SearchFilter, drf_filters.OrderingFilter, ]
    search_fields = ["title", "category","created_by"]
    ordering_fields=['created_at']

    def get_queryset(self):
        queryset = User.objects.filter(is_staff=True)
        return queryset

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return TicketReviewerListSerializer
        return None

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
# Admin Create Ticket APIView
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
class AdminCreateTicketAPIView(generics.CreateAPIView):
    queryset = Ticket.objects.all()
    serializer_class = AdminCreateTicketSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(reviewer=self.request.user)