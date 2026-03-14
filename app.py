# app.py
# This is the main file that starts your Flask web server.
# Think of it as the "on switch" for your entire application.

from flask import Flask, render_template

# Flask needs to know where your project lives.
# __name__ tells it "look in the same folder as this file."
app = Flask(__name__)

# A "route" is a URL pattern.
# When someone visits http://localhost:5000/ , this function runs.
@app.route('/')
def home():
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

# This block only runs when you execute app.py directly.
# debug=True means Flask will auto-reload when you save changes.
if __name__ == '__main__':
    app.run(debug=True)