from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.template.defaultfilters import default
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError

@receiver(post_migrate)
def create_groups(sender, **kwargs):
    staff_group, created = Group.objects.get_or_create(name='Staff')
    user_group, created = Group.objects.get_or_create(name='User')
    admin_group, created = Group.objects.get_or_create(name='Admin')

class PaymentStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    PAID = 'PAID', 'Paid'
    WAIVED = 'WAIVED', 'Waived'

class BorrowStatus(models.TextChoices):
    BORROWED = 'Borrowed', 'Borrowed'
    RETURNED = 'Returned', 'Returned'
    EXTENDED = 'Extended', 'Extended'
    OVERDUE = 'Overdue', 'Overdue'

class StaffStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Active'
    INACTIVE = 'INACTIVE', 'Inactive'
    ON_LEAVE = 'On Leave', 'On Leave'

class TransactionType(models.TextChoices):
    BORROW = 'BORROW', 'Borrow'
    RETURN = 'RETURN', 'Return'
    FEE = 'FEE', 'Fee'
    EXTENSION = 'Extension', 'Extension'

class PaymentMethod(models.TextChoices):
    CASH = 'CASH', 'Cash'
    CARD = 'CARD', 'Card'
    ONLINE = 'ONLINE', 'Online'
    WAIVER = 'Waiver', 'Waiver'

class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('user_type', 'ADMIN')
        return self.create_user(email, password, **extra_fields)

class User(AbstractUser):
    USER_TYPE_CHOICES = (
        ('USER', 'Regular User'),
        ('AUTHOR', 'Author'),
        ('ADMIN', 'Administrator'),
    )
    email = models.EmailField(unique=True)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='USER')
    date_joined = models.DateTimeField(auto_now_add=True)
    username = models.CharField(max_length=150, unique=True, default='user')

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class Author(models.Model):
    author_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='author_profile')
    bio = models.TextField(blank=True, null=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Location(models.Model):
    location_id = models.AutoField(primary_key=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.city}, {self.state}"

class Publisher(models.Model):
    publisher_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=45)
    email = models.EmailField(max_length=100)
    website = models.URLField(max_length=255)
    location = models.ForeignKey(Location, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

class Genre(models.Model):
    genre_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500)

    def __str__(self):
        return self.name

class Book(models.Model):
    book_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    isbn = models.CharField(max_length=20)
    publication_date = models.DateField()
    pages = models.IntegerField()
    available_copies = models.IntegerField()
    total_copies = models.IntegerField()
    description = models.TextField(max_length=500)
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    publisher = models.ForeignKey(Publisher, on_delete=models.CASCADE, null=True, blank=True)
    authors = models.ManyToManyField(Author, through='BookAuthor')
    genres = models.ManyToManyField(Genre, through='BookGenre')

    def __str__(self):
        return self.title

    def is_available(self):
        return self.available_copies > 0

class BookAuthor(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('book', 'author')

class BookGenre(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    genre = models.ForeignKey(Genre, on_delete=models.CASCADE)

    class Meta:
        unique_together = ('book', 'genre')

class Borrowing(models.Model):
    id = models.BigAutoField(primary_key=True)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    borrow_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(null=True, blank=True)
    due_date = models.DateField()
    returned = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.book.title}"

    def is_overdue(self):
        return not self.returned and self.due_date < timezone.now().date()

class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('book', 'user')
        ordering = ['-created_at']

    def clean(self):
        if self.rating is None:
            raise ValidationError({'rating': 'Rating is required'})
        if not isinstance(self.rating, int) or self.rating < 1 or self.rating > 5:
            raise ValidationError({'rating': 'Rating must be between 1 and 5'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username}'s review of {self.book.title}"

class Transaction(models.Model):
    TRANSACTION_TYPE_CHOICES = (
        ('BORROW', 'Borrow'),
        ('RETURN', 'Return'),
        ('FINE', 'Fine'),
        ('RESERVATION', 'Reservation'),
    )

    PAYMENT_METHOD_CHOICES = (
        ('CASH', 'Cash'),
        ('CARD', 'Credit/Debit Card'),
        ('ONLINE', 'Online Payment'),
    )

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE, null=True, blank=True)
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, null=True, blank=True)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def clean(self):
        if self.amount < 0:
            raise ValidationError({'amount': 'Amount cannot be negative'})

        if self.transaction_type in ['BORROW', 'RETURN'] and self.amount != 0:
            raise ValidationError({
                'amount': f'{self.transaction_type.capitalize()} transactions should have zero amount'
            })

        if self.transaction_type == 'BORROW' and self.book and self.book.available_copies <= 0:
            raise ValidationError({
                'book': 'This book is not available for borrowing'
            })

        # Payment method is required for FINE transactions
        if self.transaction_type == 'FINE' and not self.payment_method:
            raise ValidationError({
                'payment_method': 'Payment method is required for fine transactions'
            })

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.transaction_type} - {self.book.title if self.book else 'No Book'} by {self.user.username}"

class Staff(models.Model):
    STATUS_CHOICES = (
        ('ACTIVE', 'Active'),
        ('INACTIVE', 'Inactive'),
    )

    staff_id = models.AutoField(primary_key=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile', null=True, blank=True)
    phone = models.CharField(max_length=20)
    position = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='ACTIVE')

    def __str__(self):
        return f"{self.user.username if self.user else 'No User'} - {self.position}"