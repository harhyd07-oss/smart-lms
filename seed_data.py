# seed_data.py
# This script fills the database with sample data so the dashboard
# has something to display. Run it ONCE then delete or ignore it.
# This is called "seeding" the database — common in real projects.

from database.db import get_connection

def seed():
    conn = get_connection()
    cursor = conn.cursor()

    # --- Sample Resources ---
    resources = [
        ('Merge Sort Complete Guide', 'Deep dive into merge sort algorithm', 'pdf', 'DAA', 'Medium', 'resources/pdfs/merge_sort.pdf', 4.5, 120),
        ('Quick Sort Explained', 'Quick sort with visual examples', 'pdf', 'DAA', 'Medium', 'resources/pdfs/quick_sort.pdf', 4.2, 98),
        ('OS Process Scheduling', 'FCFS and Round Robin explained', 'pdf', 'Operating Systems', 'Easy', 'resources/pdfs/os_scheduling.pdf', 4.7, 200),
        ('SQL Joins Video Tutorial', 'Inner, outer, left joins visualized', 'video', 'DBMS', 'Easy', 'resources/videos/sql_joins.mp4', 4.8, 310),
        ('Dynamic Programming Intro', 'DP concepts with practice problems', 'pdf', 'DAA', 'Hard', 'resources/pdfs/dp_intro.pdf', 4.3, 87),
        ('Database Normalization', 'First, second, third normal forms', 'pdf', 'DBMS', 'Medium', 'resources/pdfs/normalization.pdf', 4.1, 75),
        ('Greedy Algorithms', 'Greedy approach with real examples', 'pdf', 'DAA', 'Medium', 'resources/pdfs/greedy.pdf', 4.4, 95),
        ('Memory Management in OS', 'Paging, segmentation explained', 'video', 'Operating Systems', 'Hard', 'resources/videos/memory.mp4', 4.6, 150),
    ]

    cursor.executemany('''
        INSERT OR IGNORE INTO resources 
        (title, description, type, course, difficulty, file_path, rating, downloads)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', resources)

    # --- Sample Progress for student_id = 1 ---
    progress = [
        (1, 'DAA', 55),
        (1, 'Operating Systems', 40),
        (1, 'DBMS', 70),
    ]

    cursor.executemany('''
        INSERT OR IGNORE INTO progress 
        (student_id, course, completion_percentage)
        VALUES (?, ?, ?)
    ''', progress)

    conn.commit()
    conn.close()
    print("✅ Sample data added successfully!")

if __name__ == '__main__':
    seed()