# database/db.py
# This file handles ALL database operations.
# Think of it as the "librarian" — it knows where everything is stored
# and how to retrieve or save it.

import sqlite3
import os

# This finds the path to our database file automatically,
# no matter where the project is on your computer.
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, '..', 'lms.db')


def get_connection():
    """
    Creates and returns a database connection.
    We use this function everywhere instead of hardcoding the path.
    row_factory lets us access columns by name e.g. row['email']
    instead of by index e.g. row[1]
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """
    Creates all 4 tables if they don't already exist.
    'IF NOT EXISTS' means running this twice won't break anything.
    This is called once when the app starts.
    """
    conn = get_connection()
    cursor = conn.cursor()

    # --- TABLE 1: students ---
    # Stores login credentials and basic info.
    # INTEGER PRIMARY KEY AUTOINCREMENT = SQLite auto-assigns IDs (1, 2, 3...)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS students (
            student_id   INTEGER PRIMARY KEY AUTOINCREMENT,
            name         TEXT NOT NULL,
            email        TEXT UNIQUE NOT NULL,
            password     TEXT NOT NULL,
            created_at   TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # --- TABLE 2: resources ---
    # Stores metadata about uploaded files.
    # The actual file lives in /resources folder — we only store the PATH here.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS resources (
            resource_id  INTEGER PRIMARY KEY AUTOINCREMENT,
            title        TEXT NOT NULL,
            description  TEXT,
            type         TEXT NOT NULL,
            course       TEXT NOT NULL,
            difficulty   TEXT NOT NULL,
            file_path    TEXT,
            rating       REAL DEFAULT 0,
            downloads    INTEGER DEFAULT 0,
            uploaded_at  TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # --- TABLE 3: activity_logs ---
    # Records every action a student takes — upload, download, login etc.
    # FOREIGN KEY links each log to a student in the students table.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activity_logs (
            log_id      INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id  INTEGER NOT NULL,
            action      TEXT NOT NULL,
            timestamp   TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
    ''')

    # --- TABLE 4: progress ---
    # Tracks how far each student has gotten in each course.
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS progress (
            progress_id           INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id            INTEGER NOT NULL,
            course                TEXT NOT NULL,
            completion_percentage REAL DEFAULT 0,
            last_updated          TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (student_id) REFERENCES students(student_id)
        )
    ''')

    # Save all changes and close connection
    conn.commit()
    conn.close()
    print("✅ Database initialized successfully!")


def add_student(name, email, password):
    """
    Inserts a new student into the database.
    Returns True if successful, False if email already exists.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            'INSERT INTO students (name, email, password) VALUES (?, ?, ?)',
            (name, email, password)
        )
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        # This fires when email already exists (UNIQUE constraint)
        return False
    finally:
        conn.close()


def get_student_by_email(email):
    """
    Looks up a student by email address.
    Returns the student row if found, None if not found.
    Used during login to verify credentials.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM students WHERE email = ?', (email,)
    )
    student = cursor.fetchone()
    conn.close()
    return student


def log_activity(student_id, action):
    """
    Records what a student did and when.
    Called every time a student does something meaningful.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'INSERT INTO activity_logs (student_id, action) VALUES (?, ?)',
        (student_id, action)
    )
    conn.commit()
    conn.close()


def get_recent_activity(student_id, limit=5):
    """
    Gets the last N actions for a student.
    Used on the dashboard to show recent activity.
    ORDER BY timestamp DESC = newest first.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT action, timestamp
        FROM activity_logs
        WHERE student_id = ?
        ORDER BY timestamp DESC
        LIMIT ?
    ''', (student_id, limit))
    logs = cursor.fetchall()
    conn.close()
    return logs


def get_student_progress(student_id):
    """
    Gets all course progress for a student.
    Used on the progress page and dashboard.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT course, completion_percentage
        FROM progress
        WHERE student_id = ?
        ORDER BY course
    ''', (student_id,))
    progress = cursor.fetchall()
    conn.close()
    return progress
def get_recommended_resources(limit=6):
    """
    Returns top resources sorted by rating.
    This connects to our sorting algorithm in Day 2.
    For now we use SQL ORDER BY — later we'll replace with Merge Sort.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT resource_id, title, description, type, course, difficulty, rating, downloads
        FROM resources
        ORDER BY rating DESC
        LIMIT ?
    ''', (limit,))
    resources = cursor.fetchall()
    conn.close()
    return resources


def get_all_resources():
    """
    Returns all resources from the database.
    Used in the resource library page.
    """
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT resource_id, title, description, type, 
               course, difficulty, rating, downloads
        FROM resources
        ORDER BY rating DESC
    ''')
    resources = cursor.fetchall()
    conn.close()
    return resources
def get_courses():
    """
    Returns all unique courses with their resource count
    and average rating.
    """
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT 
            course,
            COUNT(*)       AS resource_count,
            AVG(rating)    AS avg_rating,
            SUM(downloads) AS total_downloads
        FROM resources
        GROUP BY course
        ORDER BY course
    ''')
    courses = cursor.fetchall()
    conn.close()
    return courses


def get_resources_by_course(course):
    """
    Returns all resources for a specific course.
    """
    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        SELECT resource_id, title, description, type,
               course, difficulty, rating, downloads
        FROM resources
        WHERE course = ?
        ORDER BY rating DESC
    ''', (course,))
    resources = cursor.fetchall()
    conn.close()
    return resources