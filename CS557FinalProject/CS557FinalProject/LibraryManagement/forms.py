from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Book, Review, Author, Borrowing, Publisher, Genre, BookGenre, Transaction
from datetime import date
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.validators import validate_email, URLValidator


class UserRegistrationForm(UserCreationForm):
    USER_TYPE_CHOICES = (
        ('USER', 'Regular User'),
        ('AUTHOR', 'Author'),
        ('ADMIN', 'Administrator'),
    )

    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES)
    bio = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control'}), required=False, help_text="Required if registering as an Author")
    first_name = forms.CharField(max_length=100, required=True)
    last_name = forms.CharField(max_length=100, required=True)

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password1', 'password2', 'user_type']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control'}),
            'user_type': forms.Select(attrs={'class': 'form-control'})
        }

    def clean(self):
        cleaned_data = super().clean()
        user_type = cleaned_data.get('user_type')
        bio = cleaned_data.get('bio')

        if user_type == 'AUTHOR' and not bio:
            self.add_error('bio', 'Bio is required for authors')

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.username = self.cleaned_data['email']
        if commit:
            user.save()
        return user


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 4})
        }

    def clean_rating(self):
        rating = self.cleaned_data.get('rating')
        if rating is None:
            raise forms.ValidationError("Rating is required")
        try:
            rating = int(rating)
            if rating < 1 or rating > 5:
                raise forms.ValidationError("Rating must be between 1 and 5")
            return rating
        except (TypeError, ValueError):
            raise forms.ValidationError("Rating must be a number between 1 and 5")

    def clean(self):
        cleaned_data = super().clean()
        rating = cleaned_data.get('rating')
        comment = cleaned_data.get('comment')

        if not rating:
            self.add_error('rating', 'Rating is required')
        elif not isinstance(rating, int) or rating < 1 or rating > 5:
            self.add_error('rating', 'Rating must be a number between 1 and 5')

        if not comment:
            self.add_error('comment', 'Comment is required')

        return cleaned_data


class BookForm(forms.ModelForm):
    authors = forms.ModelMultipleChoiceField(
        queryset=Author.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=True
    )
    genres = forms.ModelMultipleChoiceField(
        queryset=Genre.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=True
    )
    cover_image = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Book
        fields = ['title', 'authors', 'isbn', 'publication_date', 'description', 'cover_image', 
                 'available_copies', 'total_copies', 'pages', 'publisher', 'genres']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control'}),
            'publication_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'available_copies': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'total_copies': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'pages': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'publisher': forms.Select(attrs={'class': 'form-control'})
        }

    def clean(self):
        cleaned_data = super().clean()
        title = cleaned_data.get('title')
        isbn = cleaned_data.get('isbn')
        publication_date = cleaned_data.get('publication_date')
        available_copies = cleaned_data.get('available_copies')
        total_copies = cleaned_data.get('total_copies')
        pages = cleaned_data.get('pages')
        publisher = cleaned_data.get('publisher')
        authors = cleaned_data.get('authors')
        genres = cleaned_data.get('genres')

        if not title:
            self.add_error('title', 'Title is required')
        if not isbn:
            self.add_error('isbn', 'ISBN is required')
        if not publication_date:
            self.add_error('publication_date', 'Publication date is required')
        if not pages:
            self.add_error('pages', 'Number of pages is required')
        if not publisher:
            self.add_error('publisher', 'Publisher is required')
        if not authors:
            self.add_error('authors', 'At least one author is required')
        if not genres:
            self.add_error('genres', 'At least one genre is required')

        if available_copies is not None and total_copies is not None:
            if available_copies < 0:
                self.add_error('available_copies', 'Available copies cannot be negative')
            elif available_copies > total_copies:
                self.add_error('available_copies', 'Available copies cannot be greater than total copies')

        if isbn:
            # Check for duplicate ISBN, excluding the current instance if it exists
            isbn_exists = Book.objects.filter(isbn=isbn)
            if self.instance and self.instance.pk:
                isbn_exists = isbn_exists.exclude(pk=self.instance.pk)
            if isbn_exists.exists():
                self.add_error('isbn', 'A book with this ISBN already exists')

        if publication_date and publication_date > timezone.now().date():
            self.add_error('publication_date', 'Publication date cannot be in the future')

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
            if 'authors' in self.cleaned_data:
                instance.authors.set(self.cleaned_data['authors'])
            if 'genres' in self.cleaned_data:
                instance.genres.set(self.cleaned_data['genres'])
        return instance


class AuthorForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=100, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    bio = forms.CharField(required=True, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}))
    user = forms.ModelChoiceField(queryset=User.objects.filter(user_type='AUTHOR'), required=False)

    class Meta:
        model = Author
        fields = ['first_name', 'last_name', 'bio', 'user']

    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        bio = cleaned_data.get('bio')
        user = cleaned_data.get('user')

        if not first_name:
            self.add_error('first_name', 'First name is required')
        if not last_name:
            self.add_error('last_name', 'Last name is required')
        if not bio:
            self.add_error('bio', 'Bio is required for authors')

        if first_name and last_name:
            # Check for duplicate name, excluding the current instance and the user's own author profile
            name_exists = Author.objects.filter(
                first_name__iexact=first_name,
                last_name__iexact=last_name
            )
            if self.instance and self.instance.pk:
                name_exists = name_exists.exclude(pk=self.instance.pk)
            if user:
                name_exists = name_exists.exclude(user=user)
            if name_exists.exists():
                self.add_error('first_name', 'An author with this name already exists')
                self.add_error('last_name', 'An author with this name already exists')

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        if commit:
            instance.save()
        return instance


class PublisherForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = ['name', 'address', 'phone', 'email', 'website', 'location']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'location': forms.Select(attrs={'class': 'form-control'})
        }

    def clean(self):
        cleaned_data = super().clean()
        name = cleaned_data.get('name')
        email = cleaned_data.get('email')
        website = cleaned_data.get('website')
        location = cleaned_data.get('location')

        if not name:
            self.add_error('name', 'Name is required')
        if not email:
            self.add_error('email', 'Email is required')
        if not location:
            self.add_error('location', 'Location is required')

        if email:
            try:
                validate_email(email)
            except ValidationError:
                self.add_error('email', 'Enter a valid email address')

        if website:
            if not website.startswith(('http://', 'https://')):
                website = 'https://' + website
                cleaned_data['website'] = website
            try:
                URLValidator()(website)
            except ValidationError:
                self.add_error('website', 'Enter a valid URL')

        if name:
            # Check for duplicate name, excluding the current instance
            name_exists = Publisher.objects.filter(name__iexact=name)
            if self.instance and self.instance.pk:
                name_exists = name_exists.exclude(pk=self.instance.pk)
            if name_exists.exists():
                self.add_error('name', 'A publisher with this name already exists')

        return cleaned_data


class BorrowingForm(forms.ModelForm):
    class Meta:
        model = Borrowing
        fields = ['book', 'user', 'due_date', 'returned', 'return_date']
        widgets = {
            'book': forms.Select(attrs={'class': 'form-control'}),
            'user': forms.Select(attrs={'class': 'form-control'}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'returned': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'return_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'})
        }

    def clean(self):
        cleaned_data = super().clean()
        book = cleaned_data.get('book')
        user = cleaned_data.get('user')
        due_date = cleaned_data.get('due_date')
        returned = cleaned_data.get('returned')
        return_date = cleaned_data.get('return_date')

        if book and book.available_copies <= 0:
            self.add_error('book', 'This book is not available for borrowing')

        if user and book and Borrowing.objects.filter(book=book, user=user, returned=False).exists():
            self.add_error('book', 'You have already borrowed this book')

        if due_date and due_date <= timezone.now().date():
            self.add_error('due_date', 'Due date must be in the future')

        if returned and return_date and return_date > timezone.now().date():
            self.add_error('return_date', 'Return date cannot be in the future')

        return cleaned_data


class BookEditForm(forms.ModelForm):
    genres = forms.ModelMultipleChoiceField(
        queryset=Genre.objects.all(),
        widget=forms.CheckboxSelectMultiple(attrs={'class': 'form-check-input'}),
        required=False
    )

    class Meta:
        model = Book
        fields = ['title', 'authors', 'isbn', 'publication_date', 'pages', 'available_copies', 
                 'total_copies', 'description', 'cover_image', 'publisher', 'genres']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'authors': forms.SelectMultiple(attrs={'class': 'form-control'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control'}),
            'publication_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5}),
            'pages': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'available_copies': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'total_copies': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'cover_image': forms.FileInput(attrs={'class': 'form-control'}),
            'publisher': forms.Select(attrs={'class': 'form-control'})
        }

    def clean(self):
        cleaned_data = super().clean()
        available_copies = cleaned_data.get('available_copies')
        total_copies = cleaned_data.get('total_copies')

        if available_copies and total_copies and available_copies > total_copies:
            self.add_error('available_copies', 'Available copies cannot be greater than total copies')

        return cleaned_data


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'})
        }


class BookExtensionForm(forms.ModelForm):
    extension_days = forms.IntegerField(
        min_value=1,
        max_value=14,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    class Meta:
        model = Borrowing
        fields = ['book']
        widgets = {
            'book': forms.HiddenInput()
        }

    def clean(self):
        cleaned_data = super().clean()
        book = cleaned_data.get('book')
        extension_days = cleaned_data.get('extension_days')

        if book and extension_days:
            if not book.is_available():
                self.add_error('book', 'This book is not available for extension')
            if self.instance and self.instance.due_date and self.instance.due_date < timezone.now().date():
                self.add_error('book', 'Cannot extend an overdue book')

        return cleaned_data


class BookReservationForm(forms.ModelForm):
    reservation_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))

    class Meta:
        model = Borrowing
        fields = ['book', 'reservation_date']
        widgets = {
            'book': forms.Select(attrs={'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        book = cleaned_data.get('book')
        reservation_date = cleaned_data.get('reservation_date')

        if not book:
            self.add_error('book', 'Book is required')
            return cleaned_data

        if not reservation_date:
            self.add_error('reservation_date', 'Reservation date is required')
            return cleaned_data

        if reservation_date < timezone.now().date():
            self.add_error('reservation_date', 'Reservation date cannot be in the past')

        # Check if user already has a reservation for this book
        if self.user:
            existing_reservation = Borrowing.objects.filter(
                book=book,
                user=self.user,
                returned=False
            ).exists()
            if existing_reservation:
                self.add_error('book', 'You already have a reservation for this book')

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.user = self.user
        instance.returned = False
        instance.return_date = None
        instance.due_date = self.cleaned_data['reservation_date']
        if commit:
            instance.save()
        return instance


class GenreForm(forms.ModelForm):
    class Meta:
        model = Genre
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3})
        }

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if name:
            # Check for duplicate name, excluding the current instance if it exists
            name_exists = Genre.objects.filter(name__iexact=name)
            if self.instance and self.instance.pk:
                name_exists = name_exists.exclude(pk=self.instance.pk)
            if name_exists.exists():
                raise forms.ValidationError('A genre with this name already exists')
        return name


class TransactionForm(forms.ModelForm):
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

    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=True
    )

    transaction_type = forms.ChoiceField(
        choices=TRANSACTION_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )
    amount = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        initial=0.00,
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )
    note = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False
    )

    class Meta:
        model = Transaction
        fields = ['user', 'book', 'transaction_type', 'amount', 'payment_method', 'note']
        widgets = {
            'book': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        book = cleaned_data.get('book')
        transaction_type = cleaned_data.get('transaction_type')
        amount = cleaned_data.get('amount')
        payment_method = cleaned_data.get('payment_method')

        if not user:
            self.add_error('user', 'User is required')
        if not book:
            self.add_error('book', 'Book is required')
        if not transaction_type:
            self.add_error('transaction_type', 'Transaction type is required')

        if transaction_type == 'FINE' and (not amount or amount <= 0):
            self.add_error('amount', 'Amount is required for fine transactions')
        if transaction_type == 'FINE' and not payment_method:
            self.add_error('payment_method', 'Payment method is required for fine transactions')

        return cleaned_data


class BookCSVUploadForm(forms.Form):
    csv_file = forms.FileField(label="Select CSV file")


class ContactForm(forms.Form):
    subject = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5}))