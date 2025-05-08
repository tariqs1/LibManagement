from django.db import migrations
from django.db import connection

def create_search_procedure(apps, schema_editor):
    if connection.vendor == 'mysql':
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE PROCEDURE search_bar(IN search_term VARCHAR(255))
                BEGIN
                    SELECT b.*, 
                           GROUP_CONCAT(DISTINCT a.first_name, ' ', a.last_name) as authors,
                           GROUP_CONCAT(DISTINCT g.name) as genres,
                           AVG(r.rating) as average_rating
                    FROM LibraryManagement_book b
                    LEFT JOIN LibraryManagement_bookauthor ba ON b.book_id = ba.book_id_id
                    LEFT JOIN LibraryManagement_author a ON ba.author_id_id = a.author_id
                    LEFT JOIN LibraryManagement_bookgenre bg ON b.book_id = bg.book_id_id
                    LEFT JOIN LibraryManagement_genre g ON bg.genre_id_id = g.genre_id
                    LEFT JOIN LibraryManagement_review r ON b.book_id = r.book_id
                    WHERE b.title LIKE CONCAT('%', search_term, '%')
                       OR b.isbn LIKE CONCAT('%', search_term, '%')
                       OR b.description LIKE CONCAT('%', search_term, '%')
                       OR a.first_name LIKE CONCAT('%', search_term, '%')
                       OR a.last_name LIKE CONCAT('%', search_term, '%')
                       OR g.name LIKE CONCAT('%', search_term, '%')
                    GROUP BY b.book_id;
                END
            """)

def drop_search_procedure(apps, schema_editor):
    if connection.vendor == 'mysql':
        with connection.cursor() as cursor:
            cursor.execute("DROP PROCEDURE IF EXISTS search_bar")

class Migration(migrations.Migration):
    dependencies = [
        ('LibraryManagement', '0002_remove_latefee_borrow_id_remove_latefee_user_id_and_more'),
    ]

    operations = [
        migrations.RunPython(create_search_procedure, drop_search_procedure),
    ] 