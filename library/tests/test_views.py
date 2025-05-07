from django.urls import reverse
from django.test import TestCase
from django.contrib.auth.models import User
from library.models import Book, Member, Transaction

class TestViews(TestCase):
    def setUp(self):
        # Create test users
        self.staff_user = User.objects.create_user(
            username='staff',
            password='testpass123',
            is_staff=True
        )
        self.member_user = User.objects.create_user(
            username='member',
            password='testpass123'
        )
        
    def test_create_transaction(self):
        """Test transaction creation view"""
        # Create a book first
        book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            isbn="1234567890",
            quantity=5
        )
        
        # Create a member
        member = Member.objects.create(
            name="Test Member",
            email="test@example.com",
            phone="1234567890"
        )
        
        # Login as staff
        self.client.login(username='staff', password='testpass123')
        
        # Test GET request
        response = self.client.get(reverse('create_transaction'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'library/transaction_form.html')
        
        # Test POST request with valid data
        data = {
            'book': book.id,
            'member': member.id,
            'transaction_type': 'BORROW',
            'quantity': 1
        }
        response = self.client.post(reverse('create_transaction'), data)
        self.assertEqual(response.status_code, 302)  # Should redirect after successful creation
        
        # Verify transaction was created
        transaction = Transaction.objects.first()
        self.assertIsNotNone(transaction)
        self.assertEqual(transaction.book, book)
        self.assertEqual(transaction.member, member)
        self.assertEqual(transaction.transaction_type, 'BORROW')
        self.assertEqual(transaction.quantity, 1)
        
        # Verify book quantity was updated
        book.refresh_from_db()
        self.assertEqual(book.quantity, 4)  # 5 - 1 = 4

    def test_transaction_list_view(self):
        """Test transaction list view"""
        # Create a test transaction
        book = Book.objects.create(
            title="Test Book",
            author="Test Author",
            isbn="1234567890",
            quantity=5
        )
        member = Member.objects.create(
            name="Test Member",
            email="test@example.com",
            phone="1234567890"
        )
        transaction = Transaction.objects.create(
            book=book,
            member=member,
            transaction_type='BORROW',
            quantity=1
        )
        
        # Test without login (should redirect to login)
        response = self.client.get(reverse('transaction_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
        
        # Test with staff login
        self.client.login(username='staff', password='testpass123')
        response = self.client.get(reverse('transaction_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'library/transaction_list.html')
        self.assertContains(response, book.title)
        self.assertContains(response, member.name)
        
        # Test with member login (should only see their transactions)
        self.client.login(username='member', password='testpass123')
        response = self.client.get(reverse('transaction_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'library/transaction_list.html')
        self.assertContains(response, book.title)
        self.assertContains(response, member.name)

    def test_book_list_view(self):
        """Test book list view"""
        # Create test books
        book1 = Book.objects.create(
            title="Python Programming",
            author="John Doe",
            isbn="1234567890",
            quantity=5
        )
        book2 = Book.objects.create(
            title="Django Web Development",
            author="Jane Smith",
            isbn="0987654321",
            quantity=3
        )
        
        # Test without login (should redirect to login)
        response = self.client.get(reverse('book_list'))
        self.assertEqual(response.status_code, 302)
        self.assertIn('login', response.url)
        
        # Test with staff login
        self.client.login(username='staff', password='testpass123')
        response = self.client.get(reverse('book_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'library/book_list.html')
        self.assertContains(response, book1.title)
        self.assertContains(response, book2.title)
        
        # Test search functionality
        response = self.client.get(reverse('book_list'), {'search': 'Python'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, book1.title)
        self.assertNotContains(response, book2.title)
        
        # Test with member login
        self.client.login(username='member', password='testpass123')
        response = self.client.get(reverse('book_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'library/book_list.html')
        self.assertContains(response, book1.title)
        self.assertContains(response, book2.title) 