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
            isbn='1234567890',
            publication_date=timezone.now().date(),
            pages=200,
            available_copies=5,
            total_copies=5,
            description='Test Description',
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
            title='Test Book 1',
            isbn='1234567890',
            publication_date='2023-01-01',
            pages=200,
            available_copies=5,
            total_copies=5,
            description='Test description'
        )
        book2 = Book.objects.create(
            title='Test Book 2',
            isbn='0987654321',
            publication_date='2023-02-01',
            pages=300,
            available_copies=3,
            total_copies=3,
            description='Another test description'
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
        self.client.login(username='testuser', password='testpass123')
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
        # Create a fresh client for this test
        client = Client(enforce_csrf_checks=True)
        
        # Test initial GET request
        response = client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

        # Get the CSRF token from the response
        csrf_token = client.cookies['csrftoken'].value

        # Test login with the user created in setUp
        login_data = {
            'username': 'testuser',  # Using the username from setUp
            'password': 'testpass123',  # Using the password from setUp
            'csrfmiddlewaretoken': csrf_token
        }
        response = client.post(reverse('login'), login_data)
        self.assertEqual(response.status_code, 302)  # Check for redirect
        self.assertEqual(response.url, '/home/')  # Check redirect URL

        # Test invalid login
        login_data['password'] = 'wrongpass'
        response = client.post(reverse('login'), login_data)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login.html')

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
        self.assertFalse(Borrowing.objects.filter(book=self.book, user=self.user, returned=False).exists())

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
        # Login required
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Regular user login
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 403)  # Forbidden

        # Admin login
        self.client.login(username='adminuser', password='adminpass123')
        response = self.client.get(reverse('admin_dashboard'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'admin_dashboard.html')
        self.assertContains(response, 'Dashboard')

    def test_generate_report_view(self):
        # Login required
        response = self.client.get(reverse('generate_report'))
        self.assertEqual(response.status_code, 302)  # Redirect to login

        # Regular user login
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('generate_report'))
        self.assertEqual(response.status_code, 403)  # Forbidden

        # Admin login
        self.client.login(username='adminuser', password='adminpass123')
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
        self.assertTemplateUsed(response, 'transaction_list.html')

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
        # Create a book
        book = Book.objects.create(
            title='Test Book',
            isbn='1234567890',
            publication_date='2023-01-01',
            pages=200,
            available_copies=5,
            total_copies=5,
            description='Test description'
        )

        # Create a member
        member = User.objects.create_user(
            username='member',
            email='member@test.com',
            password='testpass123'
        )

        # Test without login (should redirect to login)
        response = self.client.get(reverse('create_transaction'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

        # Test with staff login
        self.client.login(username='staffuser', password='staffpass123')
        
        # Test GET request
        response = self.client.get(reverse('create_transaction'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'create_transaction.html')

        # Test POST request for borrow transaction
        response = self.client.post(reverse('create_transaction'), {
            'book': book.book_id,
            'user': member.id,
            'transaction_type': 'BORROW',
            'amount': '0.00',
            'note': 'Test borrow'
        })
        self.assertEqual(response.status_code, 302)  # Redirect on success
        self.assertTrue(Transaction.objects.filter(book=book, user=member, transaction_type='BORROW').exists())
        book.refresh_from_db()
        self.assertEqual(book.available_copies, 4)  # Book quantity should decrease by 1

    def test_transaction_list_view(self):
        """Test transaction list view"""
        # Create a book
        book = Book.objects.create(
            title='Test Book',
            isbn='1234567890',
            publication_date='2023-01-01',
            pages=200,
            available_copies=5,
            total_copies=5,
            description='Test description'
        )

        # Create a member
        member = User.objects.create_user(
            username='member',
            email='member@test.com',
            password='testpass123'
        )

        # Create a test transaction
        transaction = Transaction.objects.create(
            book=book,
            user=member,
            transaction_type='BORROW',
            amount=0.00,
            note='Test borrow'
        )

        # Test without login (should redirect to login)
        response = self.client.get(reverse('transaction_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)

        # Test with staff login
        self.client.login(username=self.staff_user.username, password='staffpass123')
        response = self.client.get(reverse('transaction_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'transaction_list.html')
        self.assertContains(response, book.title)
        self.assertContains(response, member.username)

        # Test with member login (should only see their own transactions)
        self.client.login(username='member', password='testpass123')
        response = self.client.get(reverse('transaction_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'transaction_list.html')
        self.assertContains(response, book.title)
        self.assertContains(response, member.username) 