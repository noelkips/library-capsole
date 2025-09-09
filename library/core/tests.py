
from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Book, Transaction
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class UserModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )

    def test_user_creation(self):
        self.assertEqual(self.user.username, 'testuser')
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertTrue(self.user.is_active)

    def test_user_soft_delete(self):
        self.user.delete()
        self.user.refresh_from_db()  # Refresh to get updated state
        self.assertFalse(self.user.is_active)

class BookModelTest(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
            title='The Hobbit',
            author='J.R.R. Tolkien',
            isbn='1234567890127',
            published_date='1937-09-21',
            copies_available=3
        )

    def test_book_creation(self):
        self.assertEqual(self.book.title, 'The Hobbit')
        self.assertEqual(self.book.author, 'J.R.R. Tolkien')
        self.assertEqual(self.book.copies_available, 3)

class TransactionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.book = Book.objects.create(
            title='The Hobbit',
            author='J.R.R. Tolkien',
            isbn='1234567890127',
            published_date='1937-09-21',
            copies_available=3
        )
        self.transaction = Transaction.objects.create(
            user=self.user,
            book=self.book,
            checkout_date=timezone.now(),
            due_date=timezone.now() + timedelta(days=14)
        )

    def test_transaction_creation(self):
        self.assertEqual(self.transaction.user.username, 'testuser')
        self.assertEqual(self.transaction.book.title, 'The Hobbit')
        self.assertIsNone(self.transaction.return_date)

    def test_overdue_transaction(self):
        overdue_transaction = Transaction.objects.create(
            user=self.user,
            book=self.book,
            checkout_date=timezone.now() - timedelta(days=20),
            due_date=timezone.now() - timedelta(days=5)
        )
        overdue = Transaction.objects.filter(
            return_date__isnull=True,
            due_date__lt=timezone.now()
        )
        self.assertIn(overdue_transaction, overdue)