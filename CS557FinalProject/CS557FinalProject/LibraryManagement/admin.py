from django.contrib import admin
from .models import User, Author, Book, Review, Borrowing


class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'first_name', 'last_name', 'user_type', 'date_joined')
    search_fields = ('email', 'first_name', 'last_name')
    list_filter = ('user_type', 'is_active')


class AuthorAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'user')
    search_fields = ('user__first_name', 'user__last_name')


class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'publication_date', 'available_copies')
    search_fields = ('title', 'author__user__first_name', 'author__user__last_name', 'isbn')
    list_filter = ('publication_date',)


class ReviewAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'rating', 'created_at')
    search_fields = ('book__title', 'user__email', 'user__first_name')
    list_filter = ('rating', 'created_at')


class BorrowingAdmin(admin.ModelAdmin):
    list_display = ('book', 'user', 'borrow_date', 'due_date', 'return_date', 'returned')
    search_fields = ('book__title', 'user__email', 'user__first_name')
    list_filter = ('returned', 'borrow_date')


admin.site.register(User, UserAdmin)
admin.site.register(Author, AuthorAdmin)
admin.site.register(Book, BookAdmin)
admin.site.register(Review, ReviewAdmin)
admin.site.register(Borrowing, BorrowingAdmin)
from django.contrib import admin

# Register your models here.
