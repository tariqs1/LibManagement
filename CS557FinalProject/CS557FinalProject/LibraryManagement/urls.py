from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('books/', views.book_list, name='book_list'),
    path('books/<int:book_id>/', views.book_detail, name='book_detail'),
    path('books/<int:book_id>/borrow/', views.borrow_book, name='borrow_book'),
    path('books/add/', views.add_book, name='add_book'),
    path('books/<int:book_id>/edit/', views.edit_book, name='edit_book'),
    path('books/<int:book_id>/delete/', views.delete_book, name='delete_book'),
    path('books/<int:book_id>/reserve/', views.reserve_book, name='reserve_book'),
    path('borrows/<int:borrow_id>/return/', views.return_book, name='return_book'),
    path('borrow/<int:borrow_id>/extend/', views.extend_borrow, name='extend_borrow'),
    path('authors/', views.author_list, name='author_list'),
    path('authors/<int:author_id>/', views.author_detail, name='author_detail'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('search/', views.search, name='search'),
    path('dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/reports/', views.generate_report, name='generate_report'),
    path('dashboard/transactions/', views.transaction_list, name='transaction_list'),
    path('transactions/create/', views.create_transaction, name='create_transaction'),
    path('contact/', views.contact, name='contact'),
    path('book/<int:book_id>/delete/', views.delete_book, name='delete_book'),
]
