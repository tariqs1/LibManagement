DELIMITER $$
CREATE PROCEDURE search_bar(
	IN search_title VARCHAR(255),
    IN search_isbn VARCHAR(20),
    IN search_author VARCHAR(255),
    IN search_genre VARCHAR(100)
)
BEGIN
	SELECT
		b.book_id,
        b.title,
        b.isbn,
        GROUP_CONCAT(DISTINCT CONCAT(a.first_name, ' ', a.last_name)) AS authors,
        GROUP_CONCAT(DISTINCT g.name) AS genres,
        b.available_copies > 0 AS is_available
	FROM
		librarymanagement_book b
	LEFT JOIN 
		librarymanagement_bookauthor ba ON b.book_id = ba.book_id_id
	LEFT JOIN
		librarymanagement_author a ON ba.author_id_id = a.author_id
	LEFT JOIN
		librarymanagement_bookgenre bg ON b.book_id = bg.book_id_id
	LEFT JOIN
		librarymanagement_genre g ON bg.genre_id_id = g.genre_id
	WHERE
		(search_title IS NULL OR b.title LIKE CONCAT('%', search_title, '%'))
	AND
		(search_isbn IS NULL OR b.isbn LIKE CONCAT('%', search_isbn, '%'))
	AND
		(search_author IS NULL OR a.first_name LIKE CONCAT('%', search_author, '%')
        OR a.last_name LIKE CONCAT('%', search_author,'%'))
	AND
		(search_genre IS NULL OR g.name LIKE CONCAT('%', search_genre, '%'))
	GROUP BY
		b.book_id, b.title, b.isbn
	ORDER BY
		b.title;
END $$
DELIMITER ;