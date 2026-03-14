# app.py
from datetime import datetime, timezone, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, flash
from database.db import init_db, get_student_by_email, add_student, log_activity

app = Flask(__name__)

# Secret key is required for sessions to work securely.
# In a real app this would be a long random string stored in an environment variable.
app.secret_key = 'lms_secret_key_2024'
# IST = UTC + 5 hours 30 minutes
IST = timezone(timedelta(hours=5, minutes=30))

def convert_to_ist(timestamp_str):
    """
    Converts a UTC timestamp string from SQLite to IST.
    Example: '2026-03-14 09:04:11' → '2026-03-14 14:34:11'
    """
    if not timestamp_str:
        return timestamp_str
    try:
        # Parse the UTC time from SQLite
        utc_time = datetime.strptime(str(timestamp_str), '%Y-%m-%d %H:%M:%S')
        # Attach UTC timezone info
        utc_time = utc_time.replace(tzinfo=timezone.utc)
        # Convert to IST
        ist_time = utc_time.astimezone(IST)
        # Return nicely formatted string
        return ist_time.strftime('%d %b %Y, %I:%M %p')
    except:
        return timestamp_str

# Register as a Jinja2 filter so templates can use it
app.jinja_env.filters['to_ist'] = convert_to_ist


# Initialize the database when the app starts.
# Creates tables if they don't exist yet.
with app.app_context():
    init_db()


# ─── HOME → redirect to login ────────────────────────────────────────────────
@app.route('/')
def home():
    return redirect(url_for('login'))


# ─── LOGIN ────────────────────────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    # If already logged in, go straight to dashboard
    if 'student_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email    = request.form['email']
        password = request.form['password']

        # Look up the student in the database
        student = get_student_by_email(email)

        # Check if student exists AND password matches
        if student and student['password'] == password:
            # Save student info in session — this is how Flask
            # remembers who is logged in across page loads
            session['student_id'] = student['student_id']
            session['student_name'] = student['name']

            # Log this activity to the database
            log_activity(student['student_id'], 'Logged in')

            return redirect(url_for('dashboard'))
        else:
            # flash() sends a one-time message to the next page
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('login.html')


# ─── REGISTER ─────────────────────────────────────────────────────────────────
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name     = request.form['name']
        email    = request.form['email']
        password = request.form['password']

        success = add_student(name, email, password)

        if success:
            flash('Account created! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Email already registered. Try logging in.', 'warning')

    return render_template('register.html')


# ─── DASHBOARD ────────────────────────────────────────────────────────────────
@app.route('/dashboard')
def dashboard():
    if 'student_id' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('login'))

    student_id = session['student_id']

    # Fetch real data from database
    from database.db import get_recommended_resources, get_recent_activity, get_student_progress
    recommended = get_recommended_resources(limit=3)
    activity    = get_recent_activity(student_id, limit=5)
    progress    = get_student_progress(student_id)

    return render_template('dashboard.html',
                           student_name=session['student_name'],
                           recommended=recommended,
                           activity=activity,
                           progress=progress)


# ─── LOGOUT ───────────────────────────────────────────────────────────────────
@app.route('/logout')
def logout():
    student_id = session.get('student_id')
    if student_id:
        log_activity(student_id, 'Logged out')
    session.clear()
    flash('You have been logged out.', 'info')
    return redirect(url_for('login'))

# ─── RESOURCE LIBRARY ─────────────────────────────────────────────────────────
@app.route('/library')
def library():
    if 'student_id' not in session:
        return redirect(url_for('login'))

    from database.db import get_all_resources
    from algorithms.sorting import merge_sort
    from algorithms.greedy import greedy_recommend

    # Get all resources from database
    all_resources = get_all_resources()

    # Convert to list of dicts for our algorithms
    # (SQLite rows need to be converted for our sorting algorithm)
    resources_list = [dict(r) for r in all_resources]

    # Apply search filter if provided
    search     = request.args.get('search', '')
    course     = request.args.get('course', '')
    difficulty = request.args.get('difficulty', '')

    if search:
        resources_list = [
            r for r in resources_list
            if search.lower() in r['title'].lower()
        ]
    if course:
        resources_list = [
            r for r in resources_list
            if r['course'] == course
        ]
    if difficulty:
        resources_list = [
            r for r in resources_list
            if r['difficulty'] == difficulty
        ]

    # ── DAA CONCEPT: Sort using our Merge Sort algorithm ──
    sorted_resources = merge_sort(resources_list, key='rating', reverse=True)

    return render_template('library.html',
                           resources=sorted_resources,
                           student_name=session['student_name'],
                           search=search,
                           course=course,
                           difficulty=difficulty)


# ─── DOWNLOAD RESOURCE ────────────────────────────────────────────────────────
@app.route('/download/<int:resource_id>')
def download_resource(resource_id):
    if 'student_id' not in session:
        return redirect(url_for('login'))

    from database.db import get_connection
    conn = get_connection()
    cursor = conn.cursor()

    # Increment download count
    cursor.execute('''
        UPDATE resources 
        SET downloads = downloads + 1 
        WHERE resource_id = ?
    ''', (resource_id,))
    conn.commit()

    # Get resource info
    cursor.execute(
        'SELECT * FROM resources WHERE resource_id = ?',
        (resource_id,)
    )
    resource = cursor.fetchone()
    conn.close()

    # Log this activity
    log_activity(session['student_id'], f"Downloaded: {resource['title']}")

    # For now, redirect back to library with a success message
    # In a real app, this would serve the actual file
    flash(f"✅ '{resource['title']}' download started!", 'success')
    return redirect(url_for('library'))
# ─── UPLOAD RESOURCE ──────────────────────────────────────────────────────────
import os
from werkzeug.utils import secure_filename

UPLOAD_FOLDER   = 'resources'
ALLOWED_EXTENSIONS = {'pdf', 'mp4', 'docx', 'pptx', 'txt'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
def upload():
    if 'student_id' not in session:
        return redirect(url_for('login'))

    if request.method == 'POST':
        title       = request.form['title']
        description = request.form.get('description', '')
        course      = request.form['course']
        difficulty  = request.form['difficulty']
        file        = request.files.get('file')

        file_path = None

        # ── OS CONCEPT: File Management ──
        if file and file.filename and allowed_file(file.filename):
            # secure_filename sanitizes the filename
            # (removes path separators, special chars)
            filename = secure_filename(file.filename)

            # Determine subfolder based on file type
            ext = filename.rsplit('.', 1)[1].lower()
            if ext == 'mp4':
                subfolder = os.path.join(UPLOAD_FOLDER, 'videos')
            else:
                subfolder = os.path.join(UPLOAD_FOLDER, 'pdfs')

            # Create directory if it doesn't exist (OS file management)
            os.makedirs(subfolder, exist_ok=True)

            # Save file to filesystem
            full_path = os.path.join(subfolder, filename)
            file.save(full_path)
            file_path = full_path

        # Save resource metadata to database
        from database.db import get_connection
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO resources
            (title, description, type, course, difficulty, file_path, rating, downloads)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, description,
              ext if file_path else 'other',
              course, difficulty, file_path, 0, 0))
        conn.commit()
        conn.close()

        # ── OS CONCEPT: Multithreading ──
        # Log activity in a background thread
        # Main thread doesn't wait for this
        from os_concepts.threading_ops import process_upload_thread
        process_upload_thread(session['student_id'], title)

        flash(f"✅ '{title}' uploaded successfully!", 'success')
        return redirect(url_for('library'))

    return render_template('upload.html',
                           student_name=session['student_name'])


# ─── PROGRESS PAGE ────────────────────────────────────────────────────────────
@app.route('/progress')
def progress():
    if 'student_id' not in session:
        return redirect(url_for('login'))

    from database.db import get_student_progress, get_recent_activity
    from algorithms.dp import optimal_learning_path

    student_id = session['student_id']
    progress_data = get_student_progress(student_id)
    activity      = get_recent_activity(student_id, limit=20)

    # Convert to list of dicts for DP algorithm
    progress_list = [dict(p) for p in progress_data]

    # ── DAA CONCEPT: Dynamic Programming ──
    learning_path = optimal_learning_path(progress_list)

    return render_template('progress.html',
                           student_name=session['student_name'],
                           progress=progress_data,
                           activity=activity,
                           learning_path=learning_path)
if __name__ == '__main__':
    app.run(debug=True)