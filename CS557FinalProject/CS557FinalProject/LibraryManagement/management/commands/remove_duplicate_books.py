from django.core.management.base import BaseCommand
from CS557FinalProject.LibraryManagement.models import Book

class Command(BaseCommand):
    help = 'Remove duplicate books by ISBN, keeping only the first one for each ISBN.'

    def handle(self, *args, **options):
        seen = set()
        deleted = 0
        for book in Book.objects.order_by('book_id'):
            if book.isbn in seen:
                book.delete()
                deleted += 1
            else:
                seen.add(book.isbn)
        self.stdout.write(self.style.SUCCESS(f'Removed {deleted} duplicate books.')) 