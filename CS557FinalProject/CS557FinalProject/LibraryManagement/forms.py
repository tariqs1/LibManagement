from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Book, Review, Author


class UserRegistrationForm(UserCreationForm):
    USER_TYPE_CHOICES = (
        ('USER', 'Regular User'),
        ('AUTHOR', 'Author'),
    )

    user_type = forms.ChoiceField(choices=USER_TYPE_CHOICES)
    bio = forms.CharField(widget=forms.Textarea, required=False, help_text="Required if registering as an Author")

    class Meta:
        model = User
        fields = ['email', 'first_name', 'last_name', 'password1', 'password2', 'user_type']

    def save(self, commit=True):
        user = super().save(commit=False)
        user_type = self.cleaned_data['user_type']
        user.user_type = user_type

        if commit:
            user.save()

            if user_type == 'AUTHOR':
                Author.objects.create(
                    user=user,
                    bio=self.cleaned_data.get('bio', '')
                )

        return user


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'rows': 4})
        }


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = ['title', 'author', 'isbn', 'publication_date', 'description', 'cover_image', 'available_copies']
        widgets = {
            'publication_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 5})
        }