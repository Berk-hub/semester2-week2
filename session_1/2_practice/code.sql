-- Enable readable output format
.mode columns
.headers on

-- Instructions for students:
-- 1. Open SQLite in terminal: sqlite3 library.db
-- 2. Load this script: .read code.sql
-- 3. Exit SQLite: .exit


-- write your sql code here
SELECT
  b.title      AS book_title,
  m.name       AS member_name,
  l.loan_date  AS loan_date
FROM loans l
JOIN books b   ON b.id = l.book_id
JOIN members m ON m.id = l.member_id
ORDER BY l.loan_date DESC;

SELECT
  b.title     AS book_title,
  l.id        AS loan_id,
  l.loan_date AS loan_date,
  l.return_date
FROM books b
LEFT JOIN loans l ON l.book_id = b.id
ORDER BY b.title, l.loan_date;

SELECT
  br.name  AS branch_name,
  b.title  AS book_title
FROM branches br
LEFT JOIN books b ON b.branch_id = br.id
ORDER BY br.name, b.title;

SELECT
  br.name AS branch_name,
  COUNT(b.id) AS book_count
FROM branches br
LEFT JOIN books b ON b.branch_id = br.id
GROUP BY br.id, br.name
ORDER BY book_count DESC, br.name;

SELECT
  br.name AS branch_name,
  COUNT(b.id) AS book_count
FROM branches br
LEFT JOIN books b ON b.branch_id = br.id
GROUP BY br.id, br.name
HAVING COUNT(b.id) > 7
ORDER BY book_count DESC;

SELECT
  m.name AS member_name,
  COUNT(l.id) AS loan_count
FROM members m
LEFT JOIN loans l ON l.member_id = m.id
GROUP BY m.id, m.name
ORDER BY loan_count DESC, m.name;

SELECT
  m.name AS member_name
FROM members m
LEFT JOIN loans l ON l.member_id = m.id
WHERE l.id IS NULL
ORDER BY m.name;

SELECT
  br.name AS branch_name,
  COUNT(l.id) AS total_loans
FROM branches br
LEFT JOIN books b  ON b.branch_id = br.id
LEFT JOIN loans l  ON l.book_id = b.id
GROUP BY br.id, br.name
ORDER BY total_loans DESC, br.name;

SELECT DISTINCT
  m.name AS member_name
FROM members m
JOIN loans l ON l.member_id = m.id
WHERE l.return_date IS NULL
ORDER BY m.name;

SELECT
  b.title AS book_title,
  l.id    AS loan_id,
  l.loan_date,
  l.return_date,
  CASE
    WHEN l.id IS NULL THEN 'Unloaned book'
    ELSE 'Loaned book'
  END AS status
FROM books b
LEFT JOIN loans l ON l.book_id = b.id
ORDER BY status DESC, b.title, l.loan_date