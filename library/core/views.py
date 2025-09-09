
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response
from .models import User, Book, Transaction
from .serializers import UserSerializer, BookSerializer, TransactionSerializer
from django.utils import timezone

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

class TransactionViewSet(viewsets.ModelViewSet):
    queryset = Transaction.objects.all()
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    @action(detail=False, methods=['post'], url_path='checkout')
    def checkout(self, request):
        book_id = request.data.get('book_id')
        try:
            book = Book.objects.get(id=book_id)
        except Book.DoesNotExist:
            return Response({"error": "Book not found"}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = self.get_serializer(data={
            'user': request.user.id,
            'book': book.id
        })
        serializer.is_valid(raise_exception=True)
        book.copies_available -= 1
        book.save()
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['put'], url_path='return')
    def return_book(self, request, pk=None):
        try:
            transaction = Transaction.objects.get(pk=pk, user=request.user, return_date__isnull=True)
        except Transaction.DoesNotExist:
            return Response({"error": "Transaction not found or already returned"}, status=status.HTTP_404_NOT_FOUND)
        
        transaction.return_date = timezone.now()
        transaction.book.copies_available += 1
        transaction.book.save()
        transaction.save()
        serializer = self.get_serializer(transaction)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='overdue', permission_classes=[IsAdminUser])
    def overdue(self, request):
        overdue = Transaction.objects.filter(return_date__isnull=True, due_date__lt=timezone.now())
        serializer = self.get_serializer(overdue, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
