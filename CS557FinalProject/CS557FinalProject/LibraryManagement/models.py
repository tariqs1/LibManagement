from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager, Group, Permission
from django.db.models.signals import post_migrate
from django.dispatch import receiver
from django.template.defaultfilters import default


@receiver(post_migrate)
def create_groups(sender, **kwargs):
    staff_group, created = Group.objects.get_or_create(name='Staff')
    user_group, created = Group.objects.get_or_create(name='User')

class PaymentStatus(models.TextChoices):
    PENDING = 'Pending', 'Pending'
    PAID = 'Paid', 'Paid'
    WAIVED = 'Waived', 'Waived'

class BorrowStatus(models.TextChoices):
    BORROWED = 'Borrowed', 'Borrowed'
    RETURNED = 'Returned', 'Returned'
    EXTENDED = 'Extended', 'Extended'

class StaffStatus(models.TextChoices):
    ACTIVE = 'Active', 'Active'
    INACTIVE = 'Inactive', 'Inactive'

class TransactionType(models.TextChoices):
    BORROW = 'Borrow', 'Borrow'
    RETURN = 'Return', 'Return'
    FEE = 'Fee', 'Fee'

class PaymentMethod(models.TextChoices):
    CASH = 'Cash', 'Cash'
    CARD = 'Card', 'Card'
    ONLINE = 'Online', 'Online'

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
        ('ADMIN', 'Admin'),
        ('USER', 'User'),
        ('AUTHOR', 'Author'),
    )

    username = None
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    user_type = models.CharField(max_length=10, choices=USER_TYPE_CHOICES, default='USER')
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

class Author(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='author_profile')
    bio = models.TextField(blank=True, null=True)
    author_id = models.AutoField(primary_key=True,default=None, unique=True)
    first_name = models.CharField(max_length=100,default=None)
    last_name = models.CharField(max_length=100,default=None)

class Location(models.Model):
    location_id = models.AutoField(primary_key=True)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100)

class Publisher(models.Model):
    publisher_id = models.AutoField(primary_key=True,default=None)
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=45)
    email = models.CharField(max_length=100)
    website = models.CharField(max_length=255)
    location_id = models.ForeignKey(Location, on_delete=models.CASCADE)

class Book(models.Model):
    book_id = models.AutoField(primary_key=True, default=None)
    title = models.CharField(max_length=255)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    isbn = models.CharField(max_length=20)
    publication_date = models.DateField()
    pages = models.IntegerField(default=None)
    available_copies = models.IntegerField()
    total_copies = models.IntegerField(default=None)
    description = models.TextField()
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    publisher_id = models.ForeignKey(Publisher, on_delete=models.CASCADE, default=None)

class BookAuthor(models.Model):
    book_id = models.ForeignKey(Book, on_delete=models.CASCADE)
    author_id = models.ForeignKey(Author, on_delete=models.CASCADE)

    class Meta:
        unique_together = (('book_id', 'author_id'),)

class Genre(models.Model):
    genre_id = models.AutoField(primary_key=True,default=None)
    name = models.CharField(max_length=100)
    description = models.TextField(max_length=500)

class BookGenre(models.Model):
    book_id = models.ForeignKey(Book, on_delete=models.CASCADE)
    genre_id = models.ForeignKey(Genre, on_delete=models.CASCADE)
    class Meta:
        unique_together = (('book_id', 'genre_id'),)

class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('book', 'user')

    def __str__(self):
        return f"Review by {self.user} for {self.book}"

class Borrowing(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    borrow_date = models.DateField(auto_now_add=True)
    return_date = models.DateField(null=True, blank=True)
    due_date = models.DateField()
    returned = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user} borrowed {self.book}"

class BorrowedBook(models.Model):
    borrow_id = models.AutoField(primary_key=True,default=None)
    book_id = models.ForeignKey(Book, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    borrow_date = models.DateField()
    due_date = models.DateField()
    return_date = models.DateField(null=True, blank=True)
    extended = models.BooleanField(default=False)
    extension_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=BorrowStatus.choices)

class LateFee(models.Model):
    fee_id = models.AutoField(primary_key=True,default=None)
    borrow_id = models.ForeignKey(BorrowedBook, on_delete=models.CASCADE)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    fee_date = models.DateField()
    payment_status = models.CharField(max_length=10, choices=PaymentStatus.choices)
    payment_date = models.DateField(null=True, blank=True)
    waived_by = models.ForeignKey('Staff', on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(max_length=500, blank=True)

class Staff(models.Model):
    staff_id = models.AutoField(primary_key=True,default=None)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    position = models.CharField(max_length=100)
    status = models.CharField(max_length=10, choices=StaffStatus.choices)
    password_hash = models.CharField(max_length=255)

class Transaction(models.Model):
    transaction_id = models.AutoField(primary_key=True,default=None)
    user_id = models.ForeignKey(User, on_delete=models.CASCADE)
    staff_id = models.ForeignKey(Staff, on_delete=models.CASCADE)
    transaction_date = models.DateTimeField()
    transaction_type = models.CharField(max_length=10, choices=TransactionType.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PaymentMethod.choices)
    note = models.TextField(max_length=500, blank=True)