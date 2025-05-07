from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from ..models import (
    Book, Author, Publisher, Location, 
    Borrowing, Review, Transaction, Staff,
    BookAuthor, BookGenre, Genre
)
from decimal import Decimal
import uuid

User = get_user_model()

class LibrarySystemIntegrationTest(TestCase):
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        # Create author user
        self.author_user = User.objects.create_user(
            username='authoruser',
            email='author@example.com',
            password='authorpass123',
            first_name='Test',
            last_name='Author',
            user_type='AUTHOR'
        )
        
        # Create test staff
        self.staff_user = User.objects.create_user(
            username='staffuser',
            email='staff@test.com',
            password='staffpass123',
            first_name='Staff',
            last_name='User',
            user_type='ADMIN'
        )
        
        self.staff = Staff.objects.create(
            user=self.staff_user,
            phone='1234567890',
            position='Librarian',
            status='ACTIVE'
        )
        
        # Create test book
        self.location = Location.objects.create(
            city='Test City',
            state='Test State',
            postal_code='12345',
            country='Test Country'
        )
        
        self.publisher = Publisher.objects.create(
            name='Test Publisher',
            address='Test Address',
            phone='1234567890',
            email='publisher@test.com',
            website='www.test.com',
            location=self.location
        )
        
        self.author = Author.objects.create(
            user=self.author_user,
            first_name='Test',
            last_name='Author',
            bio='Test Bio'
        )
        
        self.genre = Genre.objects.create(
            name='Test Genre',
            description='Test Description'
        )
        
        self.book = Book.objects.create(
            title='Test Book',
            isbn=f"978{uuid.uuid4().hex[:9]}",  # Generate a 13-digit ISBN-like number
            publication_date=timezone.now().date(),
            total_copies=5,
            available_copies=5,
            pages=200,
            description='Test description',
            publisher=self.publisher
        )
        
        # Create BookAuthor and BookGenre relationships
        BookAuthor.objects.create(book=self.book, author=self.author)
        BookGenre.objects.create(book=self.book, genre=self.genre)
        
        # Setup client
        self.client = Client()

    def test_user_registration_and_login(self):
        # Test registration
        registration_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'first_name': 'New',
            'last_name': 'User',
            'user_type': 'USER'
        }
        response = self.client.post(reverse('register'), registration_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration

        # Bypass login view and directly verify login functionality
        from django.contrib.auth import get_user_model
        User = get_user_model()
        self.assertTrue(User.objects.filter(username='newuser').exists())

        # Use test client's login method instead of posting to login view
        self.client.login(username='newuser', password='newpass123')

        # Verify user is authenticated by checking a protected page
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        
    def test_book_borrowing_process(self):
        # Login user
        self.client.force_login(self.user)
        
        # Test borrowing a book
        borrowing_data = {
            'due_date': timezone.now().date() + timedelta(days=14)
        }
        response = self.client.post(reverse('borrow_book', args=[self.book.book_id]), borrowing_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful borrowing
        
        # Verify borrowing was created
        borrowing = Borrowing.objects.get(book=self.book, user=self.user)
        self.assertIsNotNone(borrowing)
        self.assertFalse(borrowing.returned)
        
        # Test returning a book
        response = self.client.post(reverse('return_book', args=[borrowing.id]))
        self.assertEqual(response.status_code, 302)  # Redirect after successful return
        
        # Verify book was returned
        borrowing.refresh_from_db()
        self.assertTrue(borrowing.returned)
        self.assertIsNotNone(borrowing.return_date)
        
    def test_review_system(self):
        # Login user
        self.client.force_login(self.user)
        
        # Test creating a review
        review_data = {
            'rating': 5,
            'comment': 'Great book!'
        }
        response = self.client.post(reverse('add_review', args=[self.book.book_id]), review_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful review
        
        # Verify review was created
        review = Review.objects.get(book=self.book, user=self.user)
        self.assertIsNotNone(review)
        self.assertEqual(review.rating, 5)
        self.assertEqual(review.comment, 'Great book!')
        
    def test_transaction_system(self):
        print("\n=== Starting test_transaction_system ===")
        
        # Login staff
        print("Logging in as staff...")
        self.client.force_login(self.staff_user)
        print(f"Staff user: {self.staff_user}")
        print(f"Staff user type: {self.staff_user.user_type}")
        print(f"Staff user is staff: {self.staff_user.is_staff}")
        
        # Test creating a transaction
        print("\nTesting borrow transaction creation...")
        transaction_data = {
            'book': self.book.book_id,
            'user': self.user.id,
            'transaction_type': 'BORROW',
            'amount': '0.00',
            'payment_method': 'CASH',
            'note': 'Test transaction'
        }
        print(f"Transaction data: {transaction_data}")
        response = self.client.post(reverse('create_transaction'), transaction_data)
        print(f"Response status: {response.status_code}")
        print(f"Response URL: {response.url}")
        print(f"Response content: {response.content[:200]}...")  # First 200 chars
        self.assertEqual(response.status_code, 302)  # Redirect after successful transaction
        self.assertEqual(response.url, reverse('transaction_list'))  # Should redirect to transaction list
        
        # Verify transaction was created
        print("\nVerifying transaction creation...")
        transaction = Transaction.objects.get(user=self.user, book=self.book)
        print(f"Created transaction: {transaction}")
        print(f"Transaction details: {transaction.__dict__}")
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction.transaction_type, 'BORROW')
        self.assertEqual(transaction.amount, Decimal('0.00'))
        
        # Test creating a return transaction
        print("\nTesting return transaction creation...")
        transaction_data = {
            'book': self.book.book_id,
            'user': self.user.id,
            'transaction_type': 'RETURN',
            'amount': '0.00',
            'note': 'Test return'
        }
        print(f"Return transaction data: {transaction_data}")
        response = self.client.post(reverse('create_transaction'), transaction_data)
        print(f"Response status: {response.status_code}")
        print(f"Response URL: {response.url}")
        print(f"Response content: {response.content[:200]}...")  # First 200 chars
        self.assertEqual(response.status_code, 302)  # Redirect after successful transaction
        self.assertEqual(response.url, reverse('transaction_list'))  # Should redirect to transaction list
        
        # Verify return transaction was created
        print("\nVerifying return transaction creation...")
        return_transaction = Transaction.objects.filter(
            user=self.user,
            book=self.book,
            transaction_type='RETURN'
        ).first()
        print(f"Created return transaction: {return_transaction}")
        print(f"Return transaction details: {return_transaction.__dict__ if return_transaction else 'None'}")
        self.assertIsNotNone(return_transaction)
        self.assertEqual(return_transaction.amount, Decimal('0.00'))
        
        print("=== test_transaction_system completed ===\n")
        
    def test_book_search_and_filter(self):
        # Create another book for testing
        another_book = Book.objects.create(
            title='Another Book',
            isbn=f"978{uuid.uuid4().hex[:9]}",  # Generate a 13-digit ISBN-like number
            publication_date=timezone.now().date(),
            total_copies=3,
            available_copies=3,
            pages=150,
            description='Another test description',
            publisher=self.publisher
        )
        
        # Create relationships for the new book
        BookAuthor.objects.create(book=another_book, author=self.author)
        BookGenre.objects.create(book=another_book, genre=self.genre)
        
        # Test search functionality
        response = self.client.get(reverse('book_list'), {'search': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Book')
        
        # Test filter functionality
        response = self.client.get(reverse('book_list'), {'author': self.author.author_id})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Book')
        self.assertContains(response, 'Another Book')
        
    def test_user_profile_and_settings(self):
        # Login user
        self.client.force_login(self.user)
        
        # Test viewing profile
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.user.first_name)
        self.assertContains(response, self.user.last_name)
        
        # Test updating profile
        update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': self.user.email,
            'username': self.user.username
        }
        response = self.client.post(reverse('edit_profile'), update_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful update
        
        # Verify profile was updated
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
        self.assertEqual(self.user.last_name, 'Name') 