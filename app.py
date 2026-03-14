# app.py

from flask import Flask, render_template, request, redirect, url_for, session, flash
from database.db import init_db, get_student_by_email, add_student, log_activity

app = Flask(__name__)

# Secret key is required for sessions to work securely.
# In a real app this would be a long random string stored in an environment variable.
app.secret_key = 'lms_secret_key_2024'


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


if __name__ == '__main__':
    app.run(debug=True)