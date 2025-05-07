from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from ..models import (
    Book, Author, Publisher, Location, 
    Borrowing, Review, Transaction, Staff,
    Genre, BookGenre, BookAuthor, User
)
from decimal import Decimal
import uuid

User = get_user_model()

class ViewTests(TestCase):
    def setUp(self):
        # Create test location
        self.location = Location.objects.create(
            city='Test City',
            state='Test State',
            postal_code='12345',
            country='Test Country'
        )

        # Create staff user
        self.staff_user = User.objects.create_user(
            username='staffuser_' + str(timezone.now().timestamp()),
            email='staff@test.com',
            password='staffpass123',
            is_staff=True,
            user_type='ADMIN'
        )

        # Create test publisher
        self.publisher = Publisher.objects.create(
            name='Test Publisher',
            address='Test Address',
            phone='1234567890',
            email='publisher@test.com',
            website='www.test.com',
            location=self.location
        )

        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            user_type='USER'
        )

        # Create test author
        self.author = Author.objects.create(
            user=self.user,
            bio='Test Bio',
            first_name='Test',
            last_name='Author'
        )

        # Create test genre
        self.genre = Genre.objects.create(
            name='Test Genre',
            description='Test Description'
        )

        # Create test book
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

        # Staff user is already created earlier in the setUp method

        # Create test admin
        self.admin_user = User.objects.create_user(
            username='adminuser',
            email='admin@example.com',
            password='adminpass123',
            first_name='Admin',
            last_name='User',
            user_type='ADMIN'
        )

        # Setup client
        self.client = Client()

    def test_home_view(self):
        response = self.client.get(reverse('home'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')
        self.assertContains(response, self.book.title)

    def test_book_list_view(self):
        """Test book list view"""
        # Create test books
        book1 = Book.objects.create(
            title='Book 1',
            isbn=f"978{uuid.uuid4().hex[:9]}",  # Generate a 13-digit ISBN-like number
            publication_date=timezone.now().date(),
            total_copies=3,
            available_copies=3,
            pages=150,
            description='Description 1',
            publisher=self.publisher
        )
        book2 = Book.objects.create(
            title='Book 2',
            isbn=f"978{uuid.uuid4().hex[:9]}",  # Generate a 13-digit ISBN-like number
            publication_date=timezone.now().date(),
            total_copies=2,
            available_copies=2,
            pages=250,
            description='Description 2',
            publisher=self.publisher
        )

        # Test public access
        response = self.client.get(reverse('book_list'))
        self.assertEqual(response.status_code, 200)  # Public access allowed
        self.assertTemplateUsed(response, 'book_list.html')
        self.assertContains(response, book1.title)
        self.assertContains(response, book2.title)

        # Test search functionality
        response = self.client.get(reverse('book_list'), {'search': 'Test Book 1'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, book1.title)
        self.assertNotContains(response, book2.title)

        # Test access with member login
        logged_in = self.client.login(email='test@example.com', password='testpass123')
        self.assertTrue(logged_in)
        response = self.client.get(reverse('book_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_list.html')
        self.assertContains(response, book1.title)
        self.assertContains(response, book2.title)

    def test_book_detail_view(self):
        response = self.client.get(reverse('book_detail', args=[self.book.book_id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'book_detail.html')
        self.assertContains(response, self.book.title)
        self.assertContains(response, self.book.description)

        # Test adding review
        self.client.force_login(self.user)
        review_data = {
            'rating': 5,
            'comment': 'Great book!'
        }
        response = self.client.post(reverse('book_detail', args=[self.book.book_id]), review_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful review
        self.assertTrue(Review.objects.filter(book=self.book, user=self.user).exists())

    def test_register_view(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'register.html')

        # Test registration
        registration_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'first_name': 'New',
            'last_name': 'User',
            'user_type': 'USER'
        }
        response = self.client.post(reverse('register'), registration_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful registration
        self.assertTrue(User.objects.filter(email='new@example.com').exists())

        # Test author registration
        registration_data = {
            'username': 'newauthor',
            'email': 'author@example.com',
            'password1': 'newpass123',
            'password2': 'newpass123',
            'first_name': 'New',
            'last_name': 'Author',
            'user_type': 'AUTHOR',
            'bio': 'Test Bio'
        }
        response = self.client.post(reverse('register'), registration_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(email='author@example.com').exists())
        self.assertTrue(Author.objects.filter(user__email='author@example.com').exists())

    def test_login_view(self):
        print("\n=== Starting test_login_view ===")
        
        # Test GET request
        print("Testing GET request...")
        response = self.client.get(reverse('login'))
        print(f"GET response status: {response.status_code}")
        print(f"GET response content: {response.content[:200]}...")  # First 200 chars
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

        # Test successful login
        print("\nTesting successful login...")
        login_data = {
            'email': 'test@example.com',
            'password': 'testpass123'
        }
        print(f"Login data: {login_data}")
        response = self.client.post(reverse('login'), login_data)
        print(f"Login response status: {response.status_code}")
        print(f"Login response URL: {response.url}")
        print(f"Login response content: {response.content[:200]}...")  # First 200 chars
        self.assertEqual(response.status_code, 302)  # Check for redirect
        self.assertIn(response.url, ['/', '/home/'])  # Accept both as valid

        # Test invalid login
        print("\nTesting invalid login...")
        login_data['password'] = 'wrongpass'
        print(f"Invalid login data: {login_data}")
        response = self.client.post(reverse('login'), login_data)
        print(f"Invalid login response status: {response.status_code}")
        print(f"Invalid login response content: {response.content[:200]}...")  # First 200 chars
        self.assertEqual(response.status_code, 200)  # Should stay on login page
        self.assertTemplateUsed(response, 'login.html')
        self.assertContains(response, 'Invalid email or password')
        
        print("=== test_login_view completed ===\n")

    def test_profile_view(self):
        # Login required
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Login and test
        self.client.force_login(self.user)
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profile.html')
        self.assertContains(response, self.user.first_name)

        # Test editing profile
        profile_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'email': self.user.email,
            'username': self.user.username
        }
        response = self.client.post(reverse('edit_profile'), profile_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful update
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')

    def test_borrow_book_view(self):
        # Login required
        response = self.client.post(reverse('borrow_book', args=[self.book.book_id]))
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Login and test
        self.client.force_login(self.user)
        response = self.client.post(reverse('borrow_book', args=[self.book.book_id]))
        self.assertEqual(response.status_code, 302)  # Redirect after successful borrowing
        self.assertTrue(Borrowing.objects.filter(book=self.book, user=self.user).exists())
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 4)

        # Test borrowing unavailable book
        self.book.available_copies = 0
        self.book.save()
        response = self.client.post(reverse('borrow_book', args=[self.book.book_id]))
        self.assertEqual(response.status_code, 302)

    def test_return_book_view(self):
        # Create borrowing
        borrowing = Borrowing.objects.create(
            book=self.book,
            user=self.user,
            due_date=timezone.now().date() + timedelta(days=14)
        )

        # Login required
        response = self.client.post(reverse('return_book', args=[borrowing.id]))
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Login and test
        self.client.force_login(self.user)
        response = self.client.post(reverse('return_book', args=[borrowing.id]))
        self.assertEqual(response.status_code, 302)  # Redirect after successful return
        borrowing.refresh_from_db()
        self.assertTrue(borrowing.returned)
        self.assertIsNotNone(borrowing.return_date)
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 6)  # 5 + 1 returned

    def test_add_review_view(self):
        # Login required
        response = self.client.post(reverse('add_review', args=[self.book.book_id]))
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Login and test
        self.client.force_login(self.user)
        review_data = {
            'rating': 5,
            'comment': 'Great book!'
        }
        response = self.client.post(reverse('add_review', args=[self.book.book_id]), review_data)
        self.assertEqual(response.status_code, 302)  # Redirect after successful review
        self.assertTrue(Review.objects.filter(book=self.book, user=self.user).exists())

        # Test invalid review
        review_data['rating'] = 6  # Invalid rating
        response = self.client.post(reverse('add_review', args=[self.book.book_id]), review_data)
        self.assertEqual(response.status_code, 200)  # Stay on the same page
        self.assertFalse(Review.objects.filter(book=self.book, user=self.user, rating=6).exists())

    def test_admin_dashboard_view(self):
        # Login required (unauthenticated)
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login
        print('Status code:', response.status_code)
        print('Redirect location:', response.get('Location'))

        # Regular user login
        logged_in = self.client.login(email='test@example.com', password='testpass123')
        self.assertTrue(logged_in)
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 403)  # Forbidden

        # Admin login
        logged_in = self.client.login(email='admin@example.com', password='adminpass123')
        self.assertTrue(logged_in)
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/dashboard.html')
        self.assertContains(response, 'Dashboard')

    def test_generate_report_view(self):
        # Login required
        response = self.client.get(reverse('generate_report'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Regular user login
        self.client.login(email='test@example.com', password='testpass123')
        response = self.client.get(reverse('generate_report'))
        self.assertEqual(response.status_code, 403)  # Forbidden

        # Admin login
        self.client.login(email='admin@example.com', password='adminpass123')
        response = self.client.get(reverse('generate_report'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'generate_report.html')

        # Test report generation
        report_data = {
            'type': 'borrowings',
            'start_date': (timezone.now().date() - timedelta(days=30)).strftime('%Y-%m-%d'),
            'end_date': timezone.now().date().strftime('%Y-%m-%d')
        }
        response = self.client.get(reverse('generate_report'), report_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'report.html')

    def test_search_view(self):
        response = self.client.get(reverse('search'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'search.html')

        # Test search functionality
        search_data = {
            'query': 'Test',
            'search_type': 'books'
        }
        response = self.client.get(reverse('search'), search_data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.book.title)

    def test_author_list_view(self):
        response = self.client.get(reverse('author_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'author_list.html')
        self.assertContains(response, self.author.first_name)

    def test_author_detail_view(self):
        response = self.client.get(reverse('author_detail', args=[self.author.author_id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'author_detail.html')
        self.assertContains(response, self.author.first_name)
        self.assertContains(response, self.book.title)

    def test_transaction_list_view(self):
        # Login required
        response = self.client.get(reverse('transaction_list'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Regular user login
        self.client.force_login(self.user)
        response = self.client.get(reverse('transaction_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/transaction_list.html')

        # Create test transaction
        transaction = Transaction.objects.create(
            user=self.user,
            book=self.book,
            transaction_type='BORROW',
            amount=0.00,
            payment_method='CASH'
        )
        response = self.client.get(reverse('transaction_list'))
        self.assertContains(response, self.book.title)

    def test_create_transaction(self):
        """Test transaction creation view"""
        print("\n=== Starting test_create_transaction ===")
        
        # Login as admin
        print("Attempting to login as admin...")
        logged_in = self.client.login(email='admin@example.com', password='adminpass123')
        print(f"Login successful: {logged_in}")
        self.assertTrue(logged_in)
        
        # Test GET request
        print("Testing GET request...")
        response = self.client.get(reverse('create_transaction'))
        print(f"GET response status: {response.status_code}")
        print(f"GET response content: {response.content[:200]}...")  # First 200 chars
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin/create_transaction.html')
        
        # Test POST request for borrow transaction
        print("\nTesting POST request...")
        post_data = {
            'book': self.book.book_id,
            'user': self.user.id,
            'transaction_type': 'BORROW',
            'amount': '0.00',
            'payment_method': 'CASH',
            'note': 'Test borrow'
        }
        print(f"POST data: {post_data}")
        response = self.client.post(reverse('create_transaction'), post_data)
        print(f"POST response status: {response.status_code}")
        print(f"POST response content: {response.content[:200]}...")  # First 200 chars
        
        # Check transaction creation
        print("\nChecking transaction creation...")
        print(f"Query details: book_id={self.book.book_id}, user_id={self.user.id}")
        transaction = Transaction.objects.filter(
            book=self.book, 
            user=self.user, 
            transaction_type='BORROW'
        ).first()
        print(f"Transaction found: {transaction}")
        
        # Verify transaction details
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction.user.id, self.user.id)
        self.assertEqual(transaction.book.book_id, self.book.book_id)
        self.assertEqual(transaction.transaction_type, 'BORROW')
        self.assertEqual(float(transaction.amount), 0.00)
        self.assertEqual(transaction.payment_method, 'CASH')
        self.assertEqual(transaction.note, 'Test borrow')
        
        # Verify book copies were updated
        self.book.refresh_from_db()
        self.assertEqual(self.book.available_copies, 4)  # Original 5 - 1
        
        print("=== test_create_transaction completed ===\n") 