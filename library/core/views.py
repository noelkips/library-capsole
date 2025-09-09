from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from .models import User, Book
from .serializers import UserSerializer, BookSerializer

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_permissions(self):
        if self.action in ['create']:
            return []  # Allow registration without auth
        if self.action in ['update', 'partial_update', 'destroy']:
            return [IsAdminUser()]  # Only admins can update/delete
        return [IsAuthenticated()]  # View requires login

    def perform_destroy(self, instance):
        instance.is_active = False  # Soft delete
        instance.save()

class BookViewSet(viewsets.ModelViewSet):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return []  # Public read access

    def get_queryset(self):
        queryset = Book.objects.all()
        available = self.request.query_params.get('available')
        title = self.request.query_params.get('title')
        author = self.request.query_params.get('author')
        isbn = self.request.query_params.get('isbn')
        if available == 'true':
            queryset = queryset.filter(copies_available__gt=0)
        if title:
            queryset = queryset.filter(title__icontains=title)
        if author:
            queryset = queryset.filter(author__icontains=author)
        if isbn:
            queryset = queryset.filter(isbn=isbn)
        return queryset