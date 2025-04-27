from django.contrib import admin
from .models import Book, Author, BookGenre, BookAuthor, Genre, Publisher, Location, User, BorrowedBook, Transaction, \
    LateFee, Staff, Review, Borrowing

admin.site.register(Location)
admin.site.register(Publisher)
admin.site.register(Genre)
admin.site.register(Author)
admin.site.register(Book)
admin.site.register(BookAuthor)
admin.site.register(BookGenre)
admin.site.register(User)
admin.site.register(BorrowedBook)
admin.site.register(LateFee)
admin.site.register(Staff)
admin.site.register(Transaction)
admin.site.register(Review)
admin.site.register(Borrowing)