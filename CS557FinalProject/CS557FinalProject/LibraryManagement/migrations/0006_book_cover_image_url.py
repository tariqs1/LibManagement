# Generated by Django 4.2.10 on 2025-05-06 21:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('LibraryManagement', '0005_alter_transaction_book_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='book',
            name='cover_image_url',
            field=models.URLField(blank=True, null=True),
        ),
    ]
