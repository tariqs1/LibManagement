from django.test import TestCase
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from ..models import (
    User, Book, Author, Publisher, Location, 
    Borrowing, Review, Transaction, Staff,
    Genre, BookAuthor
)

class UserModelTest(TestCase):
    def setUp(self):
        self.user_data = {
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
            'user_type': 'USER',
            'username': 'testuser'
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_create_user(self):
        self.assertEqual(self.user.email, self.user_data['email'])
        self.assertEqual(self.user.first_name, self.user_data['first_name'])
        self.assertEqual(self.user.user_type, self.user_data['user_type'])
        self.assertTrue(self.user.check_password(self.user_data['password']))

    def test_create_superuser(self):
        admin_data = {
            'email': 'admin@example.com',
            'password': 'adminpass123',
            'first_name': 'Admin',
            'last_name': 'User',
            'username': 'adminuser'
        }
        admin = User.objects.create_superuser(**admin_data)
        self.assertTrue(admin.is_superuser)
        self.assertTrue(admin.is_staff)
        self.assertEqual(admin.user_type, 'ADMIN')

class BookModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            user_type='USER'
        )
        self.author_user = User.objects.create_user(
            username='testauthor',
            email='author@example.com',
            password='authorpass123',
            user_type='AUTHOR'
        )
        self.author = Author.objects.create(
            user=self.author_user,
            bio='Test bio',
            first_name='Test',
            last_name='Author'
        )
        self.location = Location.objects.create(
            city='Test City',
            state='Test State',
            postal_code='12345',
            country='Test Country'
        )
        self.publisher = Publisher.objects.create(
            name='Test Publisher',
            address='456 Test Ave',
            phone='1234567890',
            email='publisher@test.com',
            website='http://test.com',
            location=self.location
        )
        self.book = Book.objects.create(
            title='Test Book',
            isbn='1234567890',
            publication_date=timezone.now().date(),
            total_copies=5,
            available_copies=5,
            pages=200,
            description='Test description',
            publisher=self.publisher
        )
        BookAuthor.objects.create(book=self.book, author=self.author)

    def test_create_book(self):
        self.assertEqual(self.book.title, 'Test Book')
        self.assertEqual(self.book.available_copies, 5)
        self.assertEqual(self.book.total_copies, 5)

    def test_book_availability(self):
        self.assertTrue(self.book.is_available())
        self.book.available_copies = 0
        self.book.save()
        self.assertFalse(self.book.is_available())

class BorrowingModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            username='testuser'
        )
        self.location = Location.objects.create(
            city='Test City',
            state='Test State',
            postal_code='12345',
            country='Test Country'
        )
        self.publisher = Publisher.objects.create(
            name='Test Publisher',
            address='456 Test Ave',
            phone='1234567890',
            email='publisher@test.com',
            website='http://test.com',
            location=self.location
        )
        self.book = Book.objects.create(
            title='Test Book',
            isbn='1234567890',
            publication_date=timezone.now().date(),
            available_copies=1,
            total_copies=1,
            pages=200,
            description='Test description',
            publisher=self.publisher
        )
        self.borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.user,
            due_date=timezone.now().date() + timedelta(days=14)
        )

    def test_create_borrowing(self):
        self.assertEqual(self.borrowing.book, self.book)
        self.assertEqual(self.borrowing.user, self.user)
        self.assertFalse(self.borrowing.returned)

    def test_return_book(self):
        self.borrowing.returned = True
        self.borrowing.return_date = timezone.now().date()
        self.borrowing.save()
        self.assertTrue(self.borrowing.returned)
        self.assertEqual(self.borrowing.return_date, timezone.now().date())

    def test_overdue_borrowing(self):
        self.borrowing.due_date = timezone.now().date() - timedelta(days=1)
        self.borrowing.save()
        self.assertTrue(self.borrowing.is_overdue())

class ReviewModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            username='testuser'
        )
        self.location = Location.objects.create(
            city='Test City',
            state='Test State',
            postal_code='12345',
            country='Test Country'
        )
        self.publisher = Publisher.objects.create(
            name='Test Publisher',
            address='456 Test Ave',
            phone='1234567890',
            email='publisher@test.com',
            website='http://test.com',
            location=self.location
        )
        self.book = Book.objects.create(
            title='Test Book',
            isbn='1234567890',
            publication_date=timezone.now().date(),
            available_copies=1,
            total_copies=1,
            pages=200,
            description='Test description',
            publisher=self.publisher
        )
        self.review = Review.objects.create(
            book=self.book,
            user=self.user,
            rating=5,
            comment='Great book!'
        )

    def test_create_review(self):
        self.assertEqual(self.review.book, self.book)
        self.assertEqual(self.review.user, self.user)
        self.assertEqual(self.review.rating, 5)
        self.assertEqual(self.review.comment, 'Great book!')

    def test_invalid_rating(self):
        # Create a new user for this test
        new_user = User.objects.create_user(
            email='newuser@example.com',
            password='testpass123',
            first_name='New',
            last_name='User',
            username='newuser'
        )
        with self.assertRaises(ValidationError):
            Review.objects.create(
                book=self.book,
                user=new_user,
                rating=6,
                comment='Invalid rating'
            )

class TransactionModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            username='testuser'
        )
        self.staff_user = User.objects.create_user(
            email='staff@example.com',
            password='staffpass123',
            first_name='Staff',
            last_name='User',
            username='staffuser',
            user_type='STAFF'
        )
        self.staff = Staff.objects.create(
            user=self.staff_user,
            phone='1234567890',
            position='Librarian',
            status='ACTIVE'
        )
        self.location = Location.objects.create(
            city='Test City',
            state='Test State',
            postal_code='12345',
            country='Test Country'
        )
        self.publisher = Publisher.objects.create(
            name='Test Publisher',
            address='456 Test Ave',
            phone='1234567890',
            email='publisher@test.com',
            website='http://test.com',
            location=self.location
        )
        self.book = Book.objects.create(
            title='Test Book',
            isbn='1234567890',
            publication_date=timezone.now().date(),
            available_copies=1,
            total_copies=1,
            pages=200,
            description='Test description',
            publisher=self.publisher
        )
        self.transaction = Transaction.objects.create(
            user=self.user,
            book=self.book,
            transaction_type='BORROW',
            amount=0.00,
            payment_method='CASH'
        )

    def test_create_transaction(self):
        self.assertEqual(self.transaction.user, self.user)
        self.assertEqual(self.transaction.book, self.book)
        self.assertEqual(self.transaction.transaction_type, 'BORROW')
        self.assertEqual(self.transaction.payment_method, 'CASH') 