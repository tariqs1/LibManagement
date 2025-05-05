from django.db import connection
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Avg
from datetime import date, timedelta
from .models import Book, Review, Borrowing, User, Author
from .forms import UserRegistrationForm, ReviewForm, BookForm
from django.db.models import Q


def home(request):
    latest_books = Book.objects.annotate(
        average_rating=Avg('reviews__rating')
    ).order_by('-book_id')[:8]
    return render(request, 'home.html', {'latest_books': latest_books})

def book_list(request):
    search = {
        'search_title': request.GET.get('title', None),
        'search_isbn': request.GET.get('isbn', None),
        'search_author': request.GET.get('author', None),
        'search_genre': request.GET.get('genre', None),
    }

    books = []
    with connection.cursor() as cursor:
        cursor.callproc('search_bar', [
            search['search_title'],
            search['search_isbn'],
            search['search_author'],
            search['search_genre']
        ])

        columns = [col[0] for col in cursor.description]
        books = [dict(zip(columns, row)) for row in cursor.fetchall()]

        for book in books:
            book['authors'] = book['authors'].split(',') if book['authors'] else []
            book['genres'] = book['genres'].split(',') if book['genres'] else []

    return render(request, 'book_list.html', {
        'books': books,
        'search': {k: v for k, v in search.items() if v is not None}
    })

def book_detail(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    reviews = book.reviews.all().order_by('-created_at')

    if request.method == 'POST' and request.user.is_authenticated:
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            review.user = request.user
            review.save()
            messages.success(request, 'Your review has been added!')
            return redirect('book_detail', book_id=book.id)
    else:
        form = ReviewForm()

    return render(request, 'book_detail.html', {
        'book': book,
        'reviews': reviews,
        'form': form
    })


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form = UserRegistrationForm()

    return render(request, 'register.html', {'form': form})


@login_required
def profile(request):
    borrowed_books = Borrowing.objects.filter(user=request.user, returned=False)
    past_borrows = Borrowing.objects.filter(user=request.user, returned=True)
    reviews = Review.objects.filter(user=request.user)

    return render(request, 'profile.html', {
        'borrowed_books': borrowed_books,
        'past_borrows': past_borrows,
        'reviews': reviews
    })


@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)

    if book.available_copies > 0:
        # Logic to calculate due date (e.g., 14 days from now)
        due_date = date.today() + timedelta(days=14)

        Borrowing.objects.create(
            book=book,
            user=request.user,
            due_date=due_date
        )

        book.available_copies -= 1
        book.save()

        messages.success(request, f'You have successfully borrowed "{book.title}"')
    else:
        messages.error(request, 'Sorry, this book is currently unavailable')

    return redirect('book_detail', book_id=book.id)


@login_required
def return_book(request, borrow_id):
    borrow = get_object_or_404(Borrowing, id=borrow_id, user=request.user)

    borrow.returned = True
    borrow.return_date = date.today()
    borrow.save()

    book = borrow.book
    book.available_copies += 1
    book.save()

    messages.success(request, f'You have successfully returned "{book.title}"')
    return redirect('profile')


# Admin views
@login_required
def add_book(request):
    if request.user.user_type != 'ADMIN' and request.user.user_type != 'AUTHOR':
        messages.error(request, 'You do not have permission to add books')
        return redirect('home')

    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save()
            messages.success(request, f'"{book.title}" has been added successfully')
            return redirect('book_detail', book_id=book.id)
    else:
        form = BookForm()

    return render(request, 'add_book.html', {'form': form})
