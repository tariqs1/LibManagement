from django.test import TestCase
from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import timedelta
from ..forms import (
    UserRegistrationForm,
    ReviewForm,
    BookForm,
    BookEditForm,
    UserProfileForm,
    BookExtensionForm,
    BookReservationForm,
    AuthorForm,
    PublisherForm,
    GenreForm,
    TransactionForm,
    BorrowingForm
)
from ..models import User, Author, Publisher, Location, Book, Genre, Transaction, BookAuthor, BookGenre

class FormTests(TestCase):
    def setUp(self):
        # Create test location
        self.location = Location.objects.create(
            city='Test City',
            state='Test State',
            postal_code='12345',
            country='Test Country'
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
            user_type='AUTHOR'
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

    def test_user_registration_form(self):
        # Test valid data
        form_data = {
            'username': 'newuser',
            'email': 'new@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'New',
            'last_name': 'User',
            'user_type': 'USER'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Test invalid data - passwords don't match
        form_data['password2'] = 'differentpass'
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('password2', form.errors)
        
        # Test invalid data - invalid email
        form_data['email'] = 'invalid-email'
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)

        # Test author registration with bio
        form_data = {
            'username': 'newauthor',
            'email': 'author@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'New',
            'last_name': 'Author',
            'user_type': 'AUTHOR',
            'bio': 'Test Bio'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertTrue(form.is_valid())

        # Test author registration without bio
        form_data.pop('bio')
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('bio', form.errors)
        
    def test_book_form(self):
        # Create a test image file
        image = SimpleUploadedFile(
            name='test_image.jpg',
            content=b'GIF87a\x01\x00\x01\x00\x80\x01\x00\x00\x00\x00ccc,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;',
            content_type='image/gif'
        )

        # Test valid data
        form_data = {
            'title': 'Test Book',
            'authors': [self.author.author_id],
            'isbn': '0987654321',
            'publication_date': '2024-01-01',
            'pages': 200,
            'available_copies': 5,
            'total_copies': 5,
            'description': 'Test Description',
            'publisher': self.publisher.publisher_id,
            'genres': [self.genre.genre_id]
        }
        form_files = {
            'cover_image': image
        }
        form = BookForm(data=form_data, files=form_files)
        if not form.is_valid():
            print("Book form errors:", form.errors)
        self.assertTrue(form.is_valid())
        
        # Test invalid data - negative copies
        form_data['available_copies'] = -1
        form = BookForm(data=form_data, files=form_files)
        self.assertFalse(form.is_valid())
        self.assertIn('available_copies', form.errors)
        
        # Test invalid data - available copies > total copies
        form_data['available_copies'] = 10
        form_data['total_copies'] = 5
        form = BookForm(data=form_data, files=form_files)
        self.assertFalse(form.is_valid())
        self.assertIn('available_copies', form.errors)

        # Test invalid data - duplicate ISBN
        form_data['available_copies'] = 5
        form_data['isbn'] = self.book.isbn
        form = BookForm(data=form_data, files=form_files)
        self.assertFalse(form.is_valid())
        self.assertIn('isbn', form.errors)
        
    def test_author_form(self):
        # Create a new user for testing
        test_user = User.objects.create_user(
            username='newauthor',
            email='newauthor@example.com',
            password='testpass123',
            first_name='New',
            last_name='Author',
            user_type='AUTHOR'
        )

        # Test valid data
        form_data = {
            'user': test_user.id,
            'bio': 'Test Bio',
            'first_name': 'New',
            'last_name': 'Author'
        }
        form = AuthorForm(data=form_data)
        if not form.is_valid():
            print("Form errors:", form.errors)
        self.assertTrue(form.is_valid())
        
        # Test invalid data - missing required fields
        form_data.pop('bio')
        form = AuthorForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('bio', form.errors)
        
    def test_publisher_form(self):
        # Test valid data
        form_data = {
            'name': 'New Publisher',
            'address': 'Test Address',
            'phone': '1234567890',
            'email': 'publisher@test.com',
            'website': 'www.test.com',
            'location': self.location.location_id
        }
        form = PublisherForm(data=form_data)
        if not form.is_valid():
            print("Publisher form errors:", form.errors)
        self.assertTrue(form.is_valid())
        
        # Test invalid data - invalid email
        form_data['email'] = 'invalid-email'
        form = PublisherForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        
        # Test invalid data - invalid website
        form_data['email'] = 'publisher@test.com'
        form_data['website'] = 'invalid-url'
        form = PublisherForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('website', form.errors)

        # Test duplicate publisher
        form_data['website'] = 'www.test.com'
        form_data['name'] = self.publisher.name
        form_data['email'] = self.publisher.email
        form = PublisherForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        
    def test_review_form(self):
        # Test valid data
        form_data = {
            'rating': 5,
            'comment': 'Great book!'
        }
        form = ReviewForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Test invalid data - rating out of range
        form_data['rating'] = 6
        form = ReviewForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors)
        
        # Test invalid data - negative rating
        form_data['rating'] = -1
        form = ReviewForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('rating', form.errors)
        
    def test_borrowing_form(self):
        # Test valid data
        form_data = {
            'book': self.book.book_id,
            'user': self.user.id,
            'due_date': (timezone.now() + timedelta(days=14)).date()
        }
        form = BorrowingForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Test invalid data - past due date
        form_data['due_date'] = timezone.now().date() - timedelta(days=1)
        form = BorrowingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('due_date', form.errors)

        # Test invalid data - book not available
        self.book.available_copies = 0
        self.book.save()
        form_data['due_date'] = (timezone.now() + timedelta(days=14)).date()
        form = BorrowingForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('book', form.errors)
        
    def test_book_extension_form(self):
        # Test valid data
        form_data = {
            'book': self.book.book_id,
            'user': self.user.id,
            'extension_days': 7
        }
        form = BookExtensionForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Test invalid data - negative extension days
        form_data['extension_days'] = -1
        form = BookExtensionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('extension_days', form.errors)
        
        # Test invalid data - too many extension days
        form_data['extension_days'] = 31
        form = BookExtensionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('extension_days', form.errors)
        
    def test_book_reservation_form(self):
        # Test valid data
        form_data = {
            'book': self.book.book_id,
            'user': self.user.id,
            'reservation_date': (timezone.now() + timedelta(days=1)).date()
        }
        form = BookReservationForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Test invalid data - past reservation date
        form_data['reservation_date'] = timezone.now().date() - timedelta(days=1)
        form = BookReservationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('reservation_date', form.errors)
        
    def test_genre_form(self):
        # Test valid data
        form_data = {
            'name': 'New Genre',
            'description': 'New Description'
        }
        form = GenreForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Test invalid data - duplicate name
        form_data['name'] = self.genre.name
        form = GenreForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
        
    def test_transaction_form(self):
        # Test valid data
        form_data = {
            'book': self.book.book_id,
            'user': self.user.id,
            'transaction_type': 'BORROW',
            'amount': 0.00,
            'payment_method': 'CASH'
        }
        form = TransactionForm(data=form_data)
        self.assertTrue(form.is_valid())
        
        # Test invalid data - negative amount
        form_data['amount'] = -10.00
        form = TransactionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('amount', form.errors)
        
        # Test invalid data - invalid transaction type
        form_data['amount'] = 0.00
        form_data['transaction_type'] = 'INVALID'
        form = TransactionForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('transaction_type', form.errors)
        
    def test_form_widgets(self):
        # Test BookForm widgets
        form = BookForm()
        self.assertEqual(form.fields['title'].widget.attrs.get('class'), 'form-control')
        self.assertEqual(form.fields['description'].widget.attrs.get('class'), 'form-control')
        
        # Test ReviewForm widgets
        form = ReviewForm()
        self.assertEqual(form.fields['rating'].widget.attrs.get('class'), 'form-control')
        self.assertEqual(form.fields['comment'].widget.attrs.get('class'), 'form-control')
        
    def test_form_validation_messages(self):
        # Test custom validation messages
        form_data = {
            'username': 'testuser',
            'email': 'invalid-email',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
        self.assertIn('Enter a valid email address', str(form.errors['email']))
        
    def test_form_required_fields(self):
        # Test required fields
        form = UserRegistrationForm(data={})
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
        self.assertIn('email', form.errors)
        self.assertIn('password1', form.errors)
        self.assertIn('password2', form.errors)
        self.assertIn('first_name', form.errors)
        self.assertIn('last_name', form.errors)
        
    def test_form_max_length_validation(self):
        # Test max length validation
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'T' * 101,  # Exceeds max_length
            'last_name': 'User'
        }
        form = UserRegistrationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('first_name', form.errors) 