
from django.test import TestCase
from rest_framework.test import APITestCase
from core.models import User, Book, Transaction
from django.utils import timezone
from datetime import timedelta

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
        self.user.refresh_from_db()
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

class TransactionAPITest(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.admin = User.objects.create_superuser(
            username='admin',
            email='admin@example.com',
            password='adminpass123'
        )
        self.book = Book.objects.create(
            title='Test Book',
            author='Test Author',
            isbn='1234567890132',
            published_date='2020-01-01',
            copies_available=1
        )

    def test_checkout(self):
        self.client.force_authenticate(user=self.user)
        response = self.client.post('/api/transactions/checkout/', {'book_id': self.book.id}, format='json')
        print(response.data)  # Debug output
        self.assertEqual(response.status_code, 201, msg=f"Checkout failed: {response.data}")
        self.assertEqual(Book.objects.get(id=self.book.id).copies_available, 0)

    def test_return_book(self):
        # Use checkout endpoint to create transaction
        self.client.force_authenticate(user=self.user)
        checkout_response = self.client.post('/api/transactions/checkout/', {'book_id': self.book.id}, format='json')
        self.assertEqual(checkout_response.status_code, 201, msg=f"Checkout failed: {checkout_response.data}")
        transaction_id = checkout_response.data['id']
        # Return the book
        response = self.client.put(f'/api/transactions/{transaction_id}/return/', format='json')
        self.assertEqual(response.status_code, 200)
        self.assertIsNotNone(Transaction.objects.get(id=transaction_id).return_date)
        self.assertEqual(Book.objects.get(id=self.book.id).copies_available, 1)

    def test_overdue(self):
        overdue_transaction = Transaction.objects.create(
            user=self.user,
            book=self.book,
            checkout_date=timezone.now() - timedelta(days=20),
            due_date=timezone.now() - timedelta(days=5)
        )
        self.client.force_authenticate(user=self.admin)
        response = self.client.get('/api/transactions/overdue/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 1)