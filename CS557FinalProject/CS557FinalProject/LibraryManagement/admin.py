from django.contrib import admin
from .models import Book, Author, BookGenre, Genre, Publisher, Location, User, Borrowing, Transaction, Staff, Review, BookAuthor

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'user_type', 'is_active')
    list_filter = ('user_type', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    ordering = ('username',)

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'isbn', 'publication_date', 'available_copies', 'total_copies')
    list_filter = ('publication_date', 'publisher')
    search_fields = ('title', 'isbn', 'description')
    ordering = ('title',)

@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ('first_name', 'last_name')
    search_fields = ('first_name', 'last_name')
    ordering = ('last_name', 'first_name')

@admin.register(Genre)
class GenreAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    search_fields = ('name',)
    ordering = ('name',)

@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone')
    search_fields = ('name', 'email')
    ordering = ('name',)

@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('city', 'state', 'postal_code')
    search_fields = ('city', 'state', 'postal_code')
    ordering = ('city',)

@admin.register(Borrowing)
class BorrowingAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'borrow_date', 'due_date', 'returned')
    list_filter = ('returned', 'borrow_date', 'due_date')
    search_fields = ('book__title', 'user__username')
    ordering = ('-borrow_date',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['user', 'book', 'transaction_type', 'created_at', 'amount', 'payment_method']
    list_filter = ['transaction_type', 'created_at', 'payment_method']
    search_fields = ['user__username', 'book__title', 'transaction_type']
    ordering = ['-created_at']

@admin.register(Staff)
class StaffAdmin(admin.ModelAdmin):
    list_display = ('user', 'position', 'status')
    list_filter = ('status', 'position')
    search_fields = ('user__username', 'phone')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'rating', 'created_at')
    list_filter = ('rating', 'created_at')
    search_fields = ('book__title', 'user__username', 'comment')
    ordering = ('-created_at',)

@admin.register(BookAuthor)
class BookAuthorAdmin(admin.ModelAdmin):
    list_display = ('book', 'author')
    search_fields = ('book__title', 'author__first_name', 'author__last_name')

@admin.register(BookGenre)
class BookGenreAdmin(admin.ModelAdmin):
    list_display = ('book', 'genre')
    search_fields = ('book__title', 'genre__name')