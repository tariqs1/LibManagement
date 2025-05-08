DROP PROCEDURE IF EXISTS search_bar;
DELIMITER //

CREATE PROCEDURE search_bar(
    IN p_title VARCHAR(255),
    IN p_isbn VARCHAR(255),
    IN p_author VARCHAR(255),
    IN p_genre VARCHAR(255)
)
BEGIN
    SELECT
        b.book_id,
        b.title,
        b.isbn,
        GROUP_CONCAT(DISTINCT CONCAT(a.first_name, ' ', a.last_name)) AS authors,
        GROUP_CONCAT(DISTINCT g.name) AS genres,
        b.available_copies,
        b.total_copies,
        b.cover_image_url
    FROM
        librarymanagement_book b
        LEFT JOIN librarymanagement_bookauthor ba ON b.book_id = ba.book_id
        LEFT JOIN librarymanagement_author a ON ba.author_id = a.author_id
        LEFT JOIN librarymanagement_bookgenre bg ON b.book_id = bg.book_id
        LEFT JOIN librarymanagement_genre g ON bg.genre_id = g.genre_id
    WHERE
        (p_title IS NULL OR p_title = '' OR b.title LIKE CONCAT('%', p_title, '%'))
        AND (p_isbn IS NULL OR p_isbn = '' OR b.isbn LIKE CONCAT('%', p_isbn, '%'))
        AND (p_author IS NULL OR p_author = '' OR CONCAT(a.first_name, ' ', a.last_name) LIKE CONCAT('%', p_author, '%'))
        AND (p_genre IS NULL OR p_genre = '' OR g.name LIKE CONCAT('%', p_genre, '%'))
    GROUP BY
        b.book_id, b.title, b.isbn, b.available_copies, b.total_copies, b.cover_image_url;
END //

DELIMITER ;