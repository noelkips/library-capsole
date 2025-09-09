
from rest_framework import serializers
from .models import User, Book, Transaction
from django.utils import timezone

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'date_of_membership', 'is_active']
        read_only_fields = ['date_of_membership']

    def validate_email(self, value):
        if User.objects.filter(email=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("Email already exists.")
        return value

class BookSerializer(serializers.ModelSerializer):
    class Meta:
        model = Book
        fields = ['id', 'title', 'author', 'isbn', 'published_date', 'copies_available']

    def validate_isbn(self, value):
        if Book.objects.filter(isbn=value).exclude(id=self.instance.id if self.instance else None).exists():
            raise serializers.ValidationError("ISBN already exists.")
        return value

    def validate_copies_available(self, value):
        if value < 0:
            raise serializers.ValidationError("Copies available cannot be negative.")
        return value

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'user', 'book', 'checkout_date', 'due_date', 'return_date']
        read_only_fields = ['checkout_date', 'due_date']

    def validate(self, data):
        book = data['book']
        user = data['user']
        if book.copies_available == 0:
            raise serializers.ValidationError("No copies available.")
        if Transaction.objects.filter(user=user, book=book, return_date__isnull=True).exists():
            raise serializers.ValidationError("User already has this book checked out.")
        return data
