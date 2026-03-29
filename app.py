# app.py
import bcrypt 
from datetime import datetime, timezone, timedelta
from flask import Flask, render_template, request, redirect, url_for, session, flash
from database.db import init_db, get_student_by_email, add_student, log_activity
import os
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

app.secret_key = 'lms_secret_key_2024'

IST = timezone(timedelta(hours=5, minutes=30))

def convert_to_ist(timestamp_str):
    if not timestamp_str:
        return timestamp_str
    try:
        utc_time = datetime.strptime(str(timestamp_str), '%Y-%m-%d %H:%M:%S')
        utc_time = utc_time.replace(tzinfo=timezone.utc)
        ist_time = utc_time.astimezone(IST)
        return ist_time.strftime('%d %b %Y, %I:%M %p')
    except:
        return timestamp_str

app.jinja_env.filters['to_ist'] = convert_to_ist

with app.app_context():
    init_db()


# ─── HOME ─────────────────────────────────────────────────────────────────────
@app.route('/')
def home():
    return redirect(url_for('login'))


# ─── LOGIN ────────────────────────────────────────────────────────────────────
@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'student_id' in session:
        return redirect(url_for('dashboard'))

    if request.method == 'POST':
        email    = request.form['email']
        password = request.form['password']
        student  = get_student_by_email(email)

        if student and bcrypt.checkpw(password.encode('utf-8'), student['password']):
            session['student_id']   = student['student_id']
            session['student_name'] = student['name']
            log_activity(student['student_id'], 'Logged in')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid email or password. Please try again.', 'danger')

    return render_template('login.html')


# ─── REGISTER ─────────────────────────────────────────────────────────────────
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name     = request.form['name']
        email    = request.form['email']
        password = request.form['password']
        success  = add_student(name, email, password)

        if success:
            flash('Account created! Please log in.', 'success')
            return redirect(url_for('login'))
        else:
            flash('Email already registered. Try logging in.', 'warning')

    return render_template('register.html')


# ─── DASHBOARD ────────────────────────────────────────────────────────────────
@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'student_id' not in session:
        flash('Please log in first.', 'warning')
        return redirect(url_for('login'))

    student_id = session['student_id']

    from database.db import get_recent_activity, get_student_progress
    activity = get_recent_activity(student_id, limit=5)
    progress = get_student_progress(student_id)

    # AI Search from dashboard search bar
    search_results = []
    search_query   = ''
    search_error   = None

    if request.method == 'POST':
        search_query = request.form.get('search', '').strip()
        if search_query:
            try:
                from algorithms.ai_search import search_and_rate
                search_results = search_and_rate(search_query, min_rating=4.0)

                if search_results is None:
                    search_error = "⚠️ Please search for educational topics only — e.g. algorithms, programming, mathematics, science."
                    search_results = []
                else:
                    log_activity(student_id, f"Searched: {search_query}")
                    if not search_results:
                        search_error = "No resources found. Try a different search term."
            except Exception as e:
                search_error  = f"Search error: {str(e)}"
                print(f"AI Search error: {e}")

    return render_template('dashboard.html',
                           student_name=session['student_name'],
                           activity=activity,
                           progress=progress,
                           search_results=search_results,
                           search_query=search_query,
                           search_error=search_error)


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

    all_resources  = get_all_resources()
    resources_list = [dict(r) for r in all_resources]

    # Check if we are showing similar resources
    show_similar  = request.args.get('show_similar', '')
    similar_title = ''

    if show_similar and 'similar_ids' in session:
        similar_ids   = session.pop('similar_ids')
        similar_title = session.pop('similar_title', '')
        session.pop('similar_course', '')

        resources_list = [
            r for r in resources_list
            if r['resource_id'] in similar_ids
        ]
        resources_list = merge_sort(resources_list, key='rating', reverse=True)

    else:
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

        resources_list = merge_sort(resources_list, key='rating', reverse=True)

    return render_template('library.html',
                           resources=resources_list,
                           student_name=session['student_name'],
                           search=request.args.get('search', ''),
                           course=request.args.get('course', ''),
                           difficulty=request.args.get('difficulty', ''),
                           similar_title=similar_title)


# ─── DOWNLOAD RESOURCE ────────────────────────────────────────────────────────
@app.route('/download/<int:resource_id>')
def download_resource(resource_id):
    if 'student_id' not in session:
        return redirect(url_for('login'))

    from flask import send_file, jsonify
    import os
    from database.db import get_connection

    conn   = get_connection()
    cursor = conn.cursor()

    cursor.execute(
        'SELECT * FROM resources WHERE resource_id = ?',
        (resource_id,)
    )
    resource = cursor.fetchone()

    if not resource:
        conn.close()
        return jsonify({'error': 'Resource not found'}), 404

    file_path = resource['file_path']

    if file_path and os.path.exists(file_path):
        # Only increment count if real file exists
        cursor.execute('''
            UPDATE resources
            SET downloads = downloads + 1
            WHERE resource_id = ?
        ''', (resource_id,))
        conn.commit()
        conn.close()

        log_activity(session['student_id'], f"Downloaded: {resource['title']}")
        # ── NEW: update progress for this course ──
        from database.db import update_progress
        update_progress(session['student_id'], resource['course'], increment=10)  
        return send_file(
            os.path.abspath(file_path),
            as_attachment=True,
            download_name=os.path.basename(file_path)
        )
    else:
        # No file — don't increment, just notify
        conn.close()
        return jsonify({'no_file': True, 'title': resource['title']}), 200


# ─── UPLOAD RESOURCE ──────────────────────────────────────────────────────────
UPLOAD_FOLDER      = 'resources'
ALLOWED_EXTENSIONS = {'pdf', 'mp4', 'docx', 'pptx', 'txt'}
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024

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
        file_path   = None
        ext         = 'other'

        if file and file.filename and allowed_file(file.filename):
            filename  = secure_filename(file.filename)
            ext       = filename.rsplit('.', 1)[1].lower()
            subfolder = os.path.join(UPLOAD_FOLDER, 'videos' if ext == 'mp4' else 'pdfs')
            os.makedirs(subfolder, exist_ok=True)
            full_path = os.path.join(subfolder, filename)
            file.save(full_path)
            file_path = full_path

        from database.db import get_connection
        conn   = get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO resources
            (title, description, type, course, difficulty, file_path, rating, downloads)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (title, description, ext, course, difficulty, file_path, 0, 0))
        conn.commit()
        conn.close()

        from os_concepts.scheduling import round_robin_scheduling
        from os_concepts.threading_ops import process_upload_thread

        background_tasks = [
            {'id': 'T1', 'name': 'Log Upload Activity',     'burst_time': 2, 'arrival_time': 0},
            {'id': 'T2', 'name': 'Refresh Recommendations', 'burst_time': 3, 'arrival_time': 0},
            {'id': 'T3', 'name': 'Update Progress Stats',   'burst_time': 2, 'arrival_time': 1},
        ]
        scheduled = round_robin_scheduling(background_tasks, quantum=2)
        process_upload_thread(session['student_id'], title)
         # ── NEW: update progress for the uploaded course ──
        from database.db import update_progress
        update_progress(session['student_id'], course, increment=15)
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

    student_id    = session['student_id']
    progress_data = get_student_progress(student_id)
    activity      = get_recent_activity(student_id, limit=20)
    progress_list = [dict(p) for p in progress_data]
    learning_path = optimal_learning_path(progress_list)

    return render_template('progress.html',
                           student_name=session['student_name'],
                           progress=progress_data,
                           activity=activity,
                           learning_path=learning_path)


# ─── SIMILAR RESOURCES ────────────────────────────────────────────────────────
@app.route('/similar/<int:resource_id>')
def similar_resources(resource_id):
    if 'student_id' not in session:
        return redirect(url_for('login'))

    from database.db import get_all_resources, get_connection
    from algorithms.similarity import find_similar_resources

    conn   = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        'SELECT * FROM resources WHERE resource_id = ?',
        (resource_id,)
    )
    target = dict(cursor.fetchone())
    conn.close()

    all_resources = [dict(r) for r in get_all_resources()]
    similar       = find_similar_resources(target, all_resources, top_n=4)

    log_activity(session['student_id'],
                 f"Viewed similar resources for: {target['title']}")

    session['similar_ids']    = [r['resource_id'] for r in similar]
    session['similar_course'] = target['course']
    session['similar_title']  = target['title']

    return redirect(url_for('library', show_similar=1))


# ─── COURSES ──────────────────────────────────────────────────────────────────
@app.route('/courses')
def courses():
    if 'student_id' not in session:
        return redirect(url_for('login'))

    from database.db import get_courses, get_resources_by_course, get_student_progress

    all_courses      = get_courses()
    student_id       = session['student_id']
    progress_data    = get_student_progress(student_id)
    progress_map     = {
        p['course']: p['completion_percentage']
        for p in progress_data
    }
    selected_course  = request.args.get('course', '')
    course_resources = []

    if selected_course:
        course_resources = get_resources_by_course(selected_course)

    return render_template('courses.html',
                           student_name=session['student_name'],
                           courses=all_courses,
                           progress_map=progress_map,
                           selected_course=selected_course,
                           course_resources=course_resources)

# ─── AI RESOURCE SEARCH ───────────────────────────────────────────────────────
@app.route('/ai-search', methods=['GET', 'POST'])
def ai_search():
    if 'student_id' not in session:
        return redirect(url_for('login'))

    results = []
    query   = ''
    error   = None

    if request.method == 'POST':
        query = request.form.get('query', '').strip()

        if query:
            try:
                from algorithms.ai_search import search_and_rate
                results = search_and_rate(query, min_rating=4.0)
                log_activity(session['student_id'],
                             f"AI searched: {query}")

                if not results:
                    error = "No high quality resources found. Try a different search term."

            except Exception as e:
                error = f"Search error: {str(e)}"
                print(f"AI Search error: {e}")

    return render_template('ai_search.html',
                           student_name=session['student_name'],
                           results=results,
                           query=query,
                           error=error)
if __name__ == '__main__':
    app.run(debug=True)