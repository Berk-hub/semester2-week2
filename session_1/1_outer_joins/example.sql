-- Enable readable output format
.mode columns
.headers on

-- Instructions for students:
-- 1. Open SQLite in terminal: sqlite3 university.db
-- 2. Load this script: .read example.sql
-- 3. Exit SQLite: .exit



-- write your sql code here
-- Example of an outer join to find all students and their enrolled courses,
-- including students who are not enrolled in any courses.  
SELECT students.student_id, students.name AS student_name, courses.course_name
FROM students
LEFT JOIN enrollments ON students.student_id = enrollments.student_id
LEFT JOIN courses ON enrollments.course_id = courses.course_id;



