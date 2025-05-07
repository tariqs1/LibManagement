from django.contrib import admin
from .models import Book, Author, BookGenre, Genre, Publisher, Location, User, Borrowing, Transaction, Staff, Review, BookAuthor
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
import csv
from .forms import BookCSVUploadForm
from django.contrib.auth import get_user_model
import random

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
    change_list_template = "admin/book_changelist.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path('upload-csv/', self.admin_site.admin_view(self.upload_csv), name='upload_csv'),
        ]
        return custom_urls + urls

    def upload_csv(self, request):
        if request.method == "POST":
            form = BookCSVUploadForm(request.POST, request.FILES)
            if form.is_valid():
                csv_file = form.cleaned_data['csv_file']
                decoded_file = csv_file.read().decode('utf-8').splitlines()
                reader = csv.DictReader(decoded_file)
                for row in reader:
                    # Map CSV columns to model fields
                    isbn = row['isbn']
                    title = row['book-title']
                    author_name = row['book-author']
                    year = row['year-of-publication']
                    publisher_name = row['publisher']
                    cover_image_url = row.get('image-url-l', '')
                    # Publisher fields
                    address = row.get('address', '')
                    city = row.get('city', '')
                    state = row.get('state', '')
                    country = row.get('country', '')
                    postal_code = row.get('postal_code', '')
                    phone_number = row.get('phone_number', '')
                    email = row.get('email', '')
                    website = row.get('website', '')

                    # Always create or get a Location
                    location, _ = Location.objects.get_or_create(
                        city=city,
                        state=state,
                        postal_code=postal_code,
                        country=country
                    )

                    publisher, created = Publisher.objects.get_or_create(
                        name=publisher_name,
                        defaults={
                            'address': address,
                            'phone': phone_number,
                            'email': email,
                            'website': website,
                            'location': location,
                        }
                    )
                    if not created and (not publisher.location_id):
                        publisher.location = location
                        publisher.save()

                    # Author (split if multiple authors)
                    first_name = author_name.split()[0]
                    last_name = ' '.join(author_name.split()[1:]) if len(author_name.split()) > 1 else ''
                    User = get_user_model()
                    base_username = (first_name + last_name).replace(' ', '').lower()
                    username = base_username
                    suffix = 1
                    while User.objects.filter(username=username).exists():
                        username = f"{base_username}{suffix}"
                        suffix += 1
                    user_email = f"{username}@imported.local"
                    user, _ = User.objects.get_or_create(
                        username=username,
                        defaults={
                            'email': user_email,
                            'first_name': first_name,
                            'last_name': last_name,
                            'user_type': 'AUTHOR',
                        }
                    )
                    user.set_password('8675309igotit')
                    user.save()
                    author, _ = Author.objects.get_or_create(
                        first_name=first_name,
                        last_name=last_name,
                        defaults={'bio': '', 'user': user}
                    )

                    # Create or update Book
                    pages = random.randint(100, 1000)
                    total_copies = random.randint(1, 10)
                    available_copies = total_copies
                    book, created = Book.objects.update_or_create(
                        isbn=isbn,
                        defaults={
                            'title': title,
                            'publisher': publisher,
                            'publication_date': f"{year}-01-01",
                            'pages': pages,
                            'total_copies': total_copies,
                            'available_copies': available_copies,
                            'cover_image_url': cover_image_url,
                            # Add more fields as needed
                        }
                    )
                self.message_user(request, "Books imported successfully!", level=messages.SUCCESS)
                return redirect("..")
        else:
            form = BookCSVUploadForm()
        return render(request, "admin/book_csv_upload.html", {"form": form})

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