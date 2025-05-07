DELIMITER $$
CREATE PROCEDURE search_bar(
	IN search_query VARCHAR(255)
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
		librarymanagement_genre g ON bg.genre_id_id = g.genre_id
	WHERE
		search_query IS NULL
		OR b.title LIKE CONCAT('%', search_query, '%')
		OR b.isbn LIKE CONCAT('%', search_query, '%')
		OR a.first_name LIKE CONCAT('%', search_query, '%')
		OR a.last_name LIKE CONCAT('%', search_query, '%')
		OR g.name LIKE CONCAT('%', search_query, '%')
	GROUP BY
		b.book_id, b.title, b.isbn
	ORDER BY
		b.title;
END $$
DELIMITER ;