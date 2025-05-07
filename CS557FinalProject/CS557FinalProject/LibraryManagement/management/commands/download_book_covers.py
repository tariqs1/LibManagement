import os
import requests
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from CS557FinalProject.LibraryManagement.models import Book

class Command(BaseCommand):
    help = 'Download book cover images from cover_image_url and save to cover_image field.'

    def handle(self, *args, **options):
        books = Book.objects.exclude(cover_image_url__isnull=True).exclude(cover_image_url='')
        total = books.count()
        self.stdout.write(f'Processing {total} books...')
        for i, book in enumerate(books, 1):
            if book.cover_image:
                self.stdout.write(f'[{i}/{total}] Skipping {book.title} (already has cover image)')
                continue
            url = book.cover_image_url
            try:
                response = requests.get(url, timeout=10)
                response.raise_for_status()
                ext = os.path.splitext(url)[1].split('?')[0] or '.jpg'
                filename = f"book_{book.pk}{ext}"
                book.cover_image.save(filename, ContentFile(response.content), save=True)
                self.stdout.write(f'[{i}/{total}] Downloaded cover for {book.title}')
            except Exception as e:
                self.stdout.write(f'[{i}/{total}] Failed to download {url} for {book.title}: {e}')
        self.stdout.write('Done!') 