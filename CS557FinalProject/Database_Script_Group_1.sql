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
		librarymanagement_bookauthor ba ON b.book_id = ba.book_id
	LEFT JOIN
		librarymanagement_author a ON ba.author_id = a.author_id
	LEFT JOIN
		librarymanagement_bookgenre bg ON b.book_id = bg.book_id
	LEFT JOIN
		librarymanagement_genre g ON bg.genre_id = g.genre_id
	WHERE
		(search_title IS NULL OR search_title = '' OR b.title LIKE CONCAT('%', search_title, '%'))
		AND (search_isbn IS NULL OR search_isbn = '' OR b.isbn LIKE CONCAT('%', search_isbn, '%'))
		AND (
			search_author IS NULL OR search_author = '' OR EXISTS (
				SELECT 1
				FROM librarymanagement_bookauthor ba2
				JOIN librarymanagement_author a2 ON ba2.author_id = a2.author_id
				WHERE ba2.book_id = b.book_id
				AND (
					a2.first_name LIKE CONCAT('%', search_author, '%')
					OR a2.last_name LIKE CONCAT('%', search_author, '%')
				)
			)
		)
		AND (
			search_genre IS NULL OR search_genre = '' OR EXISTS (
				SELECT 1
				FROM librarymanagement_bookgenre bg2
				JOIN librarymanagement_genre g2 ON bg2.genre_id = g2.genre_id
				WHERE bg2.book_id = b.book_id
				AND g2.name LIKE CONCAT('%', search_genre, '%')
			)
		)
	GROUP BY
		b.book_id, b.title, b.isbn
	ORDER BY
		b.title;
END $$

DELIMITER ;